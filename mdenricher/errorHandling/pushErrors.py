#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def pushErrors(details, e, log):

    # When pushing content downstream or log files to the log branch, handle these Git push errors

    from mdenricher.errorHandling.errorHandling import addToErrors
    from mdenricher.setup.exitBuild import exitBuild

    if (('remote: Permission to' in str(e)) and ('denied' in str(e))):
        addToErrors('Permission denied. The changes could not be pushed to the repo. ' +
                    'Verify that the user had admin permissions for the repo.\n' + str(e), 'push', '', details,
                    log, 'post-build', '', '')
    elif 'Protected branch update failed' in str(e):
        addToErrors('This location is configured to merge-automatically, but the changes could not be pushed. ' +
                    'Check that the user has correct permissions to push to the repo. ' +
                    'If permissions are correct, check the branch settings. If branch protection ' +
                    'is enabled for this branch, remove branch protection or change the location_output_action ' +
                    'to create-pr.\n' + str(e), 'push', '', details, log, 'post-build', '', '')
    elif 'remote: detect-secrets-stream' in str(e):
        addToErrors('The automated secret detection is preventing these commits from being pushed ' +
                    'to the repo. Most likely, something that is not a secret is being ' +
                    'interpreted as a secret.\n' + str(e), 'push', '', details, log, 'post-build', '', '')
    else:
        addToErrors('The changes could not be pushed to the repo. ' + str(e), 'push', '', details, log, 'post-build', '', '')
    exitBuild(details, log)
