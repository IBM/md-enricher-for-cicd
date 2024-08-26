#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def pushUpdatedLogFile(details, log):

    # Push the log file to the logs branch in the source repo

    import os  # for running OS commands like changing directories or listing files in directory
    import shutil
    import subprocess
    from subprocess import PIPE, STDOUT
    import sys

    from mdenricher.errorHandling.errorHandling import addToErrors
    from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.errorHandling.parseSubprocessOutput import parseSubprocessOutput

    def checkout():
        log.info('Checking out branch: ' + details["log_branch"])
        os.chdir(details["output_dir"] + '/' + details["log_branch"])
        subprocessOutput = subprocess.Popen('git checkout -b ' + details["log_branch"] + ' --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
        exitCode = parseSubprocessOutput(subprocessOutput, log)
        if exitCode > 0:
            addToErrors('The logs branch could not be checked out.', 'logs', '', details, log, 'post-build', '', '')
        else:
            log.info('Cleaning up unneeded files in the ' + details["source_github_branch"] + ' branch to become the ' + details["log_branch"] + ' branch.')

    def clone(branch):
        subprocessOutput = subprocess.Popen('git clone --depth 1 -b ' + branch + " https://" + details["token"] + '@' +
                                            details["source_github_domain"] + '/' + details["source_github_org"] + '/' +
                                            details["source_github_repo"] + ".git " + details["output_dir"] + '/' +
                                            details["log_branch"] + ' --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
        exitCode = parseSubprocessOutput(subprocessOutput, log)
        if exitCode > 0:
            log.info('The ' + branch + ' branch could not be cloned.')
        else:
            log.info('Cloned the ' + branch + ' branch.')
        return (exitCode)

    # from mdenricher.errorHandling.errorHandling import addToWarnings
    # from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.setup.exitBuild import exitBuild
    from mdenricher.errorHandling.pushErrors import pushErrors

    logBranchCommit = ''

    try:
        if (not details["builder"] == 'local') and (not details["source_github_branch"] == 'None') and (details["log_branch"] is not None):

            log.info("\n\n\n")
            log.info("-------------------------------------------------------------")
            log.info("Updating the log files in " + details["log_branch"])
            log.info("-------------------------------------------------------------")

            if os.path.isdir(details["output_dir"] + '/' + details["log_branch"]):
                shutil.rmtree(details["output_dir"] + '/' + details["log_branch"])

            # Clone the branch
            try:
                # Try cloning the log branch
                exitCode = clone(details["log_branch"])
            except Exception:
                # Try cloning the source branch and then checking out the log branch
                try:
                    exitCode = clone(details["source_github_branch"])
                    if exitCode == 0:
                        checkout()
                except Exception:
                    exitCode = 1

            if exitCode == 0:
                os.chdir(details["output_dir"] + '/' + details["log_branch"])
            else:
                try:
                    exitCode = clone(details["source_github_branch"])
                    if exitCode == 0:
                        checkout()
                except Exception:
                    exitCode = 1

            if not os.path.isdir(details["output_dir"] + '/' + details["log_branch"]) or exitCode > 1:
                log.error('No branches could be cloned or checked out to push log information too. ' +
                          'Check permissions for ' + details["username"] + ' in the upstream source repository.')
                sys.exit(1)

            # Remove all files in the logs branch
            for fileOrFolder in os.listdir(details["output_dir"] + '/' + details["log_branch"]):
                if os.path.isdir(fileOrFolder):
                    if not ((details["output_dir"] + '/' + details["log_branch"] + '/' + fileOrFolder) ==
                            (details["output_dir"] + '/' + details["log_branch"] + '/.git')):
                        shutil.rmtree(details["output_dir"] + '/' + details["log_branch"] + '/' + fileOrFolder)
                elif os.path.isfile(fileOrFolder):
                    if not details["last_commit_id_file"] in fileOrFolder:
                        os.remove(details["output_dir"] + '/' + details["log_branch"] + '/' + fileOrFolder)

            # Check each file to verify that the GHE_TOKEN and Slack token are not written into the file
            contains = ''
            for logFile in os.listdir(details["output_dir"]):
                if '.log' in logFile and logFile.startswith(details["log_file_name"].rsplit('.')[0], 1):
                    log.debug('Checking contents of ' + logFile + ' for sensitive information.')
                    fileName_open = open(details["output_dir"] + '/' + logFile, 'r')
                    fileContents = fileName_open.read()
                    fileName_open.close

                    if details["token"] in fileContents:
                        fileContents = fileContents.replace(details["token"], '*****')

                    if details["slack_webhook"] is not None:
                        if details["slack_webhook"] in fileContents:
                            fileContents = fileContents.replace(details["slack_webhook"], '*****')

                    fileName_open = open(details["output_dir"] + '/' + logFile, 'w')
                    fileName_open.write(fileContents)
                    fileName_open.close

                    if 'CRITICAL' in fileContents:
                        contains = ' contains CRITICAL ERRORS'
                    elif 'ERROR' in fileContents:
                        contains = ' contains ERRORS'
                    elif 'WARN' in fileContents:
                        contains = ' contains warnings'

            # Copy each log file to the log branch directory
            for fileOrFolder in sorted(os.listdir(details["output_dir"])):
                if os.path.isdir(details["output_dir"] + '/' + fileOrFolder):
                    if not (details["output_dir"] + '/' + fileOrFolder) == (details["output_dir"] + '/' + details["log_branch"]):
                        if not (details["output_dir"] + '/' + fileOrFolder) == (details["output_dir"] + '/.git'):
                            shutil.copytree(details["output_dir"] + '/' + fileOrFolder,
                                            details["output_dir"] + '/' + details["log_branch"] + '/' + fileOrFolder)
                            if os.path.isdir(details["output_dir"] + '/' + details["log_branch"] + '/' + fileOrFolder + '/.git'):
                                shutil.rmtree(details["output_dir"] + '/' + details["log_branch"] + '/' + fileOrFolder + '/.git')
                            if os.path.isfile(details["output_dir"] + '/' + details["log_branch"] + '/' + fileOrFolder + '/.gitignore'):
                                os.remove(details["output_dir"] + '/' + details["log_branch"] + '/' + fileOrFolder + '/.gitignore')
                            log.debug('Copying ' + details["output_dir"] + '/' + fileOrFolder + ' to ' +
                                      details["output_dir"] + '/' + details["log_branch"] + '/' + fileOrFolder)
                elif os.path.isfile(details["output_dir"] + '/' + fileOrFolder):
                    shutil.copyfile(details["output_dir"] + '/' + fileOrFolder, details["output_dir"] + '/' + details["log_branch"] + '/' + fileOrFolder)

            # UPDATE THE COMMIT ID FILE
            if ((not details["builder"] == 'local') and
                    (not details["test_only"] is True) and
                    ((str(details['build_number']) == '1' and os.path.exists(details["error_file"])) or
                     (not os.path.exists(details["error_file"])))):

                # Read the previous version of the file and set the contents to a max number of lines
                maxLines = 5
                commitFilePrior = ''
                if os.path.isfile(details["output_dir"] + '/' + details["log_branch"] + '/' + details["last_commit_id_file"]):
                    with open(details["output_dir"] + '/' + details["log_branch"] + '/' + details["last_commit_id_file"], "r") as commitFileOpen:
                        commitFilePrior = commitFileOpen.read()
                        commitFilePriorList = commitFilePrior.split('\n')
                        commitFileLength = len(commitFilePriorList)
                        if commitFileLength > maxLines:
                            commitFilePrior = '\n'.join(commitFilePriorList[0:maxLines])
                        if not commitFilePrior.startswith('\n'):
                            commitFilePrior = '\n' + commitFilePrior

                # Don't write the details again if this is a restart
                if '\n' + str(details["build_number"]) + ':' in commitFilePrior:
                    log.info('Commit information already stored in ' + details["last_commit_id_file"])

                # Write the old and new details
                else:
                    with open(details["output_dir"] + '/' + details["log_branch"] + '/' + details["last_commit_id_file"], "w+") as commitFileOpen:
                        if details["build_number"] is None:
                            commitFileOpen.write('\n' + details["previous_commit_id"] + ',' +
                                                 details["current_commit_id"] + commitFilePrior)
                        elif str(details["build_number"]) == '1':
                            commitFileOpen.write('\n' + str(details["build_number"]) + ':' + details["current_commit_id"] + ',' +
                                                 details["current_commit_id"] + commitFilePrior)
                        else:
                            commitFileOpen.write('\n' + str(details["build_number"]) + ':' + details["previous_commit_id"] + ',' +
                                                 details["current_commit_id"] + commitFilePrior)

                    try:
                        # If there is a JSON error in the locations file, the previous ID isn't set yet
                        log.info('Updating ' + details["last_commit_id_file"] + ': ' +
                                 details["previous_commit_id"] + ' -> ' + details["current_commit_id"] + '.')
                    except Exception:
                        log.info('Updating ' + details["last_commit_id_file"] + ': ' + details["current_commit_id"] + '.')

            # Push up the log branch changes
            os.chdir(details["output_dir"] + '/' + details["log_branch"])
            subprocessOutput = subprocess.Popen('git add --all', shell=True, stdout=PIPE, stderr=STDOUT)
            exitCode = parseSubprocessOutput(subprocessOutput, log)
            gitCommitCommand = 'git commit -m "'
            if details["builder"] == 'travis':
                gitCommitCommand = gitCommitCommand + '[ci skip]'
            if not details["build_number"] is None:
                gitCommitCommand = gitCommitCommand + ' Build ' + details["build_number"]
            try:
                subprocessOutput = subprocess.Popen(gitCommitCommand + contains +
                                                    ' - ' + details["current_commit_summary"] + '" --quiet', shell=True,
                                                    stdout=PIPE, stderr=STDOUT)
                exitCode = parseSubprocessOutput(subprocessOutput, log)
            except Exception:
                pass
            try:
                log.info('Pushing changed log files.')
                subprocessOutput = subprocess.Popen('git push  --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                exitCode = parseSubprocessOutput(subprocessOutput, log)
            except Exception:
                subprocessOutput = subprocess.Popen('git pull', shell=True, stdout=PIPE, stderr=STDOUT)
                exitCode = parseSubprocessOutput(subprocessOutput, log)
                subprocessOutput = subprocess.Popen('git push  --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                exitCode = parseSubprocessOutput(subprocessOutput, log)
            if exitCode > 0:
                try:
                    log.info('Setting upstream origin ' + details["log_branch"] + '.')
                    subprocessOutput = subprocess.Popen('git push --set-upstream origin ' + details["log_branch"] +
                                                        ' --quiet', shell=True, stdout=PIPE, stderr=STDOUT)
                    exitCode = parseSubprocessOutput(subprocessOutput, log)
                    log.info('Completed upstream origin.')
                except Exception as e:
                    pushErrors(details, e, log)
            if exitCode > 0:
                addToWarnings('The log files could not be pushed to the repo.', 'logs', '', details, log, 'post-build', '', '')
                logBranchCommit = ''
            else:

                try:
                    logBranchCommitBytes = subprocess.check_output('git rev-parse origin/' +
                                                                   details["log_branch"], shell=True)
                    logBranchCommit = logBranchCommitBytes.decode("utf-8")
                    logBranchCommit = logBranchCommit.replace('\n', '')
                    log.info('View the logs: https://' + details["source_github_domain"] + '/' + details["source_github_org"] +
                             '/' + details["source_github_repo"] + '/tree/' + logBranchCommit)
                except Exception:
                    log.info('View the logs: https://' + details["source_github_domain"] + '/' + details["source_github_org"] +
                             '/' + details["source_github_repo"] + '/tree/' + details["log_branch"])

    except Exception as e:
        log.error('Log file could not be pushed to the logs branch.')
        log.error(e)
    return (logBranchCommit)
