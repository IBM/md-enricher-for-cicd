#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def previousCommitInfo(details, log, current_commit_id, current_commit_summary):

    # Get info from the last commit and the difference between that one and the last commit the build ran on

    import base64
    import re  # for doing finds within the topic content
    import requests  # for running curl-like API requests
    import subprocess
    import sys

    from sourceFileList.addToList import addToList
    from errorHandling.errorHandling import addToWarnings
    from errorHandling.errorHandling import addToErrors
    from setup.exitBuild import exitBuild

    log.info('\n\n')
    log.info('---------------------------------------------------------')
    log.info('SOURCE')
    log.info('--------------------------------------------------------\n\n')

    source_files_original_list: dict[dict[str, str], dict[str, str]] = {}  # type: ignore[misc]
    commitsList = []
    messagesList = []

    # Get the latest commit ID and the one right immediately before it. Really, we just need the last commit ID.
    # Hopefully there's a commit ID file to get the commit before this one. But if not and this is not test,
    # the second to last one here will be used.

    # Get the last two commits to the current commit branch (though it seems like it's not filtering to just this branch)
    # We may or may not need this info going forward
    listCommits = requests.get(details["source_github_api_repos"] + '/commits?sha=' + details["current_github_branch"] +
                               '&per_page=2', auth=(details["username"], details["token"]))

    try:
        commitsJSON = listCommits.json()
    except Exception:
        addToErrors('The last two commits could not be retrieved. Review the request result.\n' + listCommits.text +
                    '\nThe last two commits could not be retrieved.', 'commits', '', details, log, 'pre-build', '', '')
        exitBuild(details, log)

    for commitJSON in commitsJSON:
        try:
            individualSha = commitJSON['sha']
            individualMessage = commitJSON['commit']['message']
            commitsList.append(individualSha)
            messagesList.append(individualMessage)
        except Exception as e:
            log.info('No previous commits to gather information from.')
            log.debug(e)
            break

    # Get the previous commit ID with the one that is stored in the file, if that file exists.
    # This is important to do because pull requests include more than one commit, so if possible,
    # we need to go back to the commit that was used in the last build, rather than the second to last commit in the repo.

    def getPreviousSha(commitsList):
        try:
            log.info(details["last_commit_id_file"] + ' might not exist yet. Getting the previous commit ID from the last commit made to the repo.')
            previous_commit_id = commitsList[1]
        except Exception as e:
            addToErrors('Not enough commits to continue.\n' + str(e), 'commits', '', details, log, 'pre-build', '', '')
            exitBuild(details, log)
        return (previous_commit_id)

    if details["test_only"] is False:
        try:
            commitID = requests.get(details["source_github_api_repos"] + "/contents/" + details["last_commit_id_file"] +
                                    "?ref=" + details["log_branch"], auth=(details["username"], details["token"]))
            commitIDJSON = commitID.json()
            previousVersionEncoded = commitIDJSON['content']
            previous_commit_id_bytes = base64.b64decode(previousVersionEncoded)
            previous_commit_id = previous_commit_id_bytes.decode("utf-8")
        except Exception:
            previous_commit_id = getPreviousSha(commitsList)
    else:
        previous_commit_id = getPreviousSha(commitsList)

    # This is a backup - this should have already been set in the setup.py file
    if (current_commit_id == 'None') or (current_commit_id == '') or (current_commit_id is None):
        try:
            current_commit_id = commitsList[0]
        except Exception:
            addToErrors('The last commit ID could not be retrieved. Verify that the ' + details["username"] +
                        ' username has write permission in the https://' + details["source_github_domain"] + '/' +
                        details["source_github_org"] + '/' + details["source_github_repo"] + ' repo.', 'commit ID', '',
                        details, log, 'pre-build', '', '')
            exitBuild(details, log)

        current_commit_summary = messagesList[0]

    # Is this necessary?
    if (current_commit_summary == 'None') or (current_commit_summary == '') or (current_commit_summary is None):
        commitJSON = requests.get(details["source_github_api_repos"] + '/commits/' + current_commit_id, auth=(details["username"], details["token"]))
        current_commit_summary = commitJSON['commit']['message']

    # This is a backup - this should have already been grabbed from the file
    if (previous_commit_id == 'None') or (previous_commit_id == '') or (previous_commit_id is None):
        try:
            previous_commit_id = commitsList[1]
            PREVIOUS_COMMIT_IDRetain = commitsList[1]
        except Exception:
            addToWarnings('The previous or next to last commit ID could not be retrieved.', 'commit ID', '', details,
                          log, 'pre-build', '', '')

    # Make sure there are no line breaks in the summary
    if '\n' in current_commit_summary:
        current_commit_summary = current_commit_summary.split('\n', 1)[0]

    # Make sure there are no newlines in the commit ID. We only want the ID itself and no weirdness around it.
    previous_commit_id = re.sub('\n', '', previous_commit_id)

    # If this isn't the source branch, compare it against the source branch and if it matches,
    # it's a new branch and therefore, doesn't need to run on these files. Exit if there's no difference.
    if details["test_only"] is True:
        checkBranchStatus = requests.get(details["source_github_api_repos"] + '/compare/' +
                                         details["source_github_branch"] + '...' + current_commit_id,
                                         auth=(details["username"], details["token"]))
        branchStatusJSON = checkBranchStatus.json()
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

    # Get the author's name
    listCommits = requests.get(details["source_github_api_repos"] + '/commits/' + current_commit_id + '?sha=' +
                               details["current_github_branch"], auth=(details["username"], details["token"]))
    commitsJSON = listCommits.json()
    current_commit_author = commitsJSON['commit']['author']['name']

    # If there aren't enough commits to compare against, run on every file.
    if len(commitsList) < 1:
        log.info('No files retrieved.')
        source_files_original_list = {}
    elif details["rebuild_all_files"] is True:
        log.info('Rebuilding all files.')
        source_files_original_list = {}
    else:

        # log.info('Getting a list of files that have changed since the last build ran.')
        # Get a list of files that have changed since the last build ran
        if details["test_only"] is True:
            # Compare the upstream branch with the current branch - this accumulates files that are changed from commit to commit
            compareDiffs = requests.get(details["source_github_api_repos"] + '/compare/' + details["source_github_branch"] +
                                        '...' + details["current_github_branch"], auth=(details["username"],
                                        details["token"]))
        else:
            # Compare the current ID with the previous ID
            compareDiffs = requests.get(details["source_github_api_repos"] + '/compare/' + previous_commit_id + '...' +
                                        current_commit_id + '?per_page=100', auth=(details["username"], details["token"]))

        try:
            # This workaround is needed when the last commit file contains a commit ID that is no longer in the repository.
            # Could happen when a commit history is blown away or if files are copied into a new repo
            if 'No common ancestor' in compareDiffs.text:
                try:
                    compareDiffs = requests.get(details["source_github_api_repos"] + '/compare/' +
                                                PREVIOUS_COMMIT_IDRetain + '...' + current_commit_id,
                                                auth=(details["username"], details["token"]))
                except Exception:
                    addToErrors('A diff between the two commit IDs could not be retrieved. ' +
                                'The problem might be with the previous commit ID: ' + PREVIOUS_COMMIT_IDRetain + '.',
                                'commits', '', details, log, 'pre-build', '', '')
                    exitBuild(details, log)
        except Exception as e:
            addToErrors('A diff between the two commit IDs could not be retrieved.\n' + str(e), 'commits', '', details, log, 'pre-build', '', '')
            exitBuild(details, log)

        try:
            compareDiffJSON = compareDiffs.json()
        except Exception:
            log.debug('No compareDiffJSON to display.')
            addToErrors('No JSON was returned to parse. Status code: ' + str(compareDiffs.status_code) +
                        '. The repo might not be accessible or the ' + details["source_github_domain"] +
                        ' domain might not be available at the moment.', 'commits', '', details, log, 'pre-build', '', '')
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
                addToErrors('The list of files in the commit could not be retrieved. If there is a ' +
                            details["last_commit_id_file"] + ' file, try deleting it and starting the build again.',
                            'commits', '', details, log, 'pre-build', '', '')
                exitBuild(details, log)

        fileCount = 0
        if filesJson == []:
            log.info('No files returned.')
            source_files_original_list = {}

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
                                                           filePatch, fileStatus, '/' + folderAndFile, source_files_original_list, [], [])

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
                                                       filePatch, fileStatus, '/' + folderAndFile, source_files_original_list, [], [])

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
                                filePatchBytes = subprocess.check_output('git diff ' + previous_commit_id + ' ' + current_commit_id +
                                                                         ' --patch ' + folderAndFile, shell=True)
                                filePatch = filePatchBytes.decode("utf-8")
                            else:
                                filePatch = ''

                            source_files_original_list = addToList('None', details, log, fileNamePrevious,
                                                                   filePatch, fileStatus, '/' + folderAndFile, source_files_original_list, [], [])

                addToWarnings('The commit included 300 or more files. ' +
                              'The Git API could not include the details for more than 300 files in a commit. ' +
                              'Information for the remaining files are being gathered from the CLI. ' +
                              'All of the files from the commit are being handled in this build, but deletions related ' +
                              'to file renames or removals might not happen as desired downstream on the files that ' +
                              'were over the first alphabetical 300.\n', 'commits', '', details, log, 'pre-build', '', '')

        # Summary of the information we got above
        log.info('Previous commit ID: ' + previous_commit_id)
        log.info('Current commit ID: ' + current_commit_id)
        log.info('Current commit description: ' + current_commit_summary + '\n')

        log.info('These were the files changed since the last commit that a build ran on:')
        for source_file, source_file_info in source_files_original_list.items():
            log.info(str(source_file) + str(' (' + source_files_original_list[source_file]['fileStatus'] + ')'))
        log.info('\n\n')

    return (current_commit_author, current_commit_id, current_commit_summary, previous_commit_id, source_files_original_list)
