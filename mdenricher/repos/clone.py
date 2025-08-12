#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

# Get the contents of the downstream repos

def clone(self, details):

    # Clone the branch of the downstream repo being worked on

    import io  # for extracting the archive download of the repo
    import os
    import shutil  # for copying files
    import subprocess
    import time
    import zipfile  # for extracting the archive download of the repo
    from subprocess import PIPE, STDOUT

    # from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.errorHandling.errorHandling import addToErrors
    from mdenricher.errorHandling.parseSubprocessOutput import parseSubprocessOutput
    from mdenricher.errorHandling.requestValidation import requestValidation
    from mdenricher.setup.exitBuild import exitBuild

    # 1. If the staging branch exists clone it. If not, clone the upstream branch and checkout the new staging branch.
    # 2. Can't create the PR branch until after the main branch is pushed to.
    # The PR will be created on second push, not first since the staging and PR branch would match.

    def checkBranchExistence(branches, branchToCreate):

        if branchToCreate in branches:
            self.log.debug(branchToCreate + ' branch exists.')
            BRANCH_EXISTS = True
        else:
            self.log.debug(branchToCreate + ' branch does not exist yet.')
            BRANCH_EXISTS = False
        return (BRANCH_EXISTS)

    def cloneBranch(BRANCH_TO_CLONE, details):

        exitCode = 0
        # Verify that the username and token are specified
        if ((details["username"] is None) or (details["token"] is None)):
            if details["username"] is None:
                addToErrors('A username was not specified in the environment variables.', 'cloning', '', details, self.log,
                            self.location_name, '', '')
            if details["token"] is None:
                addToErrors('A token was not specified in the environment variables.', 'cloning', '', details, self.log,
                            self.location_name, '', '')
            if not self.location_output_action == 'none':
                exitBuild(details, self.log)

        # CLONE THE REPOS TO A DIRECTORY
        exitCode = 1
        attempt = 1
        try:

            while attempt < 6 and exitCode > 0:

                self.log.debug('Clone attempt #' + str(attempt) + ': https://' +
                               self.location_github_domain + '/' + self.location_github_org +
                               '/' + self.location_github_repo + ".git, " + BRANCH_TO_CLONE)

                # Clone the repo
                subprocessOutput = subprocess.Popen('git clone --single-branch --depth 1 -b ' +
                                                    BRANCH_TO_CLONE + " https://" +
                                                    str(details["token"]) + '@' +
                                                    self.location_github_domain + '/' + self.location_github_org + '/' +
                                                    self.location_github_repo + ".git " + self.location_dir + ' --quiet',
                                                    shell=True, stdout=PIPE, stderr=STDOUT)
                exitCode = parseSubprocessOutput(subprocessOutput, self.log)

                if exitCode > 0:
                    self.log.debug('Waiting 5 seconds before trying again.')
                    time.sleep(5)
                    if os.path.isdir(self.location_dir):
                        shutil.rmtree(self.location_dir)
                        self.log.debug('Removing to try cloning again: ' + self.location_dir)

                attempt = attempt + 1

        # If the clone fails, download a zip and extract the files.
        except Exception as e:
            self.log.debug('Could not be cloned: https://' + self.location_github_domain + '/' + self.location_github_org +
                           '/' + self.location_github_repo + ".git")
            self.log.debug('Waiting 5 seconds to try again.')
            self.log.debug(str(e))
            time.sleep(5)

            try:
                # Try again to clone the repo
                subprocessOutput = subprocess.Popen('git clone --single-branch --depth 1 -b ' +
                                                    BRANCH_TO_CLONE + " https://" +
                                                    str(details["token"]) + '@' +
                                                    self.location_github_domain + '/' + self.location_github_org + '/' +
                                                    self.location_github_repo + ".git " + self.location_dir + ' --quiet',
                                                    shell=True, stdout=PIPE, stderr=STDOUT)
                exitCode = parseSubprocessOutput(subprocessOutput, self.log)

            except Exception:
                if os.path.isdir(self.location_dir):
                    shutil.rmtree(self.location_dir)
                    self.log.debug('Removing: ' + self.location_dir)

                # If the clone from the CLI didn't work, try downloading the files via the API
                try:
                    call = self.location_github_api_repos + '/zipball/' + BRANCH_TO_CLONE
                    response = requestValidation(details, self.log, call, 'get', None, 'error',
                                                 'The branch could not be cloned: ' +
                                                 self.location_github_api_repos + '/zipball/' +
                                                 BRANCH_TO_CLONE, True, True, 'Getting zipball: ' +
                                                 self.location_github_api_repos + '/zipball/' + BRANCH_TO_CLONE)
                except Exception:
                    self.log.debug('The zipball could not be retrieved either.')
                    addToErrors('The repo could not be cloned: https://' + self.location_github_domain + '/' +
                                self.location_github_org + '/' + self.location_github_repo + ".git", 'cloning', '', details,
                                self.log, self.location_name, '', '')
                    if not self.location_output_action == 'none':
                        exitBuild(details, self.log)
                else:
                    try:
                        z = zipfile.ZipFile(io.BytesIO(response.content))
                        z.extractall(path=None)
                    except Exception:
                        self.log.debug('The file that was downloaded is not a zip file. The repo might not be accessible.')
                        addToErrors('The repo could not be cloned: https://' + self.location_github_domain + '/' +
                                    self.location_github_org + '/' + self.location_github_repo + ".git", 'cloning', '', details,
                                    self.log, self.location_name, '', '')
                        if not self.location_output_action == 'none':
                            exitBuild(details, self.log)
                    else:
                        # Everything gets cloned into a subdirectory named org-repo-sha. Move everything from that subdirectory up a level
                        if not os.path.isdir(self.location_dir):
                            addToErrors('The repo could not be cloned: https://' + self.location_github_domain + '/' +
                                        self.location_github_org + '/' + self.location_github_repo +
                                        ".git. The repo might not be accessible or the " + self.location_github_domain +
                                        ' domain might not be available at the moment.', 'cloning', '', details, self.log,
                                        self.location_name, '', '')
                            if not self.location_output_action == 'none':
                                exitBuild(details, self.log)
                        allDirs = os.listdir(self.location_dir)
                        for directory in allDirs:
                            if ((self.location_github_repo in directory) and (self.GITHUB_ORG in directory)):
                                os.rename(directory, self.location_dir)
                                self.log.debug('Changed ' + directory + ' to ' + self.location_dir)
                        subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' init', shell=True, stdout=PIPE, stderr=STDOUT)
                        exitCode = parseSubprocessOutput(subprocessOutput, self.log)
            else:
                self.log.debug(self.location_github_repo + ', ' + BRANCH_TO_CLONE + ' branch cloned.')

        else:
            self.log.debug(self.location_github_repo + ', ' + BRANCH_TO_CLONE + ' branch cloned.')

        if exitCode > 0:
            addToErrors('The repo could not be cloned: https://' + self.location_github_domain + '/' +
                        self.location_github_org + '/' + self.location_github_repo +
                        ".git, " + BRANCH_TO_CLONE + ' branch.', 'clone', '', details, self.log, self.location_name, '', '')

    # self.log.info('\n\n')
    # self.log.info('----------------------------------')
    self.log.debug('Getting downstream contents https://' + self.location_github_domain + '/' + self.location_github_org +
                   '/' + self.location_github_repo + ".git" + ' for ' + self.location_name)
    # self.log.info('----------------------------------')

    self.changeToRebuildAll = False

    # Get a list of all the branches in the repo
    branches = []

    # CLI can only be used when the source and downstream are the same repo
    if ((details['source_github_domain'] + '/' + details['source_github_org'] + '/' + details['source_github_repo']) ==
            (self.location_github_domain + '/' + self.location_github_org + '/' + self.location_github_repo)):
        self.log.debug('Getting branches from the CLI')
        try:
            # If the clone happens without auth, then this command won't work.
            branchResponse = subprocess.check_output(['git ls-remote --heads --quiet'], stderr=subprocess.STDOUT, shell=True)
            branchResponseDecoded = branchResponse.decode("utf-8")
            if '\n' in branchResponseDecoded:
                branchesList = branchResponseDecoded.split('\n')
                self.log.debug('Branches list: ' + ', '.join(branchesList))
                for line in branchesList:
                    if 'refs/heads/' in line:
                        branches.append(line.rsplit('refs/heads/', 1)[1])
                self.log.debug('Available branches: ' + ', '.join(branches))
        except Exception:
            self.log.debug('The branch list could not be gathered. Attempting to get the branch list by using the API and continuing.')
    # Use the API when the source and downstream repos are not the same
    if branches == []:
        CONTINUE_BRANCH_CHECK_LOOP = True
        page = 0

        while CONTINUE_BRANCH_CHECK_LOOP is True:

            page = page + 1

            # Get a list of all the branches in the repo

            try:
                call = (self.location_github_api_repos + "/branches?per_page=100&page=" + str(page))
                response = requestValidation(details, self.log, call, 'get', None, 'error',
                                             'A list of branches could not be retrieved to verify the existence of the branch attempting to be cloned.',
                                             True, False, 'Getting list of branches')

            except Exception:
                CONTINUE_BRANCH_CHECK_LOOP = False

            try:
                getBranchesJSON = response.json()
            except Exception:
                addToErrors('A list of branches could not be retrieved. Review the request result:\n' + str(response.text) +
                            'A list of branches could not be retrieved.', 'cloning', '', details, self.log, self.location_name, '', '')
                if not self.location_output_action == 'none':
                    exitBuild(details, self.log)

            if 'github' not in str(getBranchesJSON):
                CONTINUE_BRANCH_CHECK_LOOP = False
            if 'Not Found' in str(getBranchesJSON):
                CONTINUE_BRANCH_CHECK_LOOP = False
                addToErrors('The downstream location_github_url was not found for ' + self.location_name + '. ' +
                            'Verify the username, token, domain, organization, and repo: https://' +
                            self.location_github_domain + '/' + self.location_github_org + '/' + self.location_github_repo,
                            'cloning', '', details, self.log, self.location_name, '', '')
                if not self.location_output_action == 'none':
                    exitBuild(details, self.log)
            else:
                for branchSection in getBranchesJSON:
                    branch = branchSection['name']
                    branches.append(branch)

    location_github_branch_push = None
    BRANCH_EXISTS = checkBranchExistence(branches, self.location_github_branch)

    if ((BRANCH_EXISTS is True) and (not self.location_output_action == 'create-pr')):
        # Get the existing main branch
        cloneBranch(self.location_github_branch, details)
        location_github_branch_push = self.location_github_branch
    elif ((BRANCH_EXISTS is True) and (self.location_output_action == 'create-pr')):
        BRANCH_EXISTS = checkBranchExistence(branches, self.location_github_branch_pr)
        if BRANCH_EXISTS is True:
            # Get the existing PR branch
            cloneBranch(self.location_github_branch_pr, details)
            location_github_branch_push = self.location_github_branch_pr
        else:
            # Get the branch to create the PR to
            cloneBranch(self.location_github_branch, details)
            if not os.path.isdir(self.location_dir):
                addToErrors('The ' + self.location_github_branch + ' branch could not be cloned.',
                            'cloning', '', details, self.log, self.location_name, '', '')
                if not self.location_output_action == 'none':
                    exitBuild(details, self.log)
            os.chdir(self.location_dir)
            self.log.debug('Checking out branch: ' + self.location_github_branch_pr)
            subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' checkout -b ' +
                                                self.location_github_branch_pr + ' --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
            exitCode = parseSubprocessOutput(subprocessOutput, self.log)
            if exitCode > 0:
                addToErrors('The ' + self.location_github_branch_pr + ' branch could not be checked out.',
                            'clone', '', details, self.log, self.location_name, '', '')
            location_github_branch_push = self.location_github_branch_pr

    elif BRANCH_EXISTS is False:
        self.changeToRebuildAll = True
        # If the repo URL is the same for source and location
        # use the source_github_repo from the locations file
        if details['source_github_repo'] == self.location_github_repo:
            # Get the source_github_branch branch
            LOCATION_DEFAULT_BRANCH_CLONE = details['source_github_branch']
        # If the URLs are different, use the default branch in the location repo
        else:
            # Get the default branch
            call = self.location_github_api_repos
            response = requestValidation(details, self.log, call, 'get', None, 'error',
                                         'The default branch could not be retrieved.', True, False, 'Getting default branch')
            LOCATION_DEFAULT_BRANCH_CLONE = response['default_branch']

        cloneBranch(LOCATION_DEFAULT_BRANCH_CLONE, details)
        os.chdir(self.location_dir)
        self.log.debug('Checking out branch: ' + self.location_github_branch)
        subprocessOutput = subprocess.Popen('git -C ' + self.location_dir + ' checkout -b ' +
                                            self.location_github_branch + ' --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
        exitCode = parseSubprocessOutput(subprocessOutput, self.log)
        if exitCode > 0:
            addToErrors('The branch could not be checked out.', 'clone', '', details, self.log, self.location_name, '', '')

        location_github_branch_push = self.location_github_branch

    self.log.debug('Branch to push to: ' + str(location_github_branch_push))

    return (str(location_github_branch_push), self.changeToRebuildAll)
