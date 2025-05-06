#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def previousCommitInfo(details, log):

    # Get info from the last commit and the difference between that one and the last commit the build ran on

    import base64
    import re  # for doing finds within the topic content
    import subprocess
    import sys
    from subprocess import PIPE, STDOUT

    from mdenricher.sourceFileList.addToList import addToList
    from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.errorHandling.errorHandling import addToErrors
    from mdenricher.setup.exitBuild import exitBuild
    from mdenricher.errorHandling.parseSubprocessOutput import parseSubprocessOutput
    from mdenricher.errorHandling.requestValidation import requestValidation

    # Get the previous commit ID with the one that is stored in the file, if that file exists.
    # This is important to do because pull requests include more than one commit, so if possible,
    # we need to go back to the commit that was used in the last build, rather than the second to last commit in the repo.

    def getLastTwoCommits():

        commitsList = []

        # Use the CLI to get the right commit ID that matches the local files if possible
        # Otherwise, use the API, but it's possible the API could get ahead of the files that were checked out
        try:
            log.debug('Getting commits from the CLI')
            logResponse = subprocess.check_output('git log -2 --format="%H"', shell=True)
            logResponseDecoded = logResponse.decode("utf-8")
            logLines = logResponseDecoded.split('\n')
            while "" in logLines:
                logLines.remove("")
            for individualSha in logLines:
                commitsList.append(individualSha)

        except Exception:
            call = (details["source_github_api_repos"] + '/commits?sha=' +
                    details["current_github_branch"] + '&per_page=2')
            response = requestValidation(details, log, call, 'get', None, 'error',
                                         'The commits could not be retrieved for: ' +
                                         details["source_github_api_repos"] + '/commits?sha=' +
                                         details["current_github_branch"] + '&per_page=2', True, False,
                                         'Getting commits')

            try:
                commitsJSON = response.json()
            except Exception:
                addToErrors('The last two commits could not be retrieved. Review the request result.\n' + response.text +
                            '\nThe last two commits could not be retrieved.', 'commits', '', details, log, 'pre-build', '', '')
                exitBuild(details, log)

            for commitJSON in commitsJSON:
                try:
                    individualSha = commitJSON['sha']
                    commitsList.append(individualSha)
                except Exception as e:
                    log.info('No previous commits to gather information from.')
                    log.debug(e)
                    break

        try:
            log.debug('Getting the current and previous commit ID from the last commits made to the repo.')
            current_commit_id = commitsList[0]
        except Exception as e:
            addToErrors('Commits could not be retrieved.\n' + str(e), 'commits', '', details, log, 'pre-build', '', '')
            exitBuild(details, log)

        try:
            previous_commit_id = commitsList[1]
        except Exception:
            previous_commit_id = 'None'

        return (current_commit_id, previous_commit_id)

    log.debug('\n\n')
    log.debug('---------------------------------------------------------')
    log.debug('SOURCE')
    log.debug('--------------------------------------------------------\n\n')

    source_files_original_list: dict[dict[str, str], dict[str, str]] = {}  # type: ignore[misc]

    # Make sure the local files are from the most recent commit
    try:
        # cloud-governance-framework/security-governed-content requires the token with the pull
        subprocessOutput = subprocess.Popen('git pull -q https://' +
                                            details["token"] + '@' +
                                            details["source_github_domain"] + '/' + details["source_github_org"] + '/' +
                                            details["source_github_repo"], shell=True, stdout=PIPE, stderr=STDOUT)

        # solution-tutorials is not using source as the default branch, so it needs checked out again
        subprocessOutput = subprocess.Popen('git checkout ' + details["source_github_branch"], shell=True, stdout=PIPE, stderr=STDOUT)
        exitCode = parseSubprocessOutput(subprocessOutput, log)
        log.debug(exitCode)

    except Exception:
        log.debug('git pull exception.')

    # Get the latest commit ID and the one right immediately before it.
    current_commit_id, previous_commit_id = getLastTwoCommits()

    # If this is for the source branch, not a feature branch,
    # get the details from the last commit file to compare against
    # But for the feature branch, the branch is compared against the source branch, not the previous commit ID
    if details["test_only"] is False:

        try:

            call = (details["source_github_api_repos"] + "/contents/" + details["last_commit_id_file"] +
                    "?ref=" + details["log_branch"])
            response = requestValidation(details, log, call, 'get', None, 'warning',
                                         'The last_commit_id_file could not be retrieved for: ' +
                                         details["source_github_api_repos"] + "/contents/" +
                                         details["last_commit_id_file"] + "?ref=" + details["log_branch"],
                                         False, False, 'Getting last_commit_id_file')
            commitIDJSON = response.json()
            lastCommitIDsEncoded = commitIDJSON['content']
            lastCommitIDsBytes = base64.b64decode(lastCommitIDsEncoded)
            lastCommitIDsDecoded = lastCommitIDsBytes.decode("utf-8")
            lastCommitIDsList = lastCommitIDsDecoded.split('\n')

            # Check if this build is restarted by looking for the build number in the last commit file
            rebuild = False
            if '\n' + details["build_number"] + ':' in lastCommitIDsDecoded and details['builder'] == 'travis':
                for lastCommitID in lastCommitIDsList:
                    if lastCommitID.startswith(details["build_number"] + ':'):
                        lastCommitIDsString = lastCommitID
                        rebuild = True
                        log.info('Rebuild detected for build ' + details["build_number"] + '. ' +
                                 'Using the current and previous commit ID stored from the original build.')
                        break
            else:
                # 0 is an empty newline to start the file
                lastCommitIDsString = lastCommitIDsList[1]

            # Get the previous commit ID from the last commit ID file
            if ':' in lastCommitIDsString:
                lastCommitIDsString = lastCommitIDsString.split(':', 1)[1]
            if ',' in lastCommitIDsString:

                # If this is a rebuild, get both the current and previous from the file
                if rebuild is True:
                    previous_commit_id, current_commit_id = lastCommitIDsString.split(',', 1)

                # If not a rebuild, then store both in case there are no new commits
                else:
                    original_previous_commit_id, previous_commit_id = lastCommitIDsString.split(',', 1)

            # Legacy, only current commit ID was stored
            else:
                previous_commit_id = lastCommitIDsString

        except Exception as e:
            log.debug('The last commit ID file could not be retrieved. Using the last two commits to the repo instead.')
            log.debug(e)

    # Make sure there are no newlines in the commit ID
    previous_commit_id = re.sub('\n', '', previous_commit_id)

    # If there is a rebuild and there seems to be no changes
    # re-run on the same files that were previously run on
    # assuming there was an issue that needs processed again
    if current_commit_id == previous_commit_id:
        log.debug('The current commit ID matches the previous that the Markdown Enricher ran on.')
        try:
            original_previous_commit_id
        except Exception:
            log.info('All changes have already been processed in a previous build. Exiting.')
            sys.exit(0)
        else:
            previous_commit_id = original_previous_commit_id
            log.debug('Resetting the previous commit ID to the one in the last commit ID file to re-run on the same files.')

    # If this isn't the source branch, compare it against the source branch and if it matches,
    # it's a new branch and therefore, doesn't need to run on these files. Exit if there's no difference.
    if details["test_only"] is True:
        call = (details["source_github_api_repos"] + '/compare/' +
                details["source_github_branch"] + '...' + current_commit_id)
        response = requestValidation(details, log, call, 'get', None, 'error',
                                     'The branch status could not be retrieved for: ' +
                                     details["source_github_api_repos"] + '/compare/' +
                                     details["source_github_branch"] + '...' + current_commit_id,
                                     False, False, 'Comparing source branch with current commit ID')
        branchStatusJSON = response.json()
        try:
            branchStatus = branchStatusJSON['status']
        except Exception:
            addToErrors('The branch status could not be retrieved. ' +
                        'The branch might not exist: ' + details["source_github_branch"] + '. Verify that the value for ' +
                        'source_github_branch that is specified in the locations file configuration section exists.',
                        'commits', '', details, log, 'pre-build', '', '')
            exitBuild(details, log)

        log.debug('branchStatus against ' + details["source_github_branch"] + ': ' + branchStatus)

        if branchStatus == 'identical':
            log.info('This commit is identical to what is currently in the ' + details["source_github_branch"] +
                     ' branch. The branch must be newly created and does not contain any new changes. Exiting.')
            sys.exit(0)

    # Get the author's name and the commit summary
    log.debug('Getting the author\'s name and commit summary.')
    try:
        logResponse = subprocess.check_output('git show --format="%an" --quiet ' + current_commit_id, shell=True)
        current_commit_author = logResponse.decode("utf-8")
        logResponse = subprocess.check_output('git show --format="%s" --quiet ' + current_commit_id, shell=True)
        current_commit_summary = logResponse.decode("utf-8")
        logResponse = subprocess.check_output('git show --format="%ce" --quiet ' + current_commit_id, shell=True)
        current_commit_email = logResponse.decode("utf-8")
    except Exception:
        try:
            call = details["source_github_api_repos"] + '/commits/' + current_commit_id
            response = requestValidation(details, log, call, 'get', None, 'error',
                                         'The commit details could not be retrieved for: ' +
                                         details["source_github_api_repos"] + '/commits/' + current_commit_id,
                                         False, False, 'Getting current_commit_id')
            commitDetailsJSON = response.json()
            current_commit_author = commitDetailsJSON['commit']['author']['name']
            current_commit_summary = commitDetailsJSON['commit']['message']
            current_commit_email = commitDetailsJSON['commit']['author']['email']
        except Exception:
            current_commit_summary = 'None'
            current_commit_email = 'None'
            current_commit_author = 'Unknown'

    # Make sure there are no line breaks in the summary
    if '\n' in current_commit_summary:
        current_commit_summary = current_commit_summary.split('\n', 1)[0]
    if '\n' in current_commit_author:
        current_commit_author = current_commit_author.split('\n', 1)[0]
    if '\n' in current_commit_email:
        current_commit_email = current_commit_email.split('\n', 1)[0]
    if '"' in current_commit_summary:
        current_commit_summary = current_commit_summary.replace('"', '')
    # Workaround for alchemy-containers/documentation
    if ('Travis CI User: ' in current_commit_summary) or ((current_commit_author + ': ') in current_commit_summary):
        current_commit_summary = current_commit_summary.split(': ', 1)[1]

    source_files_original_list = {}
    if str(previous_commit_id) == 'None':
        log.info('First commit.')
    elif details["rebuild_all_files"] is True:
        log.info('Rebuilding all files.')
    else:
        filesJson = {}
        # log.info('Getting a list of files that have changed since the last build ran.')
        # Get a list of files that have changed since the last build ran

        try:

            log.debug('Getting diff between commits.')

            if details["test_only"] is True:
                # Compare the upstream branch with the current branch - this accumulates files that are changed from commit to commit
                diffURL = details["source_github_api_repos"] + '/compare/' + details["source_github_branch"] + '...' + details["current_github_branch"]
            else:
                # Compare the current ID with the previous ID
                diffURL = details["source_github_api_repos"] + '/compare/' + previous_commit_id + '...' + current_commit_id + '?per_page=100'
            response = requestValidation(details, log, diffURL, 'get', None, 'error', 'The diff could not be retrieved: ' +
                                         details["source_github_api_repos"] + '/compare/' +
                                         details["source_github_branch"] + '...' +
                                         details["current_github_branch"], True, False,
                                         'Comparing previous commit ID with the current commit ID')

        finally:
            if 'No common ancestor' in response.text or not response.status_code == 200:
                log.debug('A diff between the two commit IDs could not be retrieved.\n' + str(response.status_code))
                log.debug(response.text)
                if 'No common ancestor' in response.text:
                    # This workaround is needed when the last commit file contains a commit ID that is no longer in the repository.
                    # Could happen when a commit history is blown away or if files are copied into a new repo
                    description = 'The problem might be with the previous commit ID: ' + previous_commit_id + '.'
                elif response.status_code == 404:
                    description = "Try again later."
                elif response.status_code == 401:
                    description = "Verify the Github username and token."
                addToErrors('Github or the https://' +
                            details["source_github_domain"] + '/' + details["source_github_org"] + '/' +
                            details["source_github_repo"] + ' repo is not accessible. ' + description, 'commits', '', details, log, 'pre-build', '', '')
                exitBuild(details, log)

        try:
            compareDiffJSON = response.json()
        except Exception:
            log.debug('No compareDiffJSON to display.')
            log.debug('No JSON was returned to parse. Status code: ' +
                      str(response.status_code) + '.')
            addToErrors('Github or the https://' +
                        details["source_github_domain"] + '/' + details["source_github_org"] + '/' +
                        details["source_github_repo"] + ' repo is not accessible. Try again later.', 'commits', '', details, log, 'pre-build', '', '')
            exitBuild(details, log)

        # The difference between each try and except below is whether there is one file changed or more than
        # one file changed in the JSON response of the diff
        try:
            # Multiple files
            for compareDiffList in compareDiffJSON:
                filesJson = compareDiffList['files']
        except Exception:
            try:
                # Single file
                filesJson = compareDiffJSON['files']
            except Exception:
                log.debug('A diff could not be made between the current commit ID and the previous commit ID. ' +
                          'Check permissions for ' + details["username"] + ' in the upstream source repository.')

        fileCount = 0
        if filesJson == {}:
            log.debug('No files returned.')
        else:
            try:
                # Try twice to get the filename, status, and patch from the JSON response of the API request for
                # commit info. Check the first time for multiple topics nested, which usually there are.
                # Otherwise, if there's an exception, just get the one.
                # Check for multiple files in the commit JSON
                for fileSection in filesJson:
                    fileCount = fileCount + 1
                    folderAndFile = fileSection['filename']
                    fileStatus = fileSection['status']
                    # Image files don't have a patch, so gotta circumvent that error with an exception
                    try:
                        filePatch = fileSection['patch']
                    except Exception:
                        filePatch = 'None'
                    try:
                        fileNamePrevious = fileSection['previous_filename']
                    except Exception:
                        fileNamePrevious = 'None'
                    source_files_original_list = addToList('None', details, log, fileNamePrevious,
                                                           filePatch, fileStatus, '/' + folderAndFile, source_files_original_list, [], [], [])

            except Exception:
                # If the multiple file check resulted in an exception, try checking for a single file in the commit JSON
                fileCount = fileCount + 1
                folderAndFile = filesJson['filename']
                fileStatus = filesJson['status']
                try:
                    filePatch = filesJson['patch']
                except Exception:
                    filePatch = 'None'
                try:
                    fileNamePrevious = filesJson['previous_filename']
                except Exception:
                    fileNamePrevious = 'None'
                source_files_original_list = addToList('None', details,
                                                       log, fileNamePrevious,
                                                       filePatch, fileStatus, '/' + folderAndFile, source_files_original_list, [], [], [])

            # Ignore the mypy comparison-overlap errors here:
            # https://mypy.readthedocs.io/en/stable/error_code_list2.html#check-that-comparisons-are-overlapping-comparison-overlap
            # Switch to the CLI and run commands to gather information about the
            # remaining files that the API did not catch
            # Using the CLI entirely doesn't seem great though because it does
            # not seem to catch renames, or at least not from VS Code
            if (fileCount > 299):
                cliCommitListBYTES = subprocess.check_output('git diff ' + previous_commit_id + ' ' + current_commit_id + ' --name-status', shell=True)
                cliCommitListString = cliCommitListBYTES.decode("utf-8")
                if '\n' in cliCommitListString:
                    cliCommitList = cliCommitListString.split('\n')
                else:
                    cliCommitList = [cliCommitListString]
                for commit in cliCommitList:
                    if not commit == '':
                        cli_list = commit.split()
                        folderAndFile = cli_list[-1]
                        log.info(folderAndFile)
                        if (('/' + folderAndFile) not in source_files_original_list.keys()):  # type: ignore[comparison-overlap]
                            # Get file status
                            fileNamePrevious = 'None'
                            if cli_list[0] == 'A':
                                fileStatus = 'added'
                            elif cli_list[0] == 'C':
                                fileStatus = 'modified'
                            elif cli_list[0] == 'D':
                                fileStatus = 'deleted'
                            elif cli_list[0] == 'M':
                                fileStatus = 'modified'
                            elif cli_list[0] == 'R':
                                fileStatus = 'renamed'
                                fileRenameBytes = subprocess.check_output('git diff ' + previous_commit_id + ' ' + current_commit_id +
                                                                          ' --patch --diff-filter=R' + folderAndFile, shell=True)
                                fileNamePrevious = fileRenameBytes.decode("utf-8")
                            else:
                                fileStatus = 'modified'
                            # Get file patch
                            if folderAndFile.endswith(tuple(details["filetypes"])):
                                try:
                                    filePatchBytes = subprocess.check_output('git diff ' + previous_commit_id + ' ' + current_commit_id +
                                                                             ' --patch ' + folderAndFile, shell=True)
                                    filePatch = filePatchBytes.decode("utf-8")
                                except Exception:
                                    filePatch = ''
                            else:
                                filePatch = ''

                            source_files_original_list = addToList('None', details, log, fileNamePrevious,
                                                                   filePatch, fileStatus, '/' + folderAndFile, source_files_original_list, [], [], [])

                addToWarnings('The commit included 300 or more files. ' +
                              'The Git API could not include the details for more than 300 files in a commit. ' +
                              'Information for the remaining files are being gathered from the CLI. ' +
                              'All of the files from the commit are being handled in this build, but deletions related ' +
                              'to file renames or removals might not happen as desired downstream on the files that ' +
                              'were over the first alphabetical 300.\n', 'commits', '', details, log, 'pre-build', '', '')
        # Summary of the information we got above
        log.info('Previous commit ID: ' + str(previous_commit_id))
        log.info('Current commit ID: ' + str(current_commit_id))
        log.info('Current commit description: ' + str(current_commit_summary + '\n'))

        log.info('These were the files changed since the last commit that a build ran on:')
        if source_files_original_list == {}:
            log.info('No changes found.')
        else:
            for source_file, source_file_info in source_files_original_list.items():
                log.info(str(source_file) + str(' (' + source_files_original_list[source_file]['fileStatus'] + ')'))
        log.info('')

    return (current_commit_author, current_commit_email, current_commit_id, current_commit_summary, previous_commit_id, source_files_original_list)
