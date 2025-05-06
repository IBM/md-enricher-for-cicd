def requestValidation(details, log, call, request_type, payload, error_type, error_description, exitableIssue, streamValue, call_description):

    from mdenricher.errorHandling.errorHandling import addToErrors
    from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.setup.exitBuild import exitBuild

    import json
    import requests
    import time

    exitCode = 1
    attempt = 1

    if 'git' in call:

        while attempt < 4 and not str(exitCode).startswith('2'):

            if request_type == 'get':
                response = requests.get(call, auth=(details["username"], details["token"]),
                                        stream=streamValue)

            elif request_type == 'post':
                response = requests.post(call, auth=(details["username"], details["token"]),
                                         data=json.dumps(payload), stream=streamValue)

            elif request_type == 'patch':
                response = requests.patch(call, auth=(details["username"], details["token"]),
                                          data=json.dumps(payload), stream=streamValue)

            exitCode = int(response.status_code)

            log.debug(call_description + ': ' + str(response.status_code) + ' (Attempt #' + str(attempt) + ')')
            attempt = attempt + 1

            if not str(exitCode).startswith('2') and attempt < 3:
                log.debug('Waiting 5 seconds before trying again.')
                time.sleep(5)

        if not str(exitCode).startswith('2'):
            error_description = error_description + ' Github or the repo is not accessible. Try again later.'

    else:
        if request_type == 'get':
            response = requests.get(call, stream=streamValue)

        elif request_type == 'post':
            response = requests.post(call, data=json.dumps(payload), headers={'content-type': 'application/json'}, stream=streamValue)

        elif request_type == 'patch':
            response = requests.patch(call, data=json.dumps(payload), stream=streamValue)

        log.debug(call_description + str(response.status_code))

    if not str(response.status_code).startswith('2'):

        if error_type == 'warning':
            errorLog = log.warning
            addToWarnings(error_description, '', '', details, log, 'request', '', '')
        else:
            errorLog = log.error
            addToErrors(error_description, '', '', details, log, 'request', '', '')

        log.debug('Debug: ', exc_info=True)
        errorLog('Status code: ' + str(response.status_code))

        if response.status_code == 401:
            errorLog('Authentication issue.')

        if 'github' in response.url:
            errorLog('Github might not be accessible.')

        if exitableIssue is True:
            exitBuild(details, log)

    return (response)
