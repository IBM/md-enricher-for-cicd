#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def writeResult(self, details, file_name, folderAndFile, folderPath, topicContents):

    # Write the revised contents to a file

    import os  # for running OS commands like changing directories or listing files in directory
    import re
    # import difflib as dl
    from mdenricher.cleanupEachFile.comments import comments
    from mdenricher.cleanupEachFile.getTodaysDate import getTodaysDate
    from mdenricher.errorHandling.errorHandling import addToWarnings

    # If the file doesn't have anything in it, don't write it or remove existing file unless it's a hidden file
    if ((topicContents == '') or ((topicContents.isspace()) is True)) and (not file_name.startswith('.')):
        if os.path.isfile(self.location_dir + folderPath + file_name):
            self.log.debug('No content to write to file in ' + self.location_name + '. Removing.')
            try:
                os.remove(self.location_dir + folderPath + file_name)
            except Exception as e:
                self.log.error(e)
        else:
            self.log.debug('No content to write to file in ' + self.location_name + '.')

    # Otherwise, write it
    else:
        topicContents = comments(self, details, folderAndFile, topicContents)
        if folderAndFile in self.all_files_dict:
            # Open the file for writing
            write = False

            currentFileLastUpdatedDate = None
            copyrightDate = None

            if folderAndFile in details['rebuild_files_list']:
                write = True
                self.log.debug('Rebuilding because the file is in the rebuild_files_list.')
            elif os.path.isfile(self.location_dir + folderPath + file_name):

                with open(self.location_dir + folderPath + file_name, 'r', encoding="utf8", errors="ignore") as fileName_read:
                    topicContentsDownstream = fileName_read.read()

                # Remove new lines from the end
                while topicContentsDownstream.endswith('\n'):
                    topicContentsDownstream = topicContentsDownstream[:-1]
                while topicContents.endswith('\n'):
                    topicContents = topicContents[:-1]

                if '[{LAST_UPDATED_DATE}]' not in topicContents and '[{CURRENT_YEAR}]' in topicContents:
                    self.log.debug('Always updating topics with copyright variable.')
                    write = True

                elif topicContentsDownstream == topicContents:
                    write = False
                    self.log.debug('No changes found to write.')

                elif '[{LAST_UPDATED_DATE}]' in topicContents or '[{CURRENT_YEAR}]' in topicContents:
                    topicContentsMeat = topicContents
                    topicContentsDownstreamMeat = topicContentsDownstream
                    if 'lastupdated:' in topicContentsMeat or 'years:' in topicContentsMeat:
                        self.log.debug('Examining diff in IBM Cloud Docs content.')

                        if 'lastupdated: "' in topicContentsMeat and 'lastupdated: "' in topicContentsDownstreamMeat:

                            # Make sure the last updated dates don't affect comparison
                            downstreamDateDownstream = re.findall('lastupdated: "(.*?)"', topicContentsDownstreamMeat)[0]
                            topicContentsDownstreamMeat = str(topicContentsDownstreamMeat).replace(str(downstreamDateDownstream), '', 1)
                            # self.log.debug('Downstream file date: ' + downstreamDateDownstream)

                            currentFileLastUpdatedDate = re.findall('lastupdated: "(.*?)"', topicContentsMeat)[0]
                            topicContentsMeat = topicContentsMeat.replace(currentFileLastUpdatedDate, '', 1)
                            # self.log.debug('Current file date: ' + currentFileLastUpdatedDate)
                        elif 'lastupdated:' in topicContentsMeat and 'lastupdated:' in topicContentsDownstreamMeat:
                            addToWarnings('The last updated date is not in the format: lastupdated: "[{LAST_UPDATED_DATE}]"',
                                          folderAndFile, folderPath + file_name, details, self.log, self.location_name, '', '')

                        if 'years: ' in topicContentsMeat and 'years: ' in topicContentsDownstreamMeat:

                            # Make sure that the copyright years don't affect comparison
                            copyrightDateDownstream = re.findall('years: (.*?)\n', topicContentsDownstreamMeat)[0]
                            topicContentsDownstreamMeat = topicContentsDownstreamMeat.replace('years: ' + copyrightDateDownstream, '', 1)

                            copyrightDate = re.findall('years: (.*?)\n', topicContentsMeat)[0]
                            topicContentsMeat = topicContentsMeat.replace('years: ' + copyrightDate, '', 1)

                        if topicContentsDownstreamMeat == topicContentsMeat:
                            write = False
                            self.log.debug('No changes found in IBM Cloud Docs file.')
                        else:
                            self.log.debug('Changes found in IBM Cloud Docs content.')
                            write = True

                            # Split on new lines
                            topicContentsDownstreamMeatLines = topicContentsDownstreamMeat.split('\n')
                            topicContentsMeatLines = topicContentsMeat.split('\n')

                            if len(topicContentsMeatLines) == len(topicContentsDownstreamMeatLines):
                                lineNumber = 0
                                for line in topicContentsMeatLines:
                                    if line != topicContentsDownstreamMeatLines[lineNumber]:
                                        self.log.debug('First changed line: "' + line[0:100] + '..."')
                                        break
                                    lineNumber = lineNumber + 1

                    else:
                        self.log.debug('Changes found. Date variables are used.')
                        write = True
                else:
                    self.log.debug('Changes found. No date variables used.')
                    write = True
            else:
                self.log.debug('Downstream file did not exist before.')
                write = True

            if write is True:

                if file_name.endswith('.md') and not topicContents.endswith('\n'):
                    topicContents = topicContents + '\n'

                currentYear, currentMonth, currentDay = getTodaysDate()
                lastUpdatedDate = currentYear + '-' + currentMonth + '-' + currentDay

                if '[{LAST_UPDATED_DATE}]' in topicContents:
                    topicContents = topicContents.replace('[{LAST_UPDATED_DATE}]', lastUpdatedDate)
                    self.log.debug(r'Replaced [{LAST_UPDATED_DATE}] with current date: ' + lastUpdatedDate)
                if '[{CURRENT_YEAR}]' in topicContents:
                    topicContents = topicContents.replace('[{CURRENT_YEAR}]', lastUpdatedDate.split('-', 1)[0])
                    self.log.debug(r'Replaced [{CURRENT_YEAR}] with current year: ' + lastUpdatedDate.split('-', 1)[0])

                # For running markdown enricher on markdown enricher docs, don't replace the examples
                if 'ME_ignore ' in topicContents:
                    topicContents = topicContents.replace('ME_ignore ', '')

                with open(self.location_dir + folderPath + file_name, 'w+', encoding="utf8", errors="ignore") as fileName_write:
                    fileName_write.write(topicContents)
                    self.log.debug('Wrote: ' + self.location_dir + folderPath + file_name)

        # Double-check that nothing is getting written that shouldn't
        else:
            if os.path.isfile(self.location_dir + folderAndFile):
                os.remove(self.location_dir + folderAndFile)
                self.log.debug('Deleted: ' + self.location_dir + folderAndFile)
            if os.path.isfile(self.location_dir + folderPath + file_name):
                os.remove(self.location_dir + folderPath + file_name)
                self.log.debug('Deleted: ' + self.location_dir + folderPath + file_name)
