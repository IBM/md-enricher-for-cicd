def postToSlack(log, details, payload, type):

    import json
    import os
    import requests
    from slack_sdk import WebClient
    from mdenricher.errorHandling.requestValidation import requestValidation
    log.info('\n\n')

    userID = None
    if (details["slack_user_mapping"] is not None) and (details["slack_bot_token"] is not None):
        # https://slack.dev/python-slack-sdk/web/index.html

        log.info('Getting Slack ID from user mapping.')

        if os.path.isfile(details["slack_user_mapping"]):
            try:
                with open(details["slack_user_mapping"], 'r', encoding="utf8", errors="ignore") as mapping_open:
                    mapping = json.load(mapping_open)
                    userList = mapping["user_mapping"]
                    for user in userList:
                        if user["github_name"] == details["current_commit_author"] or user["github_id"] == details["current_commit_author"]:
                            userID = user["slack_id"]
                            break
                    if userID is None:
                        log.info('Slack post is not ephemeral. The ID for the commit author ' + details["current_commit_author"] +
                                 ' does not exist in the user mapping file: ' +
                                 details["slack_user_mapping"])
            except Exception as e:
                log.debug(e)
                log.info('Slack post is not ephemeral.')
                log.debug('There was an issue parsing the user mapping file: ' + details["slack_user_mapping"])
        else:
            log.error('slack_user_mapping does not exist: ' + details["slack_user_mapping"])

    if ((details["slack_bot_token"] is not None) and (details["slack_channel"] is not None)):

        log.info('Posting results to Slack via bot token.')

        if ',' in details["slack_channel"]:
            slack_channel_details = details["slack_channel"].replace(' ', '')
            slack_channel_list = slack_channel_details.split(',')
        else:
            slack_channel_list = [details["slack_channel"]]

        for slack_channel in slack_channel_list:

            try:
                client = WebClient(token=details["slack_bot_token"])

                # Post ephemeral messages only when not running against the source branch
                # Slack issues warning if you don't include the text parameter
                if ((userID is not None) and
                        (not details["current_github_branch"] == details["source_github_branch"])):
                    log.info('Posting ephemeral message.')
                    response = client.chat_postEphemeral(
                        channel=slack_channel,
                        user=userID,
                        text='<@' + userID + '> Markdown enricher:',
                        attachments=payload
                    )
                elif type == 'errors':
                    log.info('Posting message to ' + slack_channel + ' mentioning members of the channel that are online (here).')
                    response = client.chat_postMessage(
                        channel=slack_channel,
                        text='<!here> Markdown enricher:',
                        attachments=payload
                    )
                else:
                    log.info('Posting message to ' + slack_channel + '.')
                    response = client.chat_postMessage(
                        channel=slack_channel,
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

        if ',' in details["slack_webhook"]:
            slack_channel_details = details["slack_webhook"].replace(' ', '')
            slack_channel_list = slack_channel_details.split(',')
        else:
            slack_channel_list = [details["slack_webhook"]]

        for slack_channel in slack_channel_list:
            try:
                requestResponse = requests.post(slack_channel, json.dumps({"attachments": payload}), headers={'content-type': 'application/json'})
                requestValidation(details, log, requestResponse, 'warning', 'The message could not be posted to Slack. Check that the webhook is valid.', False)
            except Exception as e:
                log.error('The message could not be posted to Slack.\n' + str(e))
    log.info('\n\n')
