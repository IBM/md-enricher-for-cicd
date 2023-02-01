#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def exitBuild(details, log):

    # Compile end of build info and post to Slack, if specified

    from datetime import datetime
    import json
    import os
    import re
    import requests
    import sys
    import time
    from slack_sdk import WebClient
    # from slack_sdk.errors import SlackApiError

    def postToSlack(payload):
        log.info('\n\n')

        userID = None
        if details["slack_user_mapping"] is not None:
            # https://slack.dev/python-slack-sdk/web/index.html

            log.info('Getting Slack ID from user mapping.')

            if os.path.isfile(details["slack_user_mapping"]):
                try:
                    with open(details["slack_user_mapping"], 'r', encoding="utf8", errors="ignore") as mapping_open:
                        mapping = json.load(mapping_open)
                        userList = mapping["user_mapping"]
                        for user in userList:
                            if user["github_name"] == details["current_commit_author"]:
                                userID = user["slack_id"]
                                break
                        if userID is None:
                            log.error('The ID for the commit author ' + details["current_commit_author"] +
                                      ' does not exist in the user mapping file: ' +
                                      details["slack_user_mapping"])
                except Exception as e:
                    log.error(e)
                    log.error('The ID for the commit author does not exist in the user mapping file: ' + details["slack_user_mapping"])
            else:
                log.error('slack_user_mapping does not exist: ' + details["slack_user_mapping"])

        if ((details["slack_bot_token"] is not None) and (details["slack_channel"] is not None)):

            log.info('Posting results to Slack via bot token.')

            try:
                client = WebClient(token=details["slack_bot_token"])

                # Post ephemeral messages only when not running against the source branch
                # Slack issues warning if you don't include the text parameter
                if ((userID is not None) and
                        (not details["current_github_branch"] == details["source_github_branch"])):
                    log.info('Posting ephemeral message.')
                    response = client.chat_postEphemeral(
                        channel=details["slack_channel"],
                        user=userID,
                        text='<@' + userID + '> Markdown enricher:',
                        attachments=payload
                    )
                else:
                    log.info('Posting message.')
                    response = client.chat_postMessage(
                        channel=details["slack_channel"],
                        text='Markdown enricher:',
                        attachments=payload
                    )
                if not response.status_code == 200:
                    log.error('The message could not be posted to Slack. ' +
                              'Check that the Slack bot token and the channel ID are valid. Error code: ' +
                              str(response.status_code))
            except Exception as e:
                # You will get a SlackApiError if "ok" is False
                log.error(e)    # str like 'invalid_auth', 'channel_not_found'

        elif details["slack_webhook"] is not None:

            log.info('Posting results to Slack via incoming webhook.')

            try:
                requestResponse = requests.post(details["slack_webhook"], json.dumps({"attachments": payload}), headers={'content-type': 'application/json'})
                if not requestResponse.status_code == 200:
                    log.error('The message could not be posted to Slack. Check that the webhook is valid. Error code: ' + str(requestResponse.status_code))
            except Exception as e:
                log.error('The message could not be posted to Slack.' + str(e))

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
        from repos.pushUpdatedLogFile import pushUpdatedLogFile
        logBranchCommit = pushUpdatedLogFile(details, log)
    else:
        logBranchCommit = ''

    log.info("\n\n\n")
    log.info("-------------------------------------------------------------")
    log.info("TIME TO RUN")
    log.info("-------------------------------------------------------------")

    log.info('Build ended: ' + str(datetime.now(details["time_zone"])))
    try:
        endTime = time.time()
        hours, rem = divmod(endTime-details["time_start"], 3600)
        minutes, seconds = divmod(rem, 60)
        log.info("Took {:0>2} minutes {:05.2f} seconds to complete.".format(int(minutes), seconds))
    except Exception as e:
        log.info('Time could not be calculated.')
        log.debug(e)

    log.info("\n\n\n")
    log.info("-------------------------------------------------------------")
    log.info("OVERALL BUILD STATUS")
    log.info("-------------------------------------------------------------")
    log.info("\n")

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
        build_url = details["build_url"]
    except Exception:
        build_url = ''
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

        payload = [{"color": "danger", "title_link": build_url,
                    "title": current_commit_author + possessive + ' ' + current_github_branch +
                    buildNumberPost + " failed with " + str(errors) + " " + errorsString + ", " +
                    str(warnings) + " " + warningsString + " in " + errorLocation,
                    "text": instanceList}]
        postToSlack(payload)

        log.info('BUILD FAILED')
        log.info('\n\n')
        sys.exit(1)

    elif os.path.exists(details["warning_file"]):
        if 'None' in warningList:
            instanceList = warningListNoLinks
        else:
            instanceList = warningList
        log.info(instanceList)

        payload = [{"color": "warning", "title_link": build_url,
                    "title": current_commit_author + possessive + ' ' + current_github_branch + buildNumberPost +
                    " passed with " + str(warnings) + " " + warningsString + " in " + errorLocation,
                    "text": instanceList}]
        postToSlack(payload)

        log.info('BUILD SUCCESSFUL WITH WARNINGS')
        log.info('\n\n')
        # sys.exit(0)

    else:
        if (details["slack_post_success"] is True):

            payload = [{"color": "good", "title_link": build_url,
                       "title": current_commit_author + possessive + ' ' + current_github_branch +
                        buildNumberPost + " passed"}]
            postToSlack(payload)

        log.info('BUILD SUCCESSFUL')
        log.info('\n\n')
        # sys.exit(0)
