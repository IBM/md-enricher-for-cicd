#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def flagCheck(details, log, allSourceFiles, filesForOtherLocations):

    # Check if all of the feature flags are used in the content

    # import json
    # import os

    from errorHandling.errorHandling import addToWarnings

    if not details["featureFlags"] == 'None':
        flagsNotUsed = []
        for featureFlag in details["featureFlags"]:
            featureFlagName = featureFlag["name"]
            if not featureFlagName == 'staging' and not featureFlagName == 'prod':
                found = False
                # First check all of the files used in the enabled builds
                for entry in allSourceFiles:
                    if (not details["featureFlagFile"] in entry) and (entry.endswith(tuple(details["filetypes"]))):
                        try:
                            fileContents = allSourceFiles[entry]['fileContents']
                            if ('<' + featureFlagName + '>') in fileContents:
                                log.debug('Confirmed feature flag ' + featureFlagName + ' usage in ' + entry + '.')
                                found = True
                                break
                        except Exception:
                            continue
                # If it's not found, try the files from builds that might not have been enabled
                if found is False:
                    for entry in filesForOtherLocations:
                        if (not details["featureFlagFile"] in entry) and (entry.endswith(tuple(details["filetypes"]))):
                            with open(details["source_dir"] + entry, 'r', encoding="utf8", errors="ignore") as checkFile:
                                fileContents = checkFile.read()
                                if ('<' + featureFlagName + '>') in fileContents:
                                    log.debug('Confirmed feature flag ' + featureFlagName + ' usage in ' + entry + '.')
                                    found = True
                                    break
                if found is False:
                    flagsNotUsed.append(featureFlagName)
                    log.debug('Feature flag ' + featureFlagName + ' was not used in any content files.')

        if len(flagsNotUsed) > 0:
            if len(flagsNotUsed) == 1:
                intro = 'This feature flag is'
            else:
                intro = 'These feature flags are'
            addToWarnings(intro + ' not used in any content files and can be removed: ' +
                          (", ".join(flagsNotUsed)), details["featureFlagFile"], '', details, log, 'post-build', '', '')
