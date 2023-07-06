#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def pushUpdatedLogFile(details, log):

    # Push the log file to the logs branch in the source repo

    import os  # for running OS commands like changing directories or listing files in directory
    import shutil
    import subprocess
    import sys

    def checkout():
        log.info('Checking out branch: ' + details["log_branch"])
        os.chdir(details["output_dir"] + '/' + details["log_branch"])
        subprocess.call('git checkout -b ' + details["log_branch"] + ' --quiet', shell=True)
        log.info('Cleaning up unneeded files in the ' + details["source_github_branch"] + ' branch to become the ' + details["log_branch"] + ' branch.')

    def clone(branch):
        subprocess.call('git clone --depth 1 -b ' + branch + " https://" + details["username"] + ":" + details["token"] + '@' +
                        details["source_github_domain"] + '/' + details["source_github_org"] + '/' +
                        details["source_github_repo"] + ".git " + details["output_dir"] + '/' +
                        details["log_branch"] + ' --quiet', shell=True)
        log.info('Cloned the ' + branch + ' branch.')

    # from errorHandling.errorHandling import addToWarnings
    # from errorHandling.errorHandling import addToErrors
    # from setup.exitBuild import exitBuild
    from errorHandling.pushErrors import pushErrors

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
                clone(details["log_branch"])
                log.info('Cleaning up unneeded files in the ' + details["log_branch"] + ' branch.')
            except Exception:
                # Try cloning the source branch and then checking out the log branch
                clone(details["source_github_branch"])
                checkout()

            if os.path.isdir(details["output_dir"] + '/' + details["log_branch"]):
                os.chdir(details["output_dir"] + '/' + details["log_branch"])
            else:
                clone(details["source_github_branch"])
                checkout()
                if not os.path.isdir(details["output_dir"] + '/' + details["log_branch"]):
                    log.error('The ' + details["log_branch"] + ' directory does not exist. The ' + details["log_branch"] + ' branch could not be cloned.')
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
            for logFile in os.listdir(details["output_dir"]):
                if logFile.startswith(details["log_file_name"]):
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
                    else:
                        contains = ''

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
                    (not os.path.exists(details["error_file"]))):

                with open(details["output_dir"] + '/' + details["log_branch"] + '/' + details["last_commit_id_file"], "w+") as commitFileOpen:
                    commitFileOpen.write(details["current_commit_id"])
                try:
                    # If there is a JSON error in the locations file, the previous ID isn't set yet
                    log.info('Updating ' + details["last_commit_id_file"] + ': ' + details["previous_commit_id"] + ' -> ' + details["current_commit_id"] + '.')
                except Exception:
                    log.info('Updating ' + details["last_commit_id_file"] + ': ' + details["current_commit_id"] + '.')

            # Push up the log branch changes
            os.chdir(details["output_dir"] + '/' + details["log_branch"])
            subprocess.call('git add --all', shell=True)
            subprocess.call('git commit -m "[ci skip] Build #' + details["build_number"] + contains +
                            ' - ' + details["current_commit_summary"] + '" --quiet', shell=True)
            try:
                log.info('Pushing changed log files.')
                subprocess.call('git push  --quiet', shell=True, stdout=open(os.devnull, 'wb'))
            except Exception:
                subprocess.call('git pull', shell=True)
                try:
                    log.info('Setting upstream origin ' + details["log_branch"] + '.')
                    subprocess.call('git push --set-upstream origin ' + details["log_branch"] + '  --quiet', shell=True)
                    log.info('Completed upstream origin')
                except Exception as e:
                    pushErrors(details, e, log)
            try:
                logBranchCommitBytes = subprocess.check_output('git rev-parse origin/' + details["log_branch"], shell=True)
                logBranchCommit = logBranchCommitBytes.decode("utf-8")
                logBranchCommit = logBranchCommit.replace('\n', '')
                log.info('View the logs: https://' + details["source_github_domain"] + '/' + details["source_github_org"] +
                         '/' + details["source_github_repo"] + '/tree/' + logBranchCommit)
            except Exception:
                log.warning('Cannot get the last commit sha for the ' + details["log_branch"] + '.')
                logBranchCommit = ''

    except Exception:
        log.error('Log file could not be pushed to the logs branch.')
        logBranchCommit = ''
    return (logBranchCommit)
