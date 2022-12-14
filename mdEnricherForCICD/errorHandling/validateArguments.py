#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def validateArguments(details, log):

    import os
    import sys
    # from errorHandling.errorHandling import addToWarnings
    from errorHandling.errorHandling import addToErrors
    from setup.exitBuild import exitBuild

    # source_dir
    if not os.path.isdir(details["source_dir"]):
        addToErrors('The directory specified for the source_dir variable does not exist.' +
                    'Verify that the path is correct: --source_dir=' + details["source_dir"], '', 'validate', details, log,
                    'pre-build', '', '')
        exitBuild(details, log)

    # locations_file
    log.info('Validating the locations_file path and file name: %s', details["locations_file"])
    if not os.path.isfile(details["locations_file"]):
        addToErrors('The location file specified for the locations_file variable does not exist. ' +
                    'Verify that the path and file name are correct: --locations_file=' + details["locations_file"], '',
                    'validate', details, log, 'pre-build', '', '')
        sys.exit(1)

    # slack_webhook
    # if (details["slack_webhook"] is not None) and (not details["slack_webhook"].startswith('http')):
        # addToErrors('The slack_webhook must begin with http.', 'validate', details, log, 'pre-build')
        # exitBuild(details, log)
