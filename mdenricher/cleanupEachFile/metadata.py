#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def metadata(self, details, file_name, firstAnchor, folderAndFile, folderPath, topicContents):

    # Replace the metadata variables
    # Retrieve the dates from the previous version of the file, if possible, to get an accurate changed file list

    # import os
    # import re  # for doing finds within the topic content

    # Rather than us using our own metadata attributes list, we'll use the core team's. After everyone stops using this conref, remove this section.
    if '[{METADATA_ATTRIBUTES}]' in topicContents:
        topicContents = topicContents.replace('[{METADATA_ATTRIBUTES}]', '{{site.data.keyword.attribute-definition-list}}')
        self.log.debug(r'Replaced [{METADATA_ATTRIBUTES}] with {{site.data.keyword.attribute-definition-list}}.')

    # This is for Blockchain's version links at the beginning of each file
    if '{[FIRST_ANCHOR]}' in topicContents:
        topicContents = topicContents.replace('{[FIRST_ANCHOR]}', firstAnchor)
        self.log.debug(r'Replaced [{FIRST_ANCHOR}] with ' + firstAnchor + '.')

    # Get the year and date from the previous version of the file and re-insert it
    # If that file doesn't exist yet, don't replace these variables yet
    '''
    if ((os.path.isfile(self.location_dir + folderPath + file_name)) and (details["ibm_cloud_docs"] is True)):
        with open(self.location_dir + folderPath + file_name, 'r', encoding="utf8", errors="ignore") as fileName_open:
            locationTopicContents = fileName_open.read()

            # Get the date from the downstream file
            if 'lastupdated' in locationTopicContents:
                oldLastUpdatedFound = False
                if '"lastupdated": "' in locationTopicContents:
                    locationLastUpdatedDate = re.findall('"lastupdated": "(.*?)"', locationTopicContents)
                    oldLastUpdatedFound = True
                elif 'lastupdated: "' in locationTopicContents:
                    locationLastUpdatedDate = re.findall('lastupdated: "(.*?)"', locationTopicContents)
                    oldLastUpdatedFound = True
                if oldLastUpdatedFound is True:
                    try:
                        # Try inserting the downstream file date in place of the [{LAST_UPDATED_DATE}]
                        locationYear, locationMonth, locationDay = locationLastUpdatedDate[0].split('-')
                        if '[{LAST_UPDATED_DATE}]' in topicContents:
                            # Replace the variable with the downstream date
                            topicContents = topicContents.replace('[{LAST_UPDATED_DATE}]', locationYear + '-' +
                                                                  locationMonth + '-' + locationDay, 1)
                            self.log.debug(r'Replaced [{LAST_UPDATED_DATE}] with downstream date: ' + locationYear + '-' + locationMonth + '-' + locationDay)
                        # Try inserting the downstream file date in place of the date in the source file
                        else:
                            # Get the date from the upstream file
                            currentLastUpdatedDateFound = False
                            if '"lastupdated": "' in topicContents:
                                currentLastUpdatedDate = re.findall('"lastupdated": "(.*?)"', topicContents)
                                currentLastUpdatedDateFound = True
                            elif 'lastupdated: "' in topicContents:
                                currentLastUpdatedDate = re.findall('lastupdated: "(.*?)"', topicContents)
                                currentLastUpdatedDateFound = True
                            if currentLastUpdatedDateFound is True:
                                currentTopicsYear, currentTopicsMonth, currentTopicsDay = currentLastUpdatedDate[0].split('-')
                                # Replace the upstream date with the downstream date
                                topicContents = topicContents.replace(currentTopicsYear + '-' + currentTopicsMonth + '-' +
                                                                      currentTopicsDay, locationYear + '-' +
                                                                      locationMonth + '-' + locationDay, 1)
                                self.log.debug(r'Replaced upstream date with downstream date: '
                                               + currentTopicsYear + '-' + currentTopicsMonth + '-' + currentTopicsDay)

                    except Exception as e:
                        self.log.debug('The date in the previous file could not be parsed.')
                        self.log.debug(e)

            if 'years: ' in locationTopicContents:
                locationCopyrightList = re.findall('years: (.*?)\n', locationTopicContents)
                # years: 2014, 2022
                locationCopyright = (locationCopyrightList[0]).replace('\n', '')
                if ', ' in locationCopyright:
                    locationCopyright = locationCopyright.split(', ')[1]
                if '[{CURRENT_YEAR}]' in topicContents:
                    topicContents = topicContents.replace('[{CURRENT_YEAR}]', locationCopyright, 1)
                    self.log.debug('Replaced [{CURRENT_YEAR}] with downstream copyright year: ' + locationCopyright)
                else:
                    try:
                        upstreamCopyrightList = re.findall('years: (.*?)\n', topicContents)
                        upstreamCopyright = (upstreamCopyrightList[0]).replace('\n', '')
                        if ', ' in upstreamCopyright:
                            upstreamCopyright = upstreamCopyright.split(', ')[1]
                        topicContents = topicContents.replace(upstreamCopyright, locationCopyright, 1)
                        self.log.debug('Replaced ' + upstreamCopyright + ' with downstream copyright year: ' +
                                       locationCopyright)
                    except Exception as e:
                        self.log.debug('The copyright date could not be replaced yet: ' + str(e))
    '''
    return (topicContents)
