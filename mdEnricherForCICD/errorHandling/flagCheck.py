#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def flagCheck(details, log):

    import json
    import os

    from errorHandling.errorHandling import addToWarnings

    if os.path.isfile(details["source_dir"] + details["featureFlagFile"]):

        # Get the list of conrefs that were used across all of the builds
        if os.path.isfile(details["flagUsageFile"]):
            # Get the used conref list
            with open(details["flagUsageFile"], 'r', encoding="utf8", errors="ignore") as flagUsageFileOpen:
                usedFlagsText = flagUsageFileOpen.read()
                usedFlags = usedFlagsText.split(',')

            # Open the feature flags file and get all of those defined
            flagList = []
            with open(details["source_dir"] + details["featureFlagFile"], 'r', encoding="utf8", errors="ignore") as featureFlagJson:
                featureFlags = json.load(featureFlagJson)
                for featureFlag in featureFlags:
                    featureFlagName = featureFlag["name"]
                    flagList.append(featureFlagName)

            # Compare the two lists
            unusedFlags = []
            for flag in flagList:
                if flag not in usedFlags:
                    if (not flag == 'prod') and (not flag == 'staging'):
                        unusedFlags.append(flag)
            if len(unusedFlags) > 0:
                if len(unusedFlags) == 1:
                    intro = 'This feature flag is'
                else:
                    intro = 'These feature flags are'
                addToWarnings(intro + ' not used in any content files and can be removed: ' +
                              (", ".join(unusedFlags)), details["featureFlagFile"], '', details, log, 'pre-build', '', '')
