#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def sourceFilesForThisBranch(self, details):

    # This section refines the list of files, puts them in the right directory to be committed later,
    # and calls another function to clean up the tagging in each file, if necessary

    from mdenricher.sourceFileList.addToList import addToList
    # import json
    import os  # for running OS commands like changing directories or listing files in directory
    # import re

    # from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.setup.exitBuild import exitBuild

    # Tweak the source file list depending on where stuff is running and where
    # self.log.debug('\n\n')
    # self.log.debug('----------------------------------')
    # self.log.debug('Source file list for ' + self.location_name + ':')
    # self.log.debug('----------------------------------')

    source_files = self.source_files_location_list.copy()

    conrefChangeList = []
    potentialSitemapImpact = False

    self.log.debug('Rebuilding the source file list for ' + self.location_name + '.')

    # Adding selected rebuild_files
    if not details["rebuild_files_list"] == []:
        for rebuild_file in details["rebuild_files_list"]:
            if os.path.isfile(details["source_dir"] + rebuild_file):
                self.log.debug('Adding ' + rebuild_file)
                source_files = addToList(self, details, self.log, '', '', 'rebuild',
                                         rebuild_file, source_files, self.location_contents_files,
                                         self.location_contents_folders, self.remove_all_other_files_folders)
            else:
                addToErrors('File specfied with --rebuild_files does not exist in the upstream source: ' +
                            details["source_dir"] + rebuild_file, rebuild_file, rebuild_file,
                            details, self.log, self.location_name, '', '')

    for source_file, source_file_info in list(source_files.items()):

        folderAndFile = source_files[source_file]['folderAndFile']
        file_name = source_files[source_file]['file_name']
        fileStatus = source_files[source_file]['fileStatus']
        filePatch = source_files[source_file]['filePatch']
        fileNamePrevious = source_files[source_file]['fileNamePrevious']

        if source_files[source_file]['locationHandling'] == 'remove':
            self.location_build_first.append(source_file)

        # Create a location-specific list of files to iterate over
        # If there is a heading changed, sitemap rebuild always, release notes for IBM Cloud, always add the sitemap to the source file list
        if not self.sitemap_file == 'None':
            if self.sitemap_file not in self.location_build_last:
                self.location_build_last.append(self.sitemap_file)
            if (((details["ibm_cloud_docs_sitemap_rebuild_always"] is True) or
                 ((self.location_ibm_cloud_docs is True) and
                  (potentialSitemapImpact is False) and
                  (('# ' in filePatch) or
                   ('toc.yaml' in folderAndFile) or
                   (('release' in folderAndFile) and
                    ('notes' in folderAndFile))))) and (self.remove_all_other_files_folders is False)):

                if os.path.isfile(details["source_dir"] + self.sitemap_file):
                    if self.sitemap_file not in source_files:
                        self.log.debug('Adding ' + self.sitemap_file)
                        source_files = addToList(self, details, self.log, self.sitemap_file, 'None',
                                                 'rebuild', self.sitemap_file, source_files, self.location_contents_files, self.location_contents_folders,
                                                 self.remove_all_other_files_folders)
                else:
                    self.log.debug('File does not exist: ' + details["source_dir"] + self.sitemap_file)

        if (details["reuse_snippets_folder"] in folderAndFile) and (str(details["reuse_phrases_file"]) in folderAndFile) and (details["builder"] != 'local'):
            while '+' in filePatch:
                try:
                    filePatch = filePatch.split('@@', 2)[2]
                except Exception:
                    self.log.debug('Not enough @@ to split. Trying + instead.')
                    # self.log.debug(filePatch)
                try:
                    filePatch = filePatch.split('+', 1)[1]
                except Exception:
                    self.log.debug('Not enough + to split:')
                    self.log.debug(filePatch)
                if '{[' in filePatch:
                    filePatch = filePatch.split('{[', 1)[1]
                    conrefID, filePatch = filePatch.split(']}', 1)
                    self.log.debug('Conref ID found in patch: ' + conrefID)
                    conrefChangeList.append(conrefID)
            if source_file in source_files and details['unprocessed'] is False:
                del source_files[source_file]
                self.log.debug(source_file + ': Skipping phrases content reuse file')

        elif details["reuse_snippets_folder"] + '/' in folderAndFile:
            if details["builder"] != 'local':
                try:
                    conrefMDFilename = folderAndFile.split(details["reuse_snippets_folder"] + '/', 1)[1]
                    conrefChangeList.append(conrefMDFilename)
                except Exception as e:
                    self.log.debug('Failed to parse: ' + folderAndFile)
                    self.log.debug(e)
            if source_file in source_files and details['unprocessed'] is False:
                del source_files[source_file]
                self.log.debug(source_file + ": Skipping content reuse files")

        # Adding all images to verify that they are used somewhere
        elif ((file_name.endswith(tuple(details["img_output_filetypes"])))):
            source_files = addToList(self, details, self.log, fileNamePrevious, filePatch, fileStatus,
                                     folderAndFile, source_files, self.location_contents_files,
                                     self.location_contents_folders, self.remove_all_other_files_folders)

        elif (file_name == '.build.yaml' and
              details['ibm_cloud_docs'] is True):
            self.location_build_first.append(folderAndFile)
            source_files = addToList(self, details, self.log, fileNamePrevious, filePatch, fileStatus,
                                     folderAndFile, source_files, self.location_contents_files,
                                     self.location_contents_folders, self.remove_all_other_files_folders)

        elif (file_name == 'keyref.yaml' and
              details['ibm_cloud_docs'] is True):
            self.location_build_first.append(folderAndFile)
            source_files = addToList(self, details, self.log, fileNamePrevious, filePatch, fileStatus,
                                     folderAndFile, source_files, self.location_contents_files,
                                     self.location_contents_folders, self.remove_all_other_files_folders)

        # Adding landing.json to update date automatically
        elif (file_name == 'landing.json' and
              details['ibm_cloud_docs'] is True):
            try:
                if '[{LAST_UPDATED_DATE}]' in self.all_files_dict[folderAndFile]['fileContents']:
                    source_files = addToList(self, details, self.log, fileNamePrevious, filePatch, fileStatus,
                                             folderAndFile, source_files, self.location_contents_files,
                                             self.location_contents_folders, self.remove_all_other_files_folders)
            except Exception:
                pass

        elif (details["featureFlagFile"] == folderAndFile):
            source_files = addToList(self, details, self.log, fileNamePrevious, filePatch, fileStatus,
                                     folderAndFile, source_files, self.location_contents_files,
                                     self.location_contents_folders, self.remove_all_other_files_folders)

            # If the toc.yaml file was updated, see if any other markdown files use those IDs also need to be updated
            """
            elif ('toc.yaml' in folderAndFile) and (details['ibm_cloud_docs'] is True):

                source_files = addToList(self, details, self.log, fileNamePrevious, filePatch, fileStatus,
                                        folderAndFile, source_files, self.location_contents_files,
                                        self.location_contents_folders, self.remove_all_other_files_folders)

                if details['unprocessed'] is False:
                    toc_diff = source_files[folderAndFile]['filePatch']
                    tocLines = toc_diff.split('\n')
                    for toc_line in tocLines:
                        while toc_line.endswith(' '):
                            toc_line = toc_line[:-1]
                        if '<' in toc_line:
                            tagsInLine = re.findall('<.*?>', toc_line)
                            for tagInLine in tagsInLine:
                                toc_line = toc_line.replace(tagInLine, '')
                        if toc_line.endswith(tuple(details["filetypes"])) and (toc_line.startswith('-') or toc_line.startswith('+')):
                            while toc_line.startswith(' ') or toc_line.startswith('-') or toc_line.startswith('+'):
                                toc_line = toc_line[1:]
                            if os.path.isfile(details["source_dir"] + '/' + toc_line):
                                modifiedFile = '/' + toc_line
                                fileStatus = 'Modified tag in toc file affects this file.'
                                source_files = addToList(self, details, self.log, 'None', 'None',
                                                        fileStatus, modifiedFile, source_files,
                                                        self.location_contents_files,
                                                        self.location_contents_folders,
                                                        self.remove_all_other_files_folders)

            # If the feature-flags.json file was updated, see if any other markdown files use those IDs also need to be updated
            elif (details["featureFlagFile"] in folderAndFile) and (os.path.isfile(details["source_dir"] + details["featureFlagFile"])):

                if ((details['unprocessed'] is True) and (details["featureFlagFile"] in folderAndFile)):
                    if source_file in source_files:
                        del source_files[source_file]
                        self.log.debug(source_file + ': Skipping feature flags file')
                elif (details["builder"] == 'local'):
                    if source_file in source_files:
                        del source_files[source_file]
                        self.log.debug(source_file + ': Skipping feature flags file')
                else:
                    source_files = addToList(self, details, self.log, fileNamePrevious, filePatch, fileStatus,
                                            folderAndFile, source_files, self.location_contents_files,
                                            self.location_contents_folders, self.remove_all_other_files_folders)
                    featureFlagList = []
                    featureFlagsChangedList = []
                    featureFlag_diff = source_files[folderAndFile]['filePatch']
                    self.log.debug('Feature flag diff:')
                    self.log.debug(featureFlag_diff)

                    # Verify that every feature flag has a location and gather then into a list.
                    # Also use this list to see later if a feature flag was removed.
                    if not details["featureFlags"] == 'None':
                        for featureFlag in details["featureFlags"]:
                            featureFlagName = featureFlag["name"]

                            def displayFound(featureFlagName, featureFlagDisplay):
                                self.log.debug('Display value for ' + featureFlagName + ': ' + featureFlagDisplay)

                            try:
                                featureFlagDisplay = featureFlag["location"]
                            except Exception:
                                addToWarnings('No location value for the ' + featureFlagName + ' feature flag to parse.',
                                            details["featureFlagFile"], '', details, self.log, self.location_name,
                                            featureFlagName, str(details["featureFlags"]))
                            else:
                                displayFound(featureFlagName, featureFlagDisplay)
                                featureFlagList.append(featureFlagName + ':' + featureFlagDisplay)

                        # Split the diff into sections so it can figure out which ones were changed, to know which ones to search other files for
                        if '},' in featureFlag_diff:
                            featureFlagDiffSections = featureFlag_diff.split('},')
                        else:
                            featureFlagDiffSections = [featureFlag_diff]

                        # Gather a list of changed feature flags
                        featureInFileText = ''
                        for section in featureFlagDiffSections:
                            if (('"name":' in section) and ('"location":' in section)):
                                featureFlagDiffList = section.split('\n')
                                for line in featureFlagDiffList:
                                    if (('location' in line) and ('+' in line)):
                                        featureFlagLocation = line.split('"')[3]
                                        featureFlagsChangedList.append(featureFlagName + ':' + featureFlagLocation)
                                    elif 'name' in line:
                                        featureFlagName = line.split('"')[3]
                                        # If there are some feature flags in the content that should have been removed
                                        # because they are no longer in the JSON file, post to Slack.
                                        if featureFlagName not in str(featureFlagList):
                                            # Lines that start with - indicate that the feature flag has been removed from the JSON file
                                            if line.startswith('-'):
                                                for ALL_FILES_LISTEntry in self.all_files_dict:
                                                    if os.path.isfile(details["source_dir"] + '/' + ALL_FILES_LISTEntry):
                                                        fileName_open = open(details["source_dir"] + '/' +
                                                                            ALL_FILES_LISTEntry, 'r', encoding="utf8",
                                                                            errors="ignore")
                                                        featureFlagTextCheck = fileName_open.read()
                                                        fileName_open.close
                                                        if ((('<' + featureFlagName + '>' in featureFlagTextCheck) or
                                                                ('</' + featureFlagName + '>' in featureFlagTextCheck)) and
                                                                (featureFlagName not in self.tags_hide) and
                                                                (featureFlagName not in self.tags_show)):
                                                            addToErrors('The ' + featureFlagName + ' tag was removed from ' +
                                                                        'the feature flag file but is still used in ' +
                                                                        ALL_FILES_LISTEntry + '.', details["featureFlagFile"], '',
                                                                        details, self.log, self.location_name, featureFlagName + '>', featureFlagTextCheck)
                                                            featureInFileText = (featureInFileText + featureFlagName +
                                                                                ": <https://" +
                                                                                details["source_github_domain"] + '/' +
                                                                                details["source_github_org"] + '/' +
                                                                                details["source_github_repo"] + '/' +
                                                                                "/edit/master/" + ALL_FILES_LISTEntry + "|"
                                                                                + ALL_FILES_LISTEntry + ">\n")

                    # Go through all of the source files and see if any removed feature flags are still used in there.
                    self.log.debug('featureFlagsChangedList: ' + str(featureFlagsChangedList))
                    for ALL_FILES_LISTEntry in self.all_files_dict:
                        if os.path.isfile(details["source_dir"] + ALL_FILES_LISTEntry):
                            fileName_open = open(details["source_dir"] + ALL_FILES_LISTEntry, 'r', encoding="utf8", errors="ignore")
                            featureFlagTextCheck = fileName_open.read()
                            fileName_open.close
                            for featureFlag in featureFlagsChangedList:
                                featureFlagID, featureFlagDisplay = featureFlag.split(':')
                                if ('<' + str(featureFlagID) + '>') in featureFlagTextCheck:
                                    self.log.debug('This file contains the feature flag ' + featureFlagID + ': ' + ALL_FILES_LISTEntry)
                                    if ALL_FILES_LISTEntry not in str(source_files):
                                        modifiedFile = ALL_FILES_LISTEntry
                                        fileStatus = 'Modified feature flag used in this file'
                                        source_files = addToList(self, details, self.log, 'None', 'None',
                                                                fileStatus, modifiedFile, source_files,
                                                                self.location_contents_files,
                                                                self.location_contents_folders,
                                                                self.remove_all_other_files_folders)
            """
        # Remove travis.yml and gitignore files
        elif (('.travis.yml' in source_file) or
              ('.gitignore' in source_file) or
              ('.DS_Store' in source_file) or
              ('/.git' in source_file) or
              (str(details["locations_file"].rsplit('/', 1)[1]) in source_file) or
              ('.pre-commit-config.yaml' in source_file)):
            if source_file in source_files:
                del source_files[source_file]
                # self.log.debug(source_file + ': Skipping build files')

        # Remove files with unsupported filetypes
        elif not source_file.endswith(tuple(details["filetypes"])):
            if source_file in source_files:
                del source_files[source_file]

        # If the file is included in the list for this location, add it.
        elif source_file in self.all_files_dict and not details['featureFlagFile'] in folderAndFile:
            # self.log.debug(source_file + ' is in all_files_dict')
            if source_file not in source_files:
                self.log.debug(source_file + ' is not in source_files')
                source_files = addToList(self, details, self.log, fileNamePrevious, filePatch, fileStatus,
                                         folderAndFile, source_files, self.location_contents_files,
                                         self.location_contents_folders, self.remove_all_other_files_folders)

    # 2 If a conref file was updated, see if any other markdown files use that conref that also need to be updated
    # self.log.debug(str(source_files))
    if not conrefChangeList == []:
        self.log.debug('Content reuse included: ' + str(conrefChangeList))

        for conrefID in conrefChangeList:
            for ALL_FILES_LISTEntry in self.all_files_dict:
                if ';;' in ALL_FILES_LISTEntry:
                    ALL_FILES_LISTEntrySplit = ALL_FILES_LISTEntry.split(';;', 1)[0]
                else:
                    ALL_FILES_LISTEntrySplit = ALL_FILES_LISTEntry
                if ((os.path.isfile(details["source_dir"] + ALL_FILES_LISTEntrySplit)) and (ALL_FILES_LISTEntrySplit.endswith(tuple(details["filetypes"])))):
                    try:
                        fileName_open = open(details["source_dir"] + ALL_FILES_LISTEntrySplit, 'r', encoding="utf8")
                    except Exception:
                        fileName_open = open(details["source_dir"] + ALL_FILES_LISTEntrySplit, 'r')
                    try:
                        conrefTextCheck = fileName_open.read()
                    except Exception:
                        continue
                    else:
                        fileName_open.close()
                        if ('{[' + str(conrefID) + ']}') in conrefTextCheck:
                            self.log.debug('The value for {[' + conrefID + ']} changed in ' + ALL_FILES_LISTEntrySplit + '.')
                            if (not ('\'folderAndFile\': \'' + ALL_FILES_LISTEntrySplit + '\'') in str(source_files)):
                                if ((self.remove_all_other_files_folders is False) or
                                    ((self.remove_all_other_files_folders is True) and
                                     (ALL_FILES_LISTEntrySplit in str(self.location_contents_files)))):
                                    fileStatus = 'Modified conref is used in this file'
                                    source_files = addToList(self, details, self.log, 'None', 'None', fileStatus,
                                                             ALL_FILES_LISTEntrySplit, source_files,
                                                             self.location_contents_files,
                                                             self.location_contents_folders,
                                                             self.remove_all_other_files_folders)
                                    self.log.debug('Added ' + ALL_FILES_LISTEntrySplit + ' because it uses {[' + str(conrefID) + ']}.')
                                    if details["reuse_snippets_folder"] in ALL_FILES_LISTEntrySplit:
                                        conrefFileNameToAdd = ALL_FILES_LISTEntrySplit.split(details["reuse_snippets_folder"] + '/')[1]
                                        conrefChangeList.append(conrefFileNameToAdd)

    self.log.debug('')
    self.log.debug('Revised source file list for ' + self.location_name + ':')
    for source_file, source_file_info in sorted(source_files.items()):
        self.log.debug(source_file)

    return (self.location_build_first, self.location_build_last, source_files)
