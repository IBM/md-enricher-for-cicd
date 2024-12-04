def parseSubprocessOutput(subprocessOutput, log):
    result, error = subprocessOutput.communicate()
    exitCode = subprocessOutput.wait()
    if exitCode > 0:
        '''
        if not error == None:
            if(error.decode('ascii') == ""):
                error = result
            raise Exception("Code: " + str(exitCode) + " - Message: " + error.decode('ascii'))
        else:
            raise Exception("Code: " + str(exitCode))
        '''
        log.debug('Subprocess result: ' + str(exitCode))

    if result is not None:
        result = result.decode()
        if not result == '':
            # If branch protection or a push failure for other reasons happens
            # show that in the console, otherwise, include it in the logs
            if 'remote: error' in result:
                log.warning(result)
            else:
                log.debug(result)

    return (exitCode)
