#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def writeResult(self, details, file_name, folderAndFile, folderPath, topicContents, compareSitemapContents):

    # Write the revised contents to a file

    import os  # for running OS commands like changing directories or listing files in directory
    import re
    # import difflib as dl
    from mdenricher.cleanupEachFile.comments import comments
    from datetime import datetime

    def getTodaysDate():
        now = datetime.now()
        currentYear = str(now.year)
        currentMonth = str(now.month)
        currentDay = str(now.day)
        if len(currentMonth) == 1:
            currentMonth = '0' + currentMonth
        if len(currentDay) == 1:
            currentDay = '0' + currentDay
        return (currentYear, currentMonth, currentDay)

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
        if (folderAndFile in self.all_files_dict) or (folderAndFile == self.sitemap_file) or (self.sitemap_file.endswith(folderPath + file_name)):
            # sitemap is folderAndFile on first writing after handling the potential snippets or tags in it,
            # but then when the sitemap content is generated, the folderPath and file_name is used
            # Open the file for writing
            write = False

            if folderAndFile in details['rebuild_files_list']:
                write = True
            elif os.path.isfile(self.location_dir + folderPath + file_name):
                self.log.debug('Examining diff.')

                if ((folderAndFile == self.sitemap_file) or (self.sitemap_file.endswith(folderPath + file_name))) and (compareSitemapContents is True):
                    topicContentsDownstream = self.source_files[self.sitemap_file]['downstream_sitemap_contents']
                else:
                    with open(self.location_dir + folderPath + file_name, 'r', encoding="utf8", errors="ignore") as fileName_read:
                        topicContentsDownstream = fileName_read.read()

                if 'lastupdated: "' in topicContentsDownstream:
                    self.log.debug('Examining diff in IBM Cloud Docs content.')
                    topicContentsDownstreamMeat = topicContentsDownstream
                    topicContentsMeat = topicContents

                    # Make sure the last updated dates don't affect comparison
                    downstreamDateDownstream = re.findall('lastupdated: "(.*?)"', topicContentsDownstreamMeat)[0]
                    topicContentsDownstreamMeat = str(topicContentsDownstreamMeat).replace(str(downstreamDateDownstream), '', 1)

                    lastUpdatedDate = re.findall('lastupdated: "(.*?)"', topicContentsMeat)[0]
                    topicContentsMeat = topicContentsMeat.replace(lastUpdatedDate, '', 1)

                    # Make sure that the copyright years don't affect comparison
                    copyrightDateDownstream = re.findall('years: (.*?)\n', topicContentsDownstreamMeat)[0]
                    topicContentsDownstreamMeat = topicContentsDownstreamMeat.replace('years: ' + copyrightDateDownstream, '', 1)

                    copyrightDate = re.findall('years: (.*?)\n', topicContentsMeat)[0]
                    topicContentsMeat = topicContentsMeat.replace('years: ' + copyrightDate, '', 1)

                    if topicContentsDownstreamMeat == topicContentsMeat:
                        if ((folderAndFile == self.sitemap_file) or (self.sitemap_file.endswith(folderPath + file_name))) and (compareSitemapContents is True):
                            # Write the old version of the sitemap again and undo the writing of the sub file again
                            topicContents = topicContentsDownstream
                            write = True
                        else:
                            write = False
                    else:
                        write = True
                else:
                    if topicContentsDownstream == topicContents:
                        write = False
                    else:
                        write = True
            else:
                write = True

            if write is True:

                currentYear, currentMonth, currentDay = getTodaysDate()
                lastUpdatedDate = currentYear + '-' + currentMonth + '-' + currentDay

                if '[{LAST_UPDATED_DATE}]' in topicContents:
                    topicContents = topicContents.replace('[{LAST_UPDATED_DATE}]', lastUpdatedDate)
                    self.log.debug(r'Replaced [{LAST_UPDATED_DATE}] with current date: ' + lastUpdatedDate)
                if '[{CURRENT_YEAR}]' in topicContents:
                    topicContents = topicContents.replace('[{CURRENT_YEAR}]', lastUpdatedDate.split('-', 1)[0])
                    self.log.debug(r'Replaced [{CURRENT_YEAR}] with current year: ' + lastUpdatedDate.split('-', 1)[0])
                # For running markdown enricher on markdown enricher docs, don't replace the examples
                # First curly brace then square bracket
                if '{[<!--Do not transform-->' in topicContents:
                    topicContents = topicContents.replace('{[<!--Do not transform-->', '{[')
                # Second square bracket then curly brace
                if '[{<!--Do not transform-->' in topicContents:
                    topicContents = topicContents.replace('[{<!--Do not transform-->', '[{')
                with open(self.location_dir + folderPath + file_name, 'w+', encoding="utf8", errors="ignore") as fileName_write:
                    fileName_write.write(topicContents)
                    self.log.debug('Wrote: ' + self.location_dir + folderPath + file_name)
            else:
                self.log.debug('No changes found to write.')

        # Double-check that nothing is getting written that shouldn't
        else:
            if os.path.isfile(self.location_dir + folderAndFile):
                os.remove(self.location_dir + folderAndFile)
                self.log.debug('Deleted: ' + self.location_dir + folderAndFile)
            if os.path.isfile(self.location_dir + folderPath + file_name):
                os.remove(self.location_dir + folderPath + file_name)
                self.log.debug('Deleted: ' + self.location_dir + folderPath + file_name)
