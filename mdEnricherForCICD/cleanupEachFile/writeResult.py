#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def writeResult(self, details, file_name, folderAndFile, folderPath, topicContents):

    # Write the revised contents to a file

    import os  # for running OS commands like changing directories or listing files in directory
    import difflib as dl
    from cleanupEachFile.comments import comments
    from datetime import datetime

    def examineDiff():
        with open(self.location_dir + folderPath + file_name, 'r', encoding="utf8", errors="ignore") as fileName_write:
            topicContentsOriginal = fileName_write.read()
        topicContentsLines = topicContents.splitlines()
        topicContentsOriginalLines = topicContentsOriginal.splitlines()

        diffCount = 0
        dateCount = 0
        # Look for diffs that do not include comments or only empty lines
        for diff in dl.context_diff(topicContentsOriginalLines, topicContentsLines):
            # ('<!--' not in diff) and ('-->' not in diff)
            # Removed this because Registry had comments in the file being edited
            if (diff.startswith('! ')) or (diff.startswith('+ ')) or (diff.startswith('- ')):
                diffCount = diffCount + 1
                if ('[{LAST_UPDATED_DATE}]' in diff) or ('[{CURRENT_YEAR}]' in diff) or ('lastupdated:' in diff) or ('  years:' in diff):
                    dateCount = dateCount + 1

        if (diffCount - dateCount) > 0:
            write = True
        else:
            write = False

        return (write)

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

    def useTodaysDate(topicContents):
        currentYear, currentMonth, currentDay = getTodaysDate()
        if '[{LAST_UPDATED_DATE}]' in topicContents:
            topicContents = topicContents.replace('[{LAST_UPDATED_DATE}]', currentYear + '-' + currentMonth + '-' + currentDay)
            # self.log.debug(r'Replaced [{LAST_UPDATED_DATE}] with current date: ' + currentYear + '-' + currentMonth + '-' + currentDay)
        if '[{CURRENT_YEAR}]' in topicContents:
            topicContents = topicContents.replace('[{CURRENT_YEAR}]', currentYear)
            # self.log.debug(r'Replaced [{CURRENT_YEAR}] with current year: ' + currentYear)
        return (topicContents)

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
            if ((folderAndFile == self.sitemap_file) or (self.sitemap_file.endswith(folderPath + file_name))):
                with open(details["source_dir"] + folderAndFile, 'r', encoding="utf8", errors="ignore") as fileName_write:
                    topicContentsSource = fileName_write.read()
                topicContentsLines = topicContents.splitlines()
                topicContentsSourceLines = topicContentsSource.splitlines()
                if (topicContentsLines > topicContentsSourceLines) and os.path.isfile(self.location_dir + folderPath + file_name):
                    write = examineDiff()
                else:
                    write = True
            elif ((('[{LAST_UPDATED_DATE}]' in topicContents) or
                   ('[{CURRENT_YEAR}]' in topicContents)) and
                  os.path.isfile(self.location_dir + folderPath + file_name)):
                write = examineDiff()
            else:
                write = True
            if write is True:
                topicContents = useTodaysDate(topicContents)
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
        # Double-check that nothing is getting written that shouldn't
        else:
            if os.path.isfile(self.location_dir + folderAndFile):
                os.remove(self.location_dir + folderAndFile)
                self.log.debug('Deleted: ' + self.location_dir + folderAndFile)
            if os.path.isfile(self.location_dir + folderPath + file_name):
                os.remove(self.location_dir + folderPath + file_name)
                self.log.debug('Deleted: ' + self.location_dir + folderPath + file_name)
