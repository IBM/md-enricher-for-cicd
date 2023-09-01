#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

# Get the contents of the downstream repos

def clone(self, details):

    # Clone the branch of the downstream repo being worked on

    import io  # for extracting the archive download of the repo
    import os
    import requests  # for running curl-like API requests
    import shutil  # for copying files
    import subprocess
    import time
    import zipfile  # for extracting the archive download of the repo

    # from errorHandling.errorHandling import addToWarnings
    from errorHandling.errorHandling import addToErrors
    from setup.exitBuild import exitBuild

    # 1. If the staging branch exists clone it. If not, clone the upstream branch and checkout the new staging branch.
    # 2. Can't create the PR branch until after the main branch is pushed to.
    # The PR will be created on second push, not first since the staging and PR branch would match.

    def checkBranchExistence(branches, branchToCreate):

        if branchToCreate in branches:
            # self.log.info(branchToCreate + ' branch already exists.')
            BRANCH_EXISTS = True
        else:
            # self.log.info(branchToCreate + ' branch does not exist yet.')
            BRANCH_EXISTS = False
        return (BRANCH_EXISTS)

    def cloneBranch(BRANCH_TO_CLONE, CLONE_DIR, details):
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
        try:
            # Clone the repo
            subprocess.call('git clone --depth 1 -b ' + BRANCH_TO_CLONE + " https://" +
                            str(details["username"]) + ":" + str(details["token"]) + '@' +
                            self.location_github_domain + '/' + self.location_github_org + '/' +
                            self.location_github_repo + ".git " + CLONE_DIR + ' --quiet', shell=True)

        # If the clone fails, download a zip and extract the files.
        except Exception:
            self.log.info('Could not be cloned: https://' + self.location_github_domain + '/' + self.location_github_org +
                          '/' + self.location_github_repo + ".git")
            self.log.info('Waiting 5 seconds to try again.')
            time.sleep(5)

            try:
                # Try again to clone the repo
                subprocess.call('git clone --depth 1 -b ' + BRANCH_TO_CLONE + " https://" +
                                str(details["username"]) + ":" + str(details["token"]) + '@' +
                                self.location_github_domain + '/' + self.location_github_org + '/' +
                                self.location_github_repo + ".git " + CLONE_DIR + ' --quiet', shell=True)

            except Exception:
                if os.path.isdir(self.location_dir):
                    shutil.rmtree(self.location_dir)
                    self.log.info('Removing: ' + self.location_dir)

                # If the clone from the CLI didn't work, try downloading the files via the API
                try:
                    self.log.info('Trying to get a zipball instead: ' + self.location_github_api_repos + '/zipball/' + BRANCH_TO_CLONE)
                    r = requests.get(self.location_github_api_repos + '/zipball/' + BRANCH_TO_CLONE,
                                     auth=(str(details["username"]), str(details["token"])), stream=True)
                except Exception:
                    self.log.info('The zipball could not be retrieved either.')
                    addToErrors('The repo could not be cloned: https://' + self.location_github_domain + '/' +
                                self.location_github_org + '/' + self.location_github_repo + ".git", 'cloning', '', details,
                                self.log, self.location_name, '', '')
                    if not self.location_output_action == 'none':
                        exitBuild(details, self.log)
                else:
                    try:
                        z = zipfile.ZipFile(io.BytesIO(r.content))
                        z.extractall(path=None)
                    except Exception:
                        self.log.info('The file that was downloaded is not a zip file. The repo might not be accessible.')
                        addToErrors('The repo could not be cloned: https://' + self.location_github_domain + '/' +
                                    self.location_github_org + '/' + self.location_github_repo + ".git", 'cloning', '', details,
                                    self.log, self.location_name, '', '')
                        if not self.location_output_action == 'none':
                            exitBuild(details, self.log)
                    else:
                        # Everything gets cloned into a subdirectory named org-repo-sha. Move everything from that subdirectory up a level
                        if not os.path.isdir(CLONE_DIR):
                            addToErrors('The repo could not be cloned: https://' + self.location_github_domain + '/' +
                                        self.location_github_org + '/' + self.location_github_repo +
                                        ".git. The repo might not be accessible or the " + self.location_github_domain +
                                        ' domain might not be available at the moment.', 'cloning', '', details, self.log,
                                        self.location_name, '', '')
                            if not self.location_output_action == 'none':
                                exitBuild(details, self.log)
                        allDirs = os.listdir(CLONE_DIR)
                        for directory in allDirs:
                            if ((self.location_github_repo in directory) and (self.GITHUB_ORG in directory)):
                                os.rename(directory, self.location_dir)
                                self.log.info('Changed ' + directory + ' to ' + self.location_dir)
                        subprocess.call('git init', shell=True)
            else:
                self.log.info(self.location_github_repo + ', ' + BRANCH_TO_CLONE + ' branch cloned.')

        else:
            self.log.info(self.location_github_repo + ', ' + BRANCH_TO_CLONE + ' branch cloned.')

    # self.log.info('\n\n')
    # self.log.info('----------------------------------')
    self.log.info('Getting downstream contents https://' + self.location_github_domain + '/' + self.location_github_org +
                  '/' + self.location_github_repo + ".git" + ' for ' + self.location_name)
    # self.log.info('----------------------------------')

    # Get a list of all the branches in the repo
    getBranches = requests.get(self.location_github_api_repos + "/branches?per_page=100", auth=(details["username"], details["token"]))

    try:
        getBranchesJSON = getBranches.json()
    except Exception:
        addToErrors('A list of branches could not be retrieved. Review the request result:\n' + str(getBranches.text) +
                    'A list of branches could not be retrieved.', 'cloning', '', details, self.log, self.location_name)
        if not self.location_output_action == 'none':
            exitBuild(details, self.log)
    if 'Not Found' in str(getBranchesJSON):
        addToErrors('The repo was not found. Verify the domain, organization, and repo: https://' +
                    self.location_github_domain + '/' + self.location_github_org + '/' + self.location_github_repo,
                    'cloning', '', details, self.log, self.location_name, '', '')
        if not self.location_output_action == 'none':
            exitBuild(details, self.log)
    else:
        branches = []
        for branchSection in getBranchesJSON:
            branch = branchSection['name']
            branches.append(branch)

        BRANCH_EXISTS = checkBranchExistence(branches, self.location_github_branch)

        if ((BRANCH_EXISTS is True) and (not self.location_output_action == 'create-pr')):
            # Get the existing main branch
            cloneBranch(self.location_github_branch, self.location_dir, details)
            location_github_branch_push = self.location_github_branch
        elif ((BRANCH_EXISTS is True) and (self.location_output_action == 'create-pr')):
            BRANCH_EXISTS = checkBranchExistence(branches, self.location_github_branch_pr)
            if BRANCH_EXISTS is True:
                # Get the existing PR branch
                cloneBranch(self.location_github_branch_pr, self.location_dir, details)
                location_github_branch_push = self.location_github_branch_pr
            else:
                # Get the main branch
                cloneBranch(self.location_github_branch, self.location_dir, details)
                if not os.path.isdir(self.location_dir):
                    addToErrors('The ' + self.location_github_branch + ' branch could not be cloned.',
                                'cloning', '', details, self.log, self.location_name, '', '')
                    if not self.location_output_action == 'none':
                        exitBuild(details, self.log)
                os.chdir(self.location_dir)
                self.log.info('Checking out branch: ' + self.location_github_branch_pr)
                subprocess.call('git checkout -b ' + self.location_github_branch_pr + ' --quiet', shell=True)
                location_github_branch_push = self.location_github_branch_pr
        else:
            # Get the default branch
            getRepo = requests.get(self.location_github_api_repos, auth=(details["username"], details["token"]))
            getRepoJSON = getRepo.json()
            LOCATION_GITHUB_BRANCH_DEFAULT = getRepoJSON['default_branch']
            cloneBranch(LOCATION_GITHUB_BRANCH_DEFAULT, self.location_dir, details)
            os.chdir(self.location_dir)
            self.log.info('Checking out branch: ' + self.location_github_branch)
            subprocess.call('git checkout -b ' + self.location_github_branch + ' --quiet', shell=True)

            location_github_branch_push = self.location_github_branch

        self.log.info('Branch to push to: ' + location_github_branch_push)

    return (location_github_branch_push)
