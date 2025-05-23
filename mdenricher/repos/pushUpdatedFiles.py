#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def pushUpdatedFiles(self, details):

    try:

        # Update all of the files in the downstream repos with the changes this build has created

        import base64  # For encoding & decoding API commits
        # from datetime import datetime
        import os  # for running OS commands like changing directories or listing files in directory
        import re
        import subprocess
        from subprocess import PIPE, STDOUT
        import time
        from mdenricher.repos.locationCommitSummary import locationCommitSummary

        from mdenricher.errorHandling.errorHandling import addToWarnings
        from mdenricher.errorHandling.errorHandling import addToErrors
        from mdenricher.errorHandling.parseSubprocessOutput import parseSubprocessOutput
        from mdenricher.errorHandling.pushErrors import pushErrors
        from mdenricher.errorHandling.requestValidation import requestValidation
        from mdenricher.setup.exitBuild import exitBuild

        startTime = time.time()
        if self.location_ibm_cloud_docs is True and 'draft' in self.location_name:
            time.sleep(10)

        endTime = time.time()
        totalTime = endTime - startTime
        sectionTime = str(round(totalTime, 2))
        self.log.debug(self.location_name + ' queue delay: ' + sectionTime)

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

        try:
            os.system("git config --global user.name \"" + details["username"] + "\"")
            if '@' in details["username"]:
                os.system("git config --global user.email \"" + details["username"] + "\"")
        except Exception:
            pass

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
                elif os.path.isfile(details["error_file"]):
                    self.log.error('Changes are not being pushed for ' + self.location_name + ' because content errors exist.')
                else:
                    # Otherwise, push the new branch
                    self.log.debug('Pushing new branch ' + self.location_github_branch_push + ' to repo.')
                    try:
                        subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' push origin -u ' +
                                                            self.location_github_branch_push + '  --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                        self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
                    except Exception as e:
                        self.log.error(e)
                        addToErrors('The new branch ' + self.location_github_branch_push + ' could not be pushed to the repo.',
                                    self.location_name, '', details, self.log, 'post-build', '', '')
                    else:
                        self.log.debug('New branch ' + self.location_github_branch_push + ' pushed to repo.')
                        time.sleep(5)
                        self.log.debug(subprocessOutput)
                        try:
                            status_bytes = subprocess.check_output('git -C ' + self.location_dir + ' status --short', shell=True)
                            status = status_bytes.decode("utf-8")
                        except Exception:
                            status = ''

                        if ('nothing to commit' in status.lower()) or (status == '\n') or (status == '') and (self.location_github_branch_push is not None):
                            self.log.debug('No additional commits to push.')
                        else:
                            self.pushSuccessful = True

        else:

            try:
                self.log.debug('Adding all files to be committed.')
                subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' add --all', shell=True, stdout=PIPE, stderr=STDOUT)
                self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
            except Exception as gitException:
                startTime = time.time()
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
                                call = (self.location_github_api_prefix + "/contents/" + folderAndFile + '?ref=' +
                                        self.location_github_branch_push)
                                response = requestValidation(details, self.log, call, 'get', None, 'error',
                                                             'The commit ID for ' + folderAndFile + ' file in the ' +
                                                             self.location_github_branch_push + ' branch could not be retrieved.', False, False,
                                                             'Getting the commit ID for ' + folderAndFile)
                                responseJSON = response.json()
                                lastsha = responseJSON['sha']
                            except Exception:
                                # The file didn't exist in the repo before. So create the file rather than update it.
                                try:
                                    self.log.debug('File does not exist in ' + self.location_name + ' yet.')
                                    call = self.location_github_api_prefix + "/contents/" + folderAndFile
                                    payload = {"message": self.currentCommitSummary,
                                               "content": fileContentsEncoded.decode("utf-8"),
                                               "branch": self.location_github_branch_push}
                                    response = requestValidation(details, self.log, call, 'put', payload, 'error',
                                                                 'The file could not be put into Github: ' +
                                                                 self.location_github_api_prefix + "/contents/" + folderAndFile + ', ' +
                                                                 self.location_github_branch_push, False, False,
                                                                 'Putting ' + folderAndFile)
                                except Exception:
                                    self.log.debug('ERROR. Could not add ' + folderAndFile + ' to ' + self.location_name +
                                                   ' via the API. 1 - File does not exist in the repo or authentication ' +
                                                   'error (bad API request).')
                                    self.log.debug(response.status_code)
                            else:
                                # Update the base 64 encoded version of the contents into staging/prod
                                try:
                                    fileName_open = open(self.location_dir + folderPath + file_name, 'r', encoding="utf8", errors="ignore")
                                    topicContents = fileName_open.read()
                                    fileName_open.close()
                                    oldContent = responseJSON['content']
                                    if not oldContent == topicContents:
                                        call = self.location_github_api_prefix + "/contents/" + folderAndFile
                                        payload = {"message": self.currentCommitSummary,
                                                   "content": fileContentsEncoded.decode("utf-8"),
                                                   "sha": lastsha,
                                                   "branch": self.location_github_branch_push}
                                        response = requestValidation(details, self.log, call, 'put', payload, 'warning',
                                                                     'The file could not be put into Github: ' +
                                                                     self.location_github_api_prefix + "/contents/" + folderAndFile + ', ' +
                                                                     self.location_github_branch_push, False, False, "Putting " + folderAndFile)
                                        stringStatusCode = str(response.status_code)
                                    else:
                                        self.log.debug('No changes detected. Not committing this file to ' + self.location_name + '.')
                                        stringStatusCode = 'Not committed'
                                except Exception:
                                    self.log.debug('ERROR. Could not add ' + folderAndFile + ' to ' + self.location_name +
                                                   ' via the API. 2 - File existed before, ' +
                                                   'but a new version could not be written (bad API request).')
                            stringStatusCode = str(response.status_code)
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
                endTime = time.time()
                totalTime = endTime - startTime
                sectionTime = str(round(totalTime, 2))
                self.log.info(self.location_name + ' add all exception: ' + sectionTime)

            # CLI commands - status check, merge, push.
            else:
                startTime = time.time()
                LOCATION_COMMIT_SUMMARY = locationCommitSummary(self, details)
                status_bytes = subprocess.check_output('git -C ' + self.location_dir + ' status --short', shell=True)
                status = status_bytes.decode("utf-8")
                if ('nothing to commit' in status.lower()) or (status == '\n') or (status == ''):
                    self.log.debug('Nothing to commit to ' + self.location_name + '.')
                else:
                    try:
                        self.log.debug('Committing the changes.')
                        subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' commit -m "' +
                                                            LOCATION_COMMIT_SUMMARY + '" --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                        self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
                    except Exception:
                        self.log.debug('Nothing to commit.')
                    else:
                        if self.exitCode > 0:
                            self.log.debug('Commit failed. Changes could not be pushed.')
                        elif os.path.isfile(details["error_file"]):
                            self.log.error('Changes are not being pushed for ' + self.location_name + ' because content errors exist.')
                        else:
                            try:
                                self.log.debug('Merging the commit.')
                                subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' merge --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
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
                                    if self.exitCode == 128:
                                        subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' push origin HEAD:' +
                                                                            str(self.location_github_branch_push) +
                                                                            '  --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                                        self.log.debug('Pushing with origin HEAD:' + str(self.location_github_branch_push) + '.')
                                        self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)
                                    if self.exitCode > 0:
                                        subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' push origin ' +
                                                                            str(self.location_github_branch_push) +
                                                                            '  --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                                        self.log.debug('Pushing with upstream origin ' + str(self.location_github_branch_push) + '.')
                                        self.exitCode = parseSubprocessOutput(subprocessOutput, self.log)

                                except Exception as e:
                                    self.log.error(e)

                                    try:
                                        subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' push origin ' +
                                                                            str(self.location_github_branch_push) +
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
                    if self.pushSuccessful is True:
                        if str(self.location_github_branch_push) == self.location_name:
                            self.log.info('Pushed files: ' + self.location_name + '\n' + status)
                        else:
                            self.log.info('Pushed files: ' + self.location_name + ', ' + str(self.location_github_branch_push) + ' branch\n' + status)
                        self.log.debug('Push successful.')
                        startTime = time.time()
                    else:
                        message = ('The changes were not pushed to the ' + str(self.location_github_branch_push) +
                                   ' branch of the repo for ' + self.location_name + '.')
                        if os.path.isfile(details["error_file"]):
                            message = message + ' Fix content errors that are preventing the push from completing.'
                        addToErrors(message, self.location_name, '', details, self.log, 'post-build', '', '')
                        self.log.debug(str(subprocessOutput.stdout))

                endTime = time.time()
                totalTime = endTime - startTime
                sectionTime = str(round(totalTime, 2))
                self.log.debug(self.location_name + ' push: ' + sectionTime)

        # Was something commited to create-pr locations? If a PR doesn't already exist that's created by the user, create the PR
        if ((self.location_output_action == 'create-pr') and
                (not self.location_github_branch_push == self.location_github_branch) and
                (self.pushSuccessful is True)):
            startTime = time.time()
            # List PRs
            call = self.location_github_api_repos + '/pulls?head=' + self.location_github_branch
            response = requestValidation(details, self.log, call, 'get', None, 'warning',
                                         'The pull requests could not be retrieved for the repo: ' +
                                         self.location_github_api_repos + '/pulls?head=' + self.location_github_branch, False, False, 'Getting existing PRs')
            try:
                PRs = []
                PRs = response.json()
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
                        # self.log.debug(self.source_files_location_list)
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
                self.log.debug('Creating pull request for commit ' + details["current_commit_id"])
                if self.location_internal_framework is not None:
                    PRBody = PRBodyIntroTip + PRBodyIntro + '\n'.join(linkList)
                else:
                    PRBody = ("See the Commits and Files changed tabs for more information about what is " +
                              "included in this pull request.")
                payload = {"title": "Next " + self.location_github_branch + " push", "body": PRBody,
                           "head": self.location_github_branch_push, "base": self.location_github_branch}
                call = self.location_github_api_repos + '/pulls?head=' + self.location_github_branch
                response = requestValidation(details, self.log, call, 'post', payload, 'error',
                                             'The pull request could not be created for: ' +
                                             self.location_github_api_repos + '/pulls?head=' + self.location_github_branch, False, False,
                                             'Creating PR')
                if response.status_code == 201:
                    responseJson = response.json()
                    prURL = responseJson['html_url']
                    prTitle = responseJson['title']
                    prID = responseJson['number']
                    self.log.info('Created a pull request for the ' + self.location_github_branch_push +
                                  ' branch to the ' + self.location_github_branch + ' branch:')
                    self.log.info('#' + str(prID) + ': ' + prTitle + ', ' + prURL)
                    self.log.debug('SUCCESS!')
                else:
                    if response.status_code == 401:
                        addToErrors('The pull request could not be created because of an authentication error. ' +
                                    'Maybe the token expired or the username must be updated.',
                                    self.location_name, '', details, self.log, 'post-build', '', '')
                    elif response.status_code == 422:
                        addToErrors('The pull request could not be created for one of three potential reasons. ' +
                                    '1. There might be a pull request already created for the ' +
                                    str(self.location_github_branch_push) + ' branch. Close the pull request. ' +
                                    '2. The ' +
                                    str(self.location_github_branch_push) + ' branch history might not match the publish branch history. ' +
                                    'Delete the ' +
                                    str(self.location_github_branch_push) + ' branch and let the build re-create it. ' +
                                    '3. The response from the API call might be empty. ' +
                                    'If Github is accessible, try starting another build.',
                                    self.location_name, '', details, self.log, 'post-build', '', '')
                    elif response.status_code == 500:
                        addToErrors('The pull request could not be created. The repo or the ' +
                                    details["source_github_domain"] + ' domain might not be accessible.' +
                                    str(response.status_code), self.location_name, '', details, self.log, 'post-build', '', '')
                    else:
                        addToErrors('The pull request could not be created. ' + str(response.status_code),
                                    self.location_name, '', details, self.log, 'post-build', '', '')
                    exitBuild(details, self.log)
            else:
                for PR in PRs:
                    PRHead = PR['head']['ref']
                    if PRHead == self.location_github_branch_push:
                        PRNumber = PR['number']
                        PRTitle = PR['title']
                        PRURL = PR['html_url']
                        PRBody = str(PR['body'])
                        if str(PRBodyIntro) in PRBody and self.location_internal_framework is not None:
                            existingLinkListString = PRBody.split(PRBodyIntro, 1)[1]
                            existingLinkList = existingLinkListString.split('\n')
                            for link in linkList:
                                if link not in existingLinkList and not link == '':
                                    existingLinkList.append(link)
                            existingLinkList.sort()
                            PRBodyRevised = PRBodyIntroTip + PRBodyIntro + '\n'.join(existingLinkList)
                            if not PRBodyRevised == PRBody:
                                self.log.debug('Updating PR body.')
                                payload = {"body": PRBodyRevised}
                                call = self.location_github_api_repos + '/pulls/' + str(PRNumber)
                                response = requestValidation(details, self.log, call, 'patch', payload, 'warning',
                                                             'The pull request body could not be updated for: ' +
                                                             self.location_github_api_repos + '/pulls/' + str(PRNumber), False, False, 'Updating PR body')
                        self.log.info('Updated pull request for the ' + self.location_github_branch_push +
                                      ' branch to the ' + self.location_github_branch + ' branch:')
                        self.log.info('#' + str(PRNumber) + ': ' + PRTitle + ', ' + PRURL)
            self.log.debug('File update complete.')
            endTime = time.time()
            totalTime = endTime - startTime
            sectionTime = str(round(totalTime, 2))
            self.log.debug(self.location_name + ' pr: ' + sectionTime)

    except Exception as e:
        addToErrors('The push could not be completed for ' + self.location_name + '.\n' + str(e),
                    self.location_name, '', details, self.log, 'push', '', '')
