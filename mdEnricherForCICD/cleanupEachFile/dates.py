#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def dates(self, details, source_files):

    # Update the values for the LAST_UPDATED_DATE and COPYRIGHT_YEAR variables

    from cleanupEachFile.comments import comments
    from datetime import datetime
    import os
    import re
    import subprocess

    # When the location content is cloned originally, i.e. not a local build, and the marked-it frontmatter is used,
    # the dates will always update whether you use the LAST_UPDATED_DATE and COPYRIGHT_YEAR variables or not.
    # https://ibm.github.io/marked-it/#/yaml-frontmatter

    self.log.debug('Checking all dates')

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
            topicContents = topicContents.replace('[{CURRENT_YEAR}]', currentYear, 1)
            # self.log.debug(r'Replaced [{CURRENT_YEAR}] with current year: ' + currentYear)
        return (topicContents)

    # try:
    # If the downstream repo was cloned, there should be a .git directory, then get the date from the existing file
    if os.path.isdir(self.location_dir + '/.git'):

        os.chdir(self.location_dir)
        subprocess.call('git add -n --all', shell=True, stdout=open(os.devnull, 'wb'))
        status_bytes = subprocess.check_output('git status --short', shell=True)
        status = status_bytes.decode("utf-8")
        if not status == '':
            if '\n' in status:
                fileList = status.split('\n')
            else:
                fileList = [status]
            if '' in fileList:
                fileList.remove("")
            if not fileList == []:
                self.log.debug('Updating lastupdated date in the following changed files:')
                for file in fileList:
                    filename = file.rsplit(' ', 1)[1]
                    self.log.debug(filename)
                    if (os.path.isfile(self.location_dir + '/' + filename)) and (filename.endswith(tuple(details["filetypes"]))):
                        with open(self.location_dir + '/' + filename, 'r', encoding="utf8", errors="ignore") as fileName_open:
                            topicContents = fileName_open.read()
                        topicContents = comments(self, details, '/' + filename, topicContents)
                        if '[{LAST_UPDATED_DATE}]' in topicContents or '[{CURRENT_YEAR}]' in topicContents:
                            topicContents = useTodaysDate(topicContents)
                        elif 'years: ' in topicContents or 'lastupdated: ' in topicContents:
                            locationCopyrightList = re.findall('years: (.*?)\n', topicContents)
                            # years: 2014, 2022
                            locationCopyright = (locationCopyrightList[0]).replace('\n', '')
                            currentYear, currentMonth, currentDay = getTodaysDate()
                            if locationCopyright.endswith(currentYear):
                                self.log.debug('Copyright year is current: ' + currentYear)
                            else:
                                locationCopyrightNew = locationCopyright[:-4]
                                locationCopyrightNew = locationCopyrightNew + currentYear
                                topicContents = topicContents.replace('years: ' + locationCopyright, 'years: ' + locationCopyrightNew, 1)
                                self.log.debug('Replaced: ' + locationCopyright + ' with ' + locationCopyrightNew)
                            if 'lastupdated: "' + currentYear + '-' + currentMonth + '-' + currentDay + '"' in topicContents:
                                self.log.debug('Last updated date is current: ' + currentYear + '-' + currentMonth + '-' + currentDay)
                            else:
                                locationLastUpdatedDate = re.findall('lastupdated: "(.*?)"', topicContents)
                                topicContents = topicContents.replace('lastupdated: "' + locationLastUpdatedDate[0] + '"',
                                                                      'lastupdated: "' + currentYear + '-' +
                                                                      currentMonth + '-' + currentDay + '"')
                                self.log.debug('Replaced: lastupdated: "' + locationLastUpdatedDate[0] + '" with ' +
                                               'lastupdated: "' + currentYear + '-' + currentMonth + '-' + currentDay +
                                               '"')
                        else:
                            self.log.debug('No dates to replace.')
                        # For running markdown enricher on markdown enricher docs, don't replace the examples
                        # First curly brace then square bracket
                        if '{[<!--Do not transform-->' in topicContents:
                            topicContents = topicContents.replace('{[<!--Do not transform-->', '{[')
                        # Second square bracket then curly brace
                        if '[{<!--Do not transform-->' in topicContents:
                            topicContents = topicContents.replace('[{<!--Do not transform-->', '[{')
                        with open(self.location_dir + '/' + filename, 'w+', encoding="utf8", errors="ignore") as fileName_open:
                            self.log.debug('Writing file: ' + self.location_dir + '/' + filename)
                            fileName_open.write(topicContents)
                    else:
                        self.log.debug('Not updating ' + filename)

    else:
        # Update the date in every file
        sortedList = sorted(source_files.items())
        source_files = dict(sortedList)
        for source_file, source_file_info in source_files.items():

            file_name = source_files[source_file]['file_name']
            folderPath = source_files[source_file]['folderPath']
            if (os.path.isfile(self.location_dir + folderPath + file_name)) and (file_name.endswith(tuple(details["filetypes"]))):
                with open(self.location_dir + folderPath + file_name, 'r', encoding="utf8", errors="ignore") as fileName_open:
                    topicContents = fileName_open.read()
                    topicContents = comments(self, details, folderPath + file_name, topicContents)
                    if '[{LAST_UPDATED_DATE}]' in topicContents or '[{CURRENT_YEAR}]' in topicContents:
                        topicContents = useTodaysDate(topicContents)

                    # For running markdown enricher on markdown enricher docs, don't replace the examples
                    if '{[<!--Do not transform-->' in topicContents:
                        topicContents = topicContents.replace('{[<!--Do not transform-->', '{[')
                    if '[{<!--Do not transform-->' in topicContents:
                        topicContents = topicContents.replace('[{<!--Do not transform-->', '[{')

                    with open(self.location_dir + folderPath + file_name, 'w+', encoding="utf8", errors="ignore") as fileName_open:
                        fileName_open.write(topicContents)
                        self.log.debug('Updated dates in: ' + folderPath + file_name)
            else:
                self.log.debug('Not updating ' + file_name)

    # except Exception as e:
    # self.log.debug(str(e))
