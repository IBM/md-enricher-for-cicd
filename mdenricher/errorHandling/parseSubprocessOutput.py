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
        log.debug(exitCode)

    if result is not None:
        result = result.decode()
        if not result == '':
            log.debug(result)

    return (exitCode)
