#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def tagListCompile(self, details):

    # Create a list of tags to work with whether this is staging or prod and indicate what to do with them
    # Example:  tagList = ['tag':'show/hide']

    import json  # for sending data with and parsing data from requests
    import os  # for running OS commands like changing directories or listing files in directory

    from errorHandling.errorHandling import addToWarnings
    from errorHandling.errorHandling import addToErrors
    # from setup.exitBuild import exitBuild

    tags_show = []
    tags_hide = []

    # self.log.info('\n')
    # self.log.info('----------------------------------')
    # self.log.info('Tag list and display settings for ' + self.location_name + ':')
    # self.log.info('----------------------------------')

    for tag in self.all_tags:
        if ((tag == self.location_name) and (tag not in tags_show)):
            tags_show.append(tag)
        elif ((not tag == self.location_name) and (tag not in tags_hide) and (tag not in tags_show)):
            tags_hide.append(tag)
        else:
            self.log.debug('Already handled: ' + tag)

    tags_show.append('all')
    tags_hide.append('hidden')

    # Get the feature flags and replace them with staging/prod tags to be dealt with later in this script
    if os.path.isfile(details["source_dir"] + details["featureFlagFile"]):
        with open(details["source_dir"] + details["featureFlagFile"], 'r', encoding="utf8", errors="ignore") as featureFlagJson:
            try:
                featureFlags = json.load(featureFlagJson)
            except Exception as e:
                addToErrors('Information might not be formatted properly' + str(e), details["featureFlagFile"],
                            '', details, self.log, self.location_name, '', '')
            else:
                self.log.debug('Feature flag check for ' + self.location_name + ':')
                for featureFlag in featureFlags:
                    featureFlagName = featureFlag["name"]

                    if (featureFlagName in tags_show) or (featureFlagName in tags_hide):
                        addToErrors('Check for duplicate "' + featureFlagName + '" flags in the feature flag file.', details["featureFlagFile"],
                                    '', details, self.log, self.location_name, featureFlagName, str(featureFlags))

                    if ' ' in featureFlagName:
                        addToErrors('Feature flags cannot include spaces: ' + featureFlagName, details["featureFlagFile"],
                                    '', details, self.log, self.location_name, featureFlagName, str(featureFlags))
                    else:
                        def displayFound(featureFlagName, featureFlagDisplay):
                            self.log.debug('Location value for ' + featureFlagName + ': ' + featureFlagDisplay)

                        try:
                            featureFlagDisplay = featureFlag["location"]
                        except Exception as e:
                            addToWarnings('No location value for the ' + featureFlagName + ' feature flag to parse' +
                                          str(e), details["featureFlagFile"], '', details, self.log, self.location_name,
                                          featureFlagName, str(featureFlags))
                        else:
                            displayFound(featureFlagName, featureFlagDisplay)

                        try:
                            featureFlagDisplay
                        except Exception:
                            addToErrors('No location value for the ' + featureFlagName, details["featureFlagFile"], '',
                                        details, self.log, self.location_name, featureFlagName, str(featureFlags))
                        else:
                            if ',' in featureFlagDisplay:
                                featureFlagDisplayList = featureFlagDisplay.split(',')
                            else:
                                featureFlagDisplayList = [featureFlagDisplay]

                            for featureFlagDisplayEntry in featureFlagDisplayList:
                                if ((featureFlagDisplayEntry in tags_show) and (featureFlagName not in tags_show)):
                                    if featureFlagName not in tags_show:
                                        tags_show.append(featureFlagName)

                            for featureFlagDisplayEntry in featureFlagDisplayList:
                                if ((featureFlagDisplayEntry in tags_hide) and (featureFlagName not in tags_hide) and (featureFlagName not in tags_show)):
                                    if featureFlagName not in tags_hide:
                                        tags_hide.append(featureFlagName)

    else:
        self.log.debug('No feature flag to work with: ' + details["source_dir"] + details["featureFlagFile"])

    # If there's special handling for a folder, append that as a tag name
    for directory in self.location_contents_folders_keep:
        directory = directory.replace('/', '')
        if directory != 'None':
            if directory not in tags_show:
                tags_show.append(directory)

    for directory in self.location_contents_folders_remove:
        directory = directory.replace('/', '')
        if directory != 'None':
            if ((directory not in tags_hide) and (directory not in tags_show)):
                tags_hide.append(directory)

    TAGS_SHOW_STRING = ", ".join(sorted(tags_show))
    self.log.info('tags_show: ' + TAGS_SHOW_STRING)
    TAGS_HIDE_STRING = ", ".join(sorted(tags_hide))
    self.log.debug('tags_hide: ' + TAGS_HIDE_STRING)

    return (tags_hide, tags_show)
