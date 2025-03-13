def requestValidation(details, log, response, error_type, error_description, exitableIssue):

    from mdenricher.errorHandling.errorHandling import addToErrors
    from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.setup.exitBuild import exitBuild

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
