#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def pushUpdatedFiles(self, details, pushQueue):

    # Update all of the files in the downstream repos with the changes this build has created

    import base64  # For encoding & decoding API commits
    from datetime import datetime
    import json  # for sending data with and parsing data from requests
    import os  # for running OS commands like changing directories or listing files in directory
    import re
    import requests  # for running curl-like API requests
    import subprocess
    from subprocess import PIPE, STDOUT
    import time
    from mdenricher.repos.locationCommitSummary import locationCommitSummary

    from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.errorHandling.errorHandling import addToErrors
    from mdenricher.errorHandling.parseSubprocessOutput import parseSubprocessOutput
    from mdenricher.errorHandling.pushErrors import pushErrors
    from mdenricher.setup.exitBuild import exitBuild

    if details['ibm_cloud_docs'] is True:
        while (self.location_github_org + '/' + self.location_github_repo) in pushQueue:
            time.sleep(1)

        if (self.location_github_org + '/' + self.location_github_repo) not in pushQueue:
            pushQueue.append(self.location_github_org + '/' + self.location_github_repo)
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            self.log.debug('Adding ' + self.location_name + ' location to push queue: ' + current_time)
            time.sleep(6)

    self.pushSuccessful = False

    # Check in the changed files to staging/prod!
    # self.log.debug('\n\n')
    # self.log.debug('----------------------------------')
    self.log.debug('\n')
    self.log.debug('Pushing changes for ' + self.location_name + ':')
    # self.log.debug('----------------------------------')

    os.chdir(self.location_dir)

    # Check and see if there are any changes to the files for the self.location_name.
    # It could be that changes are made to staging content and not prod.

    try:
        status_bytes = subprocess.check_output('git -C ' + self.location_dir + ' status --short', shell=True)
        status = status_bytes.decode("utf-8")
    except Exception as statusException:
        self.log.debug('WARNING: git status command could not be completed.')
        self.log.debug(statusException)
        status = 'None'

    if ('nothing to commit' in status.lower()) or (status == '\n') or (status == '') and (self.location_github_branch_push is not None):

        # Check if the branch has been pushed before or not
        try:
            branches_bytes = subprocess.check_output('git -C ' + self.location_dir + ' branch -r', shell=True)
            branches = branches_bytes.decode("utf-8")
        except Exception as statusException:
            self.log.debug('WARNING: git branch command could not be completed.')
            self.log.debug(statusException)
            status = 'None'
        else:
            # If already there, don't do anything else
            if ('origin/' + str(self.location_github_branch_push)) in branches:
                self.log.debug('Nothing to commit to ' + self.location_name + '.')
            else:
                # Otherwise, push the new branch
                self.log.debug('Pushing new branch ' + self.location_github_branch_push + ' to repo.')
                try:
                    pushBranchOutput = subprocess.check_output('git -C ' + self.location_dir + ' push origin -u ' +
                                                               self.location_github_branch_push + '  --quiet', shell=True)
                except Exception as e:
                    self.log.error(e)
                    addToErrors('The new branch ' + self.location_github_branch_push + ' could not be pushed to the repo.',
                                'push', '', details, self.log, 'post-build', '', '')
                else:
                    self.log.debug('New branch ' + self.location_github_branch_push + ' pushed to repo.')
                    self.log.debug(pushBranchOutput)

    else:
        try:
            self.log.debug('Adding all files to be committed.')
            subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' add --all', shell=True, stdout=PIPE, stderr=STDOUT)
            self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
        except Exception as gitException:
            self.log.debug('WARNING: Failed to add, commit, and push all files at the same time. Resulted in:')
            self.log.debug(gitException)
            self.log.debug('Trying to add individual files via the API instead.')
            for source_file, source_file_info in self.source_files.items():
                folderAndFile = self.source_files[source_file]['folderAndFile']
                file_name = self.source_files[source_file]['file_name']
                folderPath = self.source_files[source_file]['folderPath']
                if folderAndFile.endswith(tuple(details["filetypes"])):
                    if os.path.isfile(self.location_dir + folderPath + file_name):
                        self.log.debug(folderPath + file_name + ':')

                    # Check in the files that couldn't be added with --all by using the API
                        # The Git API requires base 64 encoding, so the topic contents have to be converted before the API request can be made
                        fileName_open = open(self.location_dir + folderPath + file_name, 'r', encoding="utf8", errors="ignore")
                        fileContents = fileName_open.read()
                        fileContentsEncoded = base64.b64encode(fileContents.encode())
                        fileName_open.close()
                        try:
                            # Get the commit ID from the previous commit of this file
                            t = requests.get(self.location_github_api_prefix + "/contents/" + folderAndFile + '?ref=' +
                                             self.location_github_branch_push, auth=(details["username"], details["token"]))
                            tJSON = t.json()
                            lastsha = tJSON['sha']
                        except Exception:
                            # The file didn't exist in the repo before. So create the file rather than update it.
                            try:
                                self.log.debug('File does not exist in ' + self.location_name + ' yet.')
                                r = requests.put(self.location_github_api_prefix + "/contents/" + folderAndFile,
                                                 auth=(details["username"], details["token"]),
                                                 data=json.dumps({"message": self.currentCommitSummary,
                                                                  "content": fileContentsEncoded.decode("utf-8"),
                                                                  "branch": self.location_github_branch_push}))
                            except Exception:
                                self.log.debug('ERROR. Could not add ' + folderAndFile + ' to ' + self.location_name +
                                               ' via the API. 1 - File does not exist in the repo or authentication ' +
                                               'error (bad API request).')
                                self.log.debug(r.status_code)
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
                                                                      "branch": self.location_github_branch_push}))
                                    stringStatusCode = str(r.status_code)
                                else:
                                    self.log.debug('No changes detected. Not committing this file to ' + self.location_name + '.')
                                    stringStatusCode = 'Not committed'
                            except Exception:
                                self.log.debug('ERROR. Could not add ' + folderAndFile + ' to ' + self.location_name +
                                               ' via the API. 2 - File existed before, ' +
                                               'but a new version could not be written (bad API request).')
                        stringStatusCode = str(r.status_code)
                        if stringStatusCode.startswith('2'):
                            self.log.debug('Success! Added ' + folderAndFile + ' to ' + self.location_name + ' via the API.')
                            self.pushSuccessful = True
                        elif 'Not committed' in stringStatusCode:
                            self.log.debug('No changes detected. Not committing this file to ' + self.location_name + '.')
                        else:
                            self.log.debug('WARNING. Could not add ' + folderAndFile + ' to ' + self.location_name + ' via the API.')
                            self.log.debug(stringStatusCode)
                else:
                    addToWarnings('Could not add ' + folderAndFile + ' to ' + self.location_name + ' via the API.',
                                  folderAndFile, folderPath + file_name, details, self.log, self.location_name, '', '')

        # CLI commands - status check, merge, push.
        else:
            LOCATION_COMMIT_SUMMARY = locationCommitSummary(self, details)
            status_bytes = subprocess.check_output('git -C ' + self.location_dir + ' status --short', shell=True)
            status = status_bytes.decode("utf-8")
            self.log.debug('Status:')
            self.log.debug(status)
            if ('nothing to commit' in status.lower()) or (status == '\n') or (status == ''):
                self.log.debug('Nothing to commit to ' + self.location_name + '.')
            else:
                # When this line is set, then the user displays as Travis CI User
                os.system("git config --global user.name \"" + details["current_commit_author"] + "\"")
                os.system("git config --global user.email \"" + details["current_commit_email"] + "\"")
                try:
                    self.log.debug('Committing the changes.')
                    subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' commit -m "' +
                                                        LOCATION_COMMIT_SUMMARY + '" --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                    self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
                except Exception:
                    self.log.debug('Nothing to commit.')
                else:
                    try:
                        self.log.debug('Merging the commit.')
                        subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' merge --quiet', shell=True)
                        self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
                    except Exception:
                        subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' merge ' + str(self.location_github_branch_push) +
                                                            ' --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                        self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
                        self.log.debug('Merging the commit with branch: ' + str(self.location_github_branch_push) + '.')

                    try:
                        self.log.debug('Pushing changed files.')
                        subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' push --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                        self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
                    except Exception:
                        try:
                            subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' push --set-upstream origin ' +
                                                                str(self.location_github_branch_push) +
                                                                ' --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                            self.log.debug('Setting upstream origin ' + str(self.location_github_branch_push) + '.')
                            self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
                        except Exception as e:
                            pushErrors(details, e, self.log)
                        else:
                            self.pushSuccessful = True
                    else:
                        try:
                            if self.exitCode > 0:
                                subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' push origin ' + str(self.location_github_branch_push) +
                                                                    '  --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                                self.log.debug('Pushing with upstream origin ' + str(self.location_github_branch_push) + '.')
                                self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
                        except Exception as e:
                            self.log.error(e)

                            try:
                                subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' push origin ' + str(self.location_github_branch_push) +
                                                                    '  --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                                self.log.debug('Try 2: Pushing with upstream origin ' + str(self.location_github_branch_push) + '.')
                                self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
                            except Exception:
                                self.log.debug('Push failed. Waiting 5 seconds and trying again.')
                                time.sleep(5)
                                try:
                                    subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' push origin ' +
                                                                        str(self.location_github_branch_push) +
                                                                        ' --quiet', shell=True, stdout=PIPE,
                                                                        stderr=STDOUT)
                                    self.log.debug('Try 3: Pushing with upstream origin ' + str(self.location_github_branch_push) + '.')
                                    self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
                                except Exception:
                                    self.log.debug('Push failed.')
                                else:
                                    if self.exitCode == 0:
                                        self.pushSuccessful = True
                            else:
                                if self.exitCode == 0:
                                    self.pushSuccessful = True
                        else:
                            if self.exitCode == 0:
                                self.pushSuccessful = True

        # Was something commited to Next Prod Push? If a PR doesn't already exist that's created by the user, create the PR for prod

        if self.pushSuccessful is True:
            self.log.debug('Push successful.')

            if (self.location_output_action == 'create-pr') and (not self.location_github_branch_push == self.location_github_branch):
                # List PRs
                listPRs = requests.get(self.location_github_api_repos + '/pulls?head=' + self.location_github_branch,
                                       auth=(details["username"], details["token"]))
                try:
                    PRs = listPRs.json()
                    PRstring = str(PRs)
                except Exception:
                    PRstring = ''
                if not PRstring == '[]':
                    self.log.debug('Existing PRs:')
                    for PR in PRs:
                        PRNumber = PR['number']
                        PRTitle = PR['title']
                        self.log.debug(str(PRNumber) + ': ' + PRTitle)

                # Get topic links for the PR body
                if self.location_internal_framework is not None:
                    changedFileList = status.split('\n')
                    linkList = []

                    for changedFile in changedFileList:
                        try:
                            changedFile = changedFile.rsplit(' ', 1)[1]
                            self.log.debug('Changed file: ' + changedFile)
                            self.log.debug(self.source_files_location_list)
                            for file_included in self.source_files:
                                if self.source_files[file_included]['file_name'] == changedFile:
                                    with open(self.location_dir + self.source_files[file_included]['folderPath'] +
                                              self.source_files[file_included]['file_name'], 'r', encoding="utf8", errors="ignore") as fileName_write:
                                        fileContents = fileName_write.read()
                                    break
                            topicID = re.findall('{: #(.*?)}', fileContents)[0]
                            self.log.debug('Topic ID found: ' + topicID)
                            subcollection = re.findall('subcollection: (.*?)\n', fileContents)[0]
                            self.log.debug('Subcollection: ' + subcollection)
                            linkList.append('[' + changedFile + '](' + self.location_internal_framework + '/' +
                                            subcollection + '?topic=' + subcollection + '-' + topicID + ')')
                            self.log.debug('[' + changedFile + '](' + self.location_internal_framework + '/' +
                                           subcollection + '?topic=' + subcollection + '-' + topicID + ')')
                        except Exception:
                            if not changedFile == '':
                                linkList.append(changedFile)
                    self.log.debug(linkList)

                if self.location_downstream_build_url is None:
                    buildLink = 'IBM Cloud Docs builds'
                else:
                    buildLink = ('[IBM Cloud Docs builds](' + self.location_downstream_build_url)
                    try:
                        buildLink = buildLink + '/job/' + subcollection + ')'
                    except Exception:
                        buildLink = buildLink + ')'

                PRBodyIntroTip = ('Tip: The changes in this PR might not be visible in the ' +
                                  'framework immediately. If not, allow the ' + buildLink + ' to ' +
                                  'complete and check back.\n\n')
                PRBodyIntro = 'Changed topics:\n'

                if self.location_github_branch_pr not in PRstring:
                    if self.location_internal_framework is not None:
                        PRBody = PRBodyIntroTip + PRBodyIntro + '\n'.join(linkList)
                    else:
                        PRBody = ("See the Commits and Files changed tabs for more information about what is " +
                                  "included in this pull request.")
                    g = {"title": "Next " + self.location_github_branch + " push", "body": PRBody,
                         "head": self.location_github_branch_push, "base": self.location_github_branch}
                    r = requests.post(self.location_github_api_repos + '/pulls?head=' + self.location_github_branch,
                                      auth=(details["username"], details["token"]), data=json.dumps(g))
                    self.log.debug('Creating pull request for commit ' + details["current_commit_id"])
                    if r.status_code == 201:
                        self.log.debug('SUCCESS!')
                    else:
                        if r.status_code == 401:
                            addToErrors('Authentication error. Maybe the token expired or the username must be updated.',
                                        'pr', '', details, self.log, 'post-build', '', '')
                        elif r.status_code == 422:
                            addToErrors('The pull request could not be created for one of three potential reasons. ' +
                                        '1. There might be a pull request already created for the ' +
                                        str(self.location_github_branch_push) + ' branch. Close the pull request. ' +
                                        '2. The ' +
                                        str(self.location_github_branch_push) + ' branch history might not match the publish branch history. ' +
                                        'Delete the ' +
                                        str(self.location_github_branch_push) + ' branch and let the build re-create it. ' +
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
                        if PRHead == self.location_github_branch_push:
                            PRNumber = PR['number']
                            PRTitle = PR['title']
                            PRBase = PR['base']['ref']
                            PRBody = PR['body']
                            if PRBodyIntro in PRBody and self.location_internal_framework is not None:
                                existingLinkListString = PRBody.split(PRBodyIntro, 1)[1]
                                existingLinkList = existingLinkListString.split('\n')
                                for link in linkList:
                                    if link not in existingLinkList and not link == '':
                                        existingLinkList.append(link)
                                existingLinkList.sort()
                                PRBodyRevised = PRBodyIntroTip + PRBodyIntro + '\n'.join(existingLinkList)
                                if not PRBodyRevised == PRBody:
                                    self.log.debug('Updating PR body.')
                                    g = {"body": PRBodyRevised}
                                    r = requests.patch(self.location_github_api_repos + '/pulls/' + str(PRNumber),
                                                       auth=(details["username"], details["token"]), data=json.dumps(g))
                            self.log.debug('Updating pull request #' + str(PRNumber) + ': ' + PRTitle + ', head: ' + PRHead + ', base: ' + PRBase + '.')
            self.log.debug('File update complete.')
        else:
            addToErrors('The changes could not be pushed to the ' + str(self.location_github_branch_push) + ' branch of the repo.',
                        'push', '', details, self.log, 'post-build', '', '')

    if details['ibm_cloud_docs'] is True:
        pushQueue.remove(self.location_github_org + '/' + self.location_github_repo)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.log.debug('Removing ' + self.location_name + ' from push queue: ' + current_time)
