#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def pushUpdatedFiles(self, details, location_github_branch_push, source_files):

    # Update all of the files in the downstream repos with the changes this build has created

    import base64  # For encoding & decoding API commits
    import json  # for sending data with and parsing data from requests
    import os  # for running OS commands like changing directories or listing files in directory
    import requests  # for running curl-like API requests
    import subprocess
    import time
    from repos.locationCommitSummary import locationCommitSummary

    from errorHandling.errorHandling import addToWarnings
    from errorHandling.errorHandling import addToErrors
    from errorHandling.pushErrors import pushErrors
    from setup.exitBuild import exitBuild

    pushSuccessful = False

    # Check in the changed files to staging/prod!
    # self.log.info('\n\n')
    # self.log.info('----------------------------------')
    self.log.info('\n')
    self.log.info('Pushing changes for ' + self.location_name + ':')
    # self.log.info('----------------------------------')

    os.chdir(self.location_dir)

    # Check and see if there are any changes to the files for the self.location_name.
    # It could be that changes are made to staging content and not prod.

    try:
        status_bytes = subprocess.check_output('git status --short', shell=True)
        status = status_bytes.decode("utf-8")
    except Exception as statusException:
        self.log.info('WARNING: git status command could not be completed.')
        self.log.info(statusException)
        status = 'None'

    if ('nothing to commit' in status.lower()) or (status == '\n') or (status == ''):
        self.log.info('Nothing to commit to ' + self.location_name + '.')
    else:
        try:
            subprocess.call('git add --all', shell=True)
            self.log.info('Adding all files to be committed.')
        except Exception as gitException:
            self.log.info('WARNING: Failed to add, commit, and push all files at the same time. Resulted in:')
            self.log.info(gitException)
            self.log.info('Trying to add individual files via the API instead.')
            for source_file, source_file_info in source_files.items():
                folderAndFile = source_files[source_file]['folderAndFile']
                file_name = source_files[source_file]['file_name']
                folderPath = source_files[source_file]['folderPath']
                if folderAndFile.endswith(tuple(details["filetypes"])):
                    if os.path.isfile(self.location_dir + folderPath + file_name):
                        self.log.info(folderPath + file_name + ':')

                    # Check in the files that couldn't be added with --all by using the API
                        # The Git API requires base 64 encoding, so the topic contents have to be converted before the API request can be made
                        fileName_open = open(self.location_dir + folderPath + file_name, 'r', encoding="utf8", errors="ignore")
                        fileContents = fileName_open.read()
                        fileContentsEncoded = base64.b64encode(fileContents.encode())
                        fileName_open.close()
                        try:
                            # Get the commit ID from the previous commit of this file
                            t = requests.get(self.location_github_api_prefix + "/contents/" + folderAndFile + '?ref=' +
                                             location_github_branch_push, auth=(details["username"], details["token"]))
                            tJSON = t.json()
                            lastsha = tJSON['sha']
                        except Exception:
                            # The file didn't exist in the repo before. So create the file rather than update it.
                            try:
                                self.log.info('File does not exist in ' + self.location_name + ' yet.')
                                r = requests.put(self.location_github_api_prefix + "/contents/" + folderAndFile,
                                                 auth=(details["username"], details["token"]),
                                                 data=json.dumps({"message": self.currentCommitSummary,
                                                                  "content": fileContentsEncoded.decode("utf-8"),
                                                                  "branch": location_github_branch_push}))
                            except Exception:
                                self.log.info('ERROR. Could not add ' + folderAndFile + ' to ' + self.location_name +
                                              ' via the API. 1 - File does not exist in the repo or authentication ' +
                                              'error (bad API request).')
                                self.log.info(r.status_code)
                        else:
                            # Update the base 64 encoded version of the contents into staging/prod
                            try:
                                fileName_open = open(self.location_dir + folderPath + file_name, 'r', encoding="utf8", errors="ignore")
                                topicContents = fileName_open.read()
                                fileName_open.close()
                                oldContent = tJSON['content']
                                if not oldContent == topicContents:
                                    r = requests.put(self.location_github_api_prefix + "/contents/" + folderAndFile,
                                                     auth=(details["username"], details["token"]),
                                                     data=json.dumps({"message": self.currentCommitSummary, "content":
                                                                      fileContentsEncoded.decode("utf-8"), "sha": lastsha,
                                                                      "branch": location_github_branch_push}))
                                    stringStatusCode = str(r.status_code)
                                else:
                                    self.log.info('No changes detected. Not committing this file to ' + self.location_name + '.')
                                    stringStatusCode = 'Not committed'
                            except Exception:
                                self.log.info('ERROR. Could not add ' + folderAndFile + ' to ' + self.location_name +
                                              ' via the API. 2 - File existed before, ' +
                                              'but a new version could not be written (bad API request).')
                        stringStatusCode = str(r.status_code)
                        if stringStatusCode.startswith('2'):
                            self.log.info('Success! Added ' + folderAndFile + ' to ' + self.location_name + ' via the API.')
                            pushSuccessful = True
                        elif 'Not committed' in stringStatusCode:
                            self.log.info('No changes detected. Not committing this file to ' + self.location_name + '.')
                        else:
                            self.log.info('WARNING. Could not add ' + folderAndFile + ' to ' + self.location_name + ' via the API.')
                            self.log.info(stringStatusCode)
                else:
                    addToWarnings('Could not add ' + folderAndFile + ' to ' + self.location_name + ' via the API.',
                                  folderAndFile, folderPath + file_name, details, self.log, self.location_name, '', '')

        # CLI commands - status check, merge, push.
        else:
            LOCATION_COMMIT_SUMMARY = locationCommitSummary(self, details)
            status_bytes = subprocess.check_output('git status --short', shell=True)
            status = status_bytes.decode("utf-8")
            self.log.info('Status:')
            self.log.info(status)
            if ('nothing to commit' in status.lower()) or (status == '\n') or (status == ''):
                self.log.info('Nothing to commit to ' + self.location_name + '.')
            else:
                # When these two lines are not set, then the user displays as Travis CI User
                os.system("git config --global user.name \"" + details["username"] + "\"")
                try:
                    subprocess.call('git commit -m "' + LOCATION_COMMIT_SUMMARY + '" --quiet', shell=True)
                    self.log.info('Committing the changes.')
                except Exception:
                    self.log.info('Nothing to commit.')
                else:
                    try:
                        subprocess.call('git merge --quiet', shell=True)
                        self.log.info('Merging the commit.')
                    except Exception:
                        subprocess.call('git merge ' + location_github_branch_push + ' --quiet', shell=True)
                        self.log.info('Merging the commit with branch: ' + location_github_branch_push + '.')
                    try:
                        self.log.info('Pushing changed files to the ' + location_github_branch_push + ' branch.')
                        subprocess.call('git push --quiet', shell=True)
                    except Exception:
                        try:
                            self.log.info('Setting upstream origin ' + location_github_branch_push + '.')
                            subprocess.call('git push --set-upstream origin ' + location_github_branch_push + ' --quiet', shell=True)
                        except Exception as e:
                            pushErrors(details, e, self.log)
                        else:
                            pushSuccessful = True
                    else:
                        try:
                            subprocess.call('git push origin ' + location_github_branch_push + '  --quiet', shell=True)
                        except Exception as e:
                            self.log.error(e)
                            addToErrors('The changes could not be pushed to the repo.', 'push', '', details, self.log, 'post-build', '', '')
                        else:
                            try:
                                resultPush = str(subprocess.call('git push origin ' + location_github_branch_push + '  --quiet', shell=True))
                            except Exception:
                                self.log.info('Push failed. Waiting 5 seconds and trying again.')
                                time.sleep(5)
                                try:
                                    resultPush = str(subprocess.call('git push origin ' +
                                                     location_github_branch_push +
                                                     ' --quiet', shell=True, stdout=open(os.devnull, 'wb')))
                                except Exception:
                                    self.log.info('Push failed.')
                                else:
                                    self.log.debug(resultPush)
                                    pushSuccessful = True
                            else:
                                self.log.debug(resultPush)
                                pushSuccessful = True

        # Was something commited to Next Prod Push? If a PR doesn't already exist that's created by the user, create the PR for prod

        if pushSuccessful is True:
            if (self.location_output_action == 'create-pr') and (not location_github_branch_push == self.location_github_branch):
                # List PRs
                listPRs = requests.get(self.location_github_api_repos + '/pulls?head=' + self.location_github_branch,
                                       auth=(details["username"], details["token"]))
                PRs = listPRs.json()
                PRstring = str(PRs)
                if not PRstring == '[]':
                    self.log.debug('Existing PRs:')
                    for PR in PRs:
                        PRNumber = PR['number']
                        PRTitle = PR['title']
                        self.log.debug(str(PRNumber) + ': ' + PRTitle)
                if self.location_github_branch_pr not in PRstring:
                    g = {"title": "Next " + self.location_github_branch + " push", "body":
                         "See the Commits and Files changed tabs for more information about what is " +
                         "included in this pull request.",
                         "head": location_github_branch_push, "base": self.location_github_branch}
                    r = requests.post(self.location_github_api_repos + '/pulls?head=' + self.location_github_branch,
                                      auth=(details["username"], details["token"]), data=json.dumps(g))
                    self.log.info('Creating pull request for commit ' + details["current_commit_id"])
                    if r.status_code == 201:
                        self.log.info('SUCCESS!')
                    else:
                        if r.status_code == 401:
                            addToErrors('Authentication error. Maybe the token expired or the username must be updated.',
                                        'pr', '', details, self.log, 'post-build', '', '')
                        elif r.status_code == 422:
                            addToErrors('The pull request could not be created for one of three potential reasons. ' +
                                        '1. There might be a pull request already created for the ' +
                                        location_github_branch_push + ' branch. Close the pull request. ' +
                                        '2. The next-prod-push branch history might not match the publish branch history. ' +
                                        'Delete the next-prod-push branch and let the build re-create it. ' +
                                        '3. The response from the API call might be empty. ' +
                                        'If Github is accessible, try starting another build.',
                                        'pr', '', details, self.log, 'post-build', '', '')
                        elif r.status_code == 500:
                            addToErrors('The pull request could not be created. The repo or the ' +
                                        details["source_github_domain"] + ' domain might not be accessible.' +
                                        str(r.status_code), 'pr', '', details, self.log, 'post-build', '', '')
                        else:
                            addToErrors('The pull request could not be created. ' + str(r.status_code), 'pr', '', details, self.log, 'post-build', '', '')
                        exitBuild(details, self.log)
                else:
                    for PR in PRs:
                        PRHead = PR['head']['ref']
                        if PRHead == location_github_branch_push:
                            PRNumber = PR['number']
                            PRTitle = PR['title']
                            PRBase = PR['base']['ref']
                            self.log.info('Updating pull request #' + str(PRNumber) + ': ' + PRTitle + ', head: ' + PRHead + ', base: ' + PRBase + '.')
            self.log.info('File update complete.')
