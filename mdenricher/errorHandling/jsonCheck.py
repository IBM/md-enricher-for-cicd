#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def jsonCheck(details, log, ISSUE_WARNINGS, json_files_list, location_dir):

    # Verify the JSON syntax in valid in md-enricher files and content files

    import json  # for sending data with and parsing data from requests
    import os  # for running OS commands like changing directories or listing files in directory

    from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.errorHandling.errorHandling import addToErrors
    from mdenricher.setup.exitBuild import exitBuild

    if not json_files_list == []:

        # Conditional log
        if ISSUE_WARNINGS == 'False':
            log.debug('Validating markdown enricher JSON files.')

        # First time this is run, only run it on the files needed for the markdown enricher to run.
        # Next time through, run it on all other JSON files found.
        # This allows tagging to be used and cleaned up before validating for accurate JSON.

        for jsonFile in json_files_list:

            # Run on the reuse_phrases_file first time through before the build
            if ISSUE_WARNINGS == 'False':
                # Open the json file and read it
                if os.path.isfile(details["source_dir"] + str(jsonFile)):
                    with open(details["source_dir"] + jsonFile, 'r', encoding="utf8", errors="ignore") as jsonFileVar:
                        try:
                            json.load(jsonFileVar)
                            log.debug('JSON validated: ' + jsonFile)
                        except Exception as e:
                            log.error(e)
                            addToErrors('JSON not formatted properly. ' + str(e), jsonFile, '', details, log, 'pre-build', '', '')
                            exitBuild(details, log)

            # Run on everything else after the build to verify if the tags were handled properly
            else:
                if os.path.isfile(location_dir + str(jsonFile)):
                    with open(location_dir + jsonFile, 'r', encoding="utf8", errors="ignore") as jsonFileVar:
                        try:
                            json.load(jsonFileVar)
                            log.debug('JSON validated: ' + jsonFile)
                        except Exception as e:
                            log.error(e)
                            addToWarnings('JSON not formatted properly. ' + str(e), jsonFile, '', details, log, 'post-build', '', '')
