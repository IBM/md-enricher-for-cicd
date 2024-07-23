#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def exitBuild(details, log):

    # Compile end of build info and post to Slack, if specified

    from datetime import datetime
    import os
    import re
    import sys
    import time
    from mdenricher.setup.postToSlack import postToSlack

    def instanceCleanup(details, itemList, log, logBranchCommit):
        # This section is to remove duplicate errors and warnings that are the same in different locations.
        # Condenses dupes so that there are fewer overall errors and easier scannability.
        itemListNoDupes = ''
        # if details["output_dir"] in itemList:
        # itemList = itemList.replace(details["output_dir"], '')
        try:
            if details["log_branch"] in itemList:
                itemList = itemList.replace('/edit/' + details["log_branch"] + '/', '/blame/' + logBranchCommit + '/')
            itemListSplits = itemList.split('\n\n')
            itemListSplits.sort()
            itemListSplits = list(filter(('').__ne__, itemListSplits))
            for itemListSplit in itemListSplits:
                if 'Output: ' in itemListSplit and '|>' in itemListSplit:
                    noOutputInstances = re.findall('Output: ' + '.*?' + '|>', itemListSplit)
                    for noOutputInstance in noOutputInstances:
                        itemListSplit = itemListSplit.replace(noOutputInstance, 'Output: None')
                if 'Stage: ' in itemListSplit:
                    errorWithoutLocation, errorLocation = itemListSplit.rsplit('Stage: ', 1)
                    if errorWithoutLocation in itemListNoDupes:
                        if not itemListNoDupes.endswith(errorLocation):
                            itemListNoDupes = itemListNoDupes + ', ' + errorLocation
                    else:
                        if itemListSplit not in itemListNoDupes:
                            itemListNoDupes = itemListNoDupes + '\n' + itemListSplit
                else:
                    if itemListSplit not in itemListNoDupes:
                        itemListNoDupes = itemListNoDupes + '\n' + itemListSplit
        except Exception:
            itemListNoDupes = itemList
        return (itemListNoDupes)

    if not details["builder"] == 'local':

        # Update the log file with the information from this build
        from mdenricher.repos.pushUpdatedLogFile import pushUpdatedLogFile
        logBranchCommit = pushUpdatedLogFile(details, log)
    else:
        logBranchCommit = ''

    log.info("\n\n\n")
    log.info("-------------------------------------------------------------")
    log.info("OVERALL BUILD STATUS")
    log.info("-------------------------------------------------------------")
    log.info("")

    log.debug('Build ended: ' + str(datetime.now(details["time_zone"])))
    try:
        endTime = time.time()
        hours, rem = divmod(endTime-details["time_start"], 3600)
        minutes, seconds = divmod(rem, 60)

        minutes = str(str(minutes).split('.')[0])
        if minutes == '1':
            minutesString = 'minute'
        else:
            minutesString = 'minutes'

        seconds = round(seconds)
        if seconds == 1:
            secondsString = 'second'
        else:
            secondsString = 'seconds'

        if minutes == '0':
            log.info("Completed in " + str(seconds) + " " + secondsString + ".")
        else:
            log.info("Completed in " + str(minutes) + " " + minutesString + " " + str(seconds) + " " + secondsString + ".")
    except Exception as e:
        log.info('Time could not be calculated.')
        log.debug(e)
    log.info("")

    errors = 0
    if os.path.exists(details["error_file"]):
        with open(details["error_file"], 'r', encoding="utf8", errors="ignore") as file_open:
            errorList = file_open.read()
            errorList = instanceCleanup(details, errorList, log, logBranchCommit)
            errors = errorList.count('ERROR:')
            errorLinks = re.findall('<http(.*?)>', errorList)
            errorListNoLinks = errorList
            for errorLink in errorLinks:
                try:
                    file_name = errorLink.split('|')[1]
                    errorListNoLinks = errorListNoLinks.replace('<http' + errorLink + '>', file_name)
                except Exception as e:
                    log.debug('Error link could not be replaced with a file name: ' + errorLink)
                    log.debug(e)
            log.info('TOTAL ERRORS: ' + str(errors))
    else:
        errorList = ''

    warnings = 0
    if os.path.exists(details["warning_file"]):
        with open(details["warning_file"], 'r', encoding="utf8", errors="ignore") as file_open:
            warningList = file_open.read()
            warningList = instanceCleanup(details, warningList, log, logBranchCommit)
            warnings = warningList.count('WARNING:')
            warningLinks = re.findall('<http(.*?)>', warningList)
            warningListNoLinks = warningList
            for warningLink in warningLinks:
                try:
                    file_name = warningLink.split('|')[1]
                    warningListNoLinks = warningListNoLinks.replace('<http' + warningLink + '>', file_name)
                except Exception as e:
                    log.debug('Warning link could not be replaced with a file name: ' + warningLink)
                    log.debug(e)

            log.info('TOTAL WARNINGS: ' + str(warnings))
    else:
        warningList = ''

    if details["builder"] == 'local':
        buildNumberPost = 'local build'
    else:
        buildNumberPost = 'build #' + str(details["build_number"])

    if warnings == 1:
        warningsString = 'warning'
    else:
        warningsString = 'warnings'

    if errors == 1:
        errorsString = 'error'
    else:
        errorsString = 'errors'

    if details["slack_show_author"] is True:
        try:
            current_commit_author = details["current_commit_author"]
            if details["current_commit_author"].endswith('s'):
                possessive = '\''
            else:
                possessive = '\'s'
        except Exception:
            current_commit_author = ''
            possessive = ''
    else:
        current_commit_author = ''
        possessive = ''

    # Making sure these variables have been specified so far - does this defeat the purpose of having details?

    try:
        current_github_branch = details["current_github_branch"] + ' branch '
    except Exception:
        current_github_branch = ''

    if details["builder"] == 'local':
        errorLocation = details["output_dir"]
        current_github_branch = ''
    else:

        try:
            source_github_org = details["source_github_org"]
        except Exception:
            source_github_org = 'Unknown Org'
        try:
            source_github_repo = details["source_github_repo"]
        except Exception:
            source_github_repo = 'Unknown Repo'

        errorLocation = source_github_org + '/' + source_github_repo

    # Output dir cleanup

    if os.path.exists(details["error_file"]):
        if 'None' in errorList or 'None' in warningList:
            if os.path.exists(details["warning_file"]):
                instanceList = errorListNoLinks + warningListNoLinks
            else:
                instanceList = errorListNoLinks
        else:
            if os.path.exists(details["warning_file"]):
                instanceList = errorList + warningList
            else:
                instanceList = errorList
        log.info(instanceList)

        payload = [{"color": "danger", "title_link": details["build_url"],
                    "title": current_commit_author + possessive + ' ' + current_github_branch +
                    buildNumberPost + " failed with " + str(errors) + " " + errorsString + ", " +
                    str(warnings) + " " + warningsString + " in " + errorLocation,
                    "text": instanceList}]
        postToSlack(log, details, payload)

        log.info('BUILD FAILED')
        log.info('\n\n')
        sys.exit(1)

    elif os.path.exists(details["warning_file"]):
        if 'None' in warningList:
            instanceList = warningListNoLinks
        else:
            instanceList = warningList
        log.info(instanceList)

        payload = [{"color": "warning", "title_link": details["build_url"],
                    "title": current_commit_author + possessive + ' ' + current_github_branch + buildNumberPost +
                    " passed with " + str(warnings) + " " + warningsString + " in " + errorLocation,
                    "text": instanceList}]
        postToSlack(log, details, payload)

        log.info('BUILD SUCCESSFUL WITH WARNINGS')
        log.info('\n\n')
        sys.exit(0)

    else:
        if (details["slack_post_success"] is True):

            payload = [{"color": "good", "title_link": details["build_url"],
                       "title": current_commit_author + possessive + ' ' + current_github_branch +
                        buildNumberPost + " passed"}]
            postToSlack(log, details, payload)

        log.info('BUILD SUCCESSFUL')
        log.info('\n\n')
        sys.exit(0)
