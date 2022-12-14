#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def cleanupEachFile(self, details, location_github_branch_push, source_files, tags_hide, tags_show):

    # Loop through every file in the source_files dictionary and do the tag and conref replacements and whatever

    import json
    import os  # for running OS commands like changing directories or listing files in directory
    import re

    from errorHandling.errorHandling import addToWarnings
    from errorHandling.errorHandling import addToErrors
    # from setup.exitBuild import exitBuild

    def fileCleanUpLoop(self, details, allFlagsUsed, allInLinePhrasesUsed, allSnippetsUsed, conrefJSON, file_name,
                        fileNamePrevious, fileStatus, folderAndFile, folderPath, tags_hide, tags_show):

        # Open the source file for reading and get its contents
        with open(details["source_dir"] + folderAndFile, 'r', encoding="utf8", errors="ignore") as fileName_open:
            topicContents = fileName_open.read()

        # Get first topic ID
        try:
            allAnchors = re.findall('{: #(.*)}', topicContents)
            firstAnchor = allAnchors[0]
            # self.log.debug('First anchor: ' + firstAnchor)
        except Exception:
            # self.log.debug('No anchors in the page.')
            firstAnchor = '{[FIRST_ANCHOR]}'

        # Replace all of the conrefs in this file
        if os.path.isdir(details["source_dir"] + '/' + details["reuse_snippets_folder"] + '/'):
            # Replace the conref files first
            if '.md]}' in topicContents:
                # If they exist, replace all of the .md conrefs in the conref file
                from conrefs.wholeFileConrefs import wholeFileConrefs
                allSnippetsUsed, topicContents = wholeFileConrefs(self, details, allSnippetsUsed, file_name, folderAndFile, folderPath, topicContents)
                if not allSnippetsUsed == []:
                    self.log.debug('Snippets used:')
                    self.log.debug(sorted(allSnippetsUsed))
            # Replace the conref phrases
            if not str(details["reuse_phrases_file"]) in file_name:
                # Don't look for conref phrases in the conref phrases file or else it will replace the IDs that we need!!!
                if ((']}' in topicContents) or ('{[' in topicContents)):
                    from conrefs.inlineConrefs import inlineConrefs
                    allInLinePhrasesUsed, topicContents = inlineConrefs(self, details, allInLinePhrasesUsed, conrefJSON,
                                                                        file_name, folderAndFile, folderPath, topicContents)
                    if not allInLinePhrasesUsed == []:
                        self.log.debug('Phrases used:')
                        self.log.debug(sorted(allInLinePhrasesUsed))
                else:
                    self.log.debug('No inline snippets to handle.')

        if (('{{' in topicContents) and (details["ibm_cloud_docs_product_name_check"] is True)):
            from errorHandling.productConrefCheck import productConrefCheck
            productConrefCheck(self, details, file_name, folderAndFile, folderPath, topicContents)

        # from tags.tagCheck import tagCheck
        # allFlagsUsed = tagCheck(self, details, allFlagsUsed, file_name, folderAndFile, folderPath, tags_hide, tags_show, topicContents)
        # if not allInLinePhrasesUsed == []:
            # self.log.debug('Flags used:')
            # self.log.debug(allFlagsUsed)

        from tags.tagRemoval import tagRemoval
        allFlagsUsed, topicContents = tagRemoval(self, details, allFlagsUsed, folderAndFile, folderPath, file_name, tags_hide, tags_show, topicContents)
        if not allFlagsUsed == []:
            self.log.debug('Flags used:')
            self.log.debug(sorted(allFlagsUsed))

        if '```\n    ```' in topicContents:
            # Tested 1/6/21
            addToErrors('Empty codeblock. This issue will fail the markdown processor and prevent this file and any ' +
                        'file after it from being handled by the markdown processor. Verify that the removal of tags in ' +
                        'the codeblock aren\'t leaving behind the empty codeblock.', folderAndFile, folderPath + file_name, details, self.log,
                        self.location_name, '```\n    ```', topicContents)

        # if details["ibm_cloud_docs"] is True:
        from images.imagesCheckRelativePaths import imagesCheckRelativePaths
        topicContents = imagesCheckRelativePaths(self, details, file_name, folderAndFile, folderPath, topicContents)

        from cleanupEachFile.metadata import metadata
        topicContents = metadata(self, details, file_name, firstAnchor, folderAndFile, folderPath, topicContents)

        from cleanupEachFile.writeResult import writeResult
        writeResult(self, details, file_name, folderAndFile, folderPath, location_github_branch_push, topicContents)

        if folderAndFile.endswith('.json'):
            from errorHandling.jsonCheck import jsonCheck
            jsonCheck(details, self.log, 'True', [folderPath + file_name], self.location_dir)

        if (folderAndFile.endswith('.yaml')) or (folderAndFile.endswith('.yml')):
            from errorHandling.ymlCheck import ymlCheck
            ymlCheck(details, self.log, 'True', [folderPath + file_name], [folderAndFile], self.location_dir, self.location_name)

        if ((details["validation"] == 'on') and ('.json' not in folderAndFile)):
            from tags.htmlValidator import htmlValidator
            htmlValidator(self, details, file_name, folderAndFile, folderPath, tags_hide, tags_show, topicContents)

        # Handle images
        if os.path.isdir(details["source_dir"] + '/images'):
            from images.imagesUsed import imagesUsed
            imagesUsed(self, details, file_name, folderAndFile, folderPath, topicContents)

    if source_files == {}:
        self.log.info('No files to process for ' + self.location_name + '.')
    else:
        self.log.info('\n')
        self.log.info('Handling files for ' + self.location_name + '.')

        if os.path.isfile(details["phraseUsageFile"]):
            with open(details["phraseUsageFile"], 'r', encoding="utf8", errors="ignore") as conrefUsageFileOpen:
                allInLinePhrasesUsedText = conrefUsageFileOpen.read()
                allInLinePhrasesUsed = allInLinePhrasesUsedText.split(',')
        else:
            allInLinePhrasesUsed = []

        if os.path.isfile(details["snippetUsageFile"]):
            with open(details["snippetUsageFile"], 'r', encoding="utf8", errors="ignore") as snippetUsageFileOpen:
                allSnippetsUsedText = snippetUsageFileOpen.read()
                allSnippetsUsed = allSnippetsUsedText.split(',')
        else:
            allSnippetsUsed = []

        if os.path.isfile(details["flagUsageFile"]):
            with open(details["flagUsageFile"], 'r', encoding="utf8", errors="ignore") as flagUsageFileOpen:
                allFlagsUsedText = flagUsageFileOpen.read()
                allFlagsUsed = allFlagsUsedText.split(',')
                if '' in allFlagsUsed:
                    allFlagsUsed.remove('')

        else:
            allFlagsUsed = []

        if os.path.isfile(details["source_dir"] + '/' + details["reuse_snippets_folder"] + '/' + str(details["reuse_phrases_file"])):
            # Open the conrefs file
            with open(details["source_dir"] + '/' + details["reuse_snippets_folder"] + '/' + details["reuse_phrases_file"],
                      'r', encoding="utf8", errors="ignore") as conrefTxtFile:
                # Load the conrefs file as json
                conrefTxt = conrefTxtFile.read()
                conrefJSON = json.loads(conrefTxt)
        else:
            conrefJSON = ''

        # Start handling each file individually from the source_files dictionary
        sortedList = sorted(source_files.items())
        source_files = dict(sortedList)

        for source_file, source_file_info in source_files.items():

            folderAndFile = source_files[source_file]['folderAndFile']
            file_name = source_files[source_file]['file_name']
            folderPath = source_files[source_file]['folderPath']
            fileStatus = source_files[source_file]['fileStatus']
            fileNamePrevious = source_files[source_file]['fileNamePrevious']

            self.log.debug('\n\n')
            self.log.debug('----------------------------------')

            self.log.info(folderAndFile)
            self.log.debug('----------------------------------')
            self.log.debug('(folderAndFile=' + folderAndFile + ',folderPath=' + folderPath + ',file_name=' + file_name +
                           ',fileStatus=' + fileStatus + ',fileNamePrevious=' + fileNamePrevious + ')')

            if not details["reuse_snippets_folder"] in folderAndFile:

                # If the subdirectory, doesn't exist in the downstream repo, create it
                if not os.path.isdir(self.location_dir + folderPath):
                    try:
                        os.makedirs(self.location_dir + folderPath)
                    except Exception:
                        if os.path.isfile(self.location_dir + folderPath):
                            os.remove(self.location_dir + folderPath)
                            os.makedirs(self.location_dir + folderPath)
                        if not os.path.isdir(self.location_dir + folderPath):
                            addToErrors('Could not create directory: ' + self.location_dir + folderPath,
                                        folderAndFile, folderPath + file_name, details, self.log, self.location_name,
                                        '', '')

                # Check the file status for 'renamed' and if so, use the fileNamePrevious to remove the old version of
                # the file from the downstream repo. This can't be a part of the following if/elif because the new
                # file still should be handled.
                if 'renamed' in fileStatus:
                    self.log.debug('Rename detected in the file status for ' + source_file + '.')
                    if fileNamePrevious == 'None':
                        addToWarnings(source_file + ' was renamed, but the previous file name could not be found, so the ' +
                                      'previous version of the file could not be removed from the downstream repo.',
                                      folderAndFile, folderPath + file_name, details, self.log, self.location_name, '', '')
                    else:
                        try:
                            if os.path.isfile(self.location_dir + '/' + fileNamePrevious):
                                os.remove(self.location_dir + '/' + fileNamePrevious)
                                self.log.debug(source_file + ' was renamed in the upstream repo. Deleting ' +
                                               fileNamePrevious + ' from ' + self.location_name + ' as well.')
                        except Exception:
                            addToWarnings(fileNamePrevious + ' could not be found, so the previous version of the file ' +
                                          'could not be removed from the downstream repo.', folderAndFile, folderPath + file_name, details, self.log,
                                          self.location_name, '', '')

                if 'removed-for-location' in fileStatus:
                    if os.path.isfile(self.location_dir + folderPath + file_name):
                        os.remove(self.location_dir + folderPath + file_name)
                        self.log.debug(source_file + ' was deleted from the upstream repo. Deleting from ' + self.location_name + ' as well.')

                # Check the file status for 'removed'. If the file was removed from upsteam, remove it from staging/prod too
                elif 'removed' in fileStatus:
                    if os.path.isfile(self.location_dir + folderPath + file_name):
                        os.remove(self.location_dir + folderPath + file_name)
                        self.log.debug(source_file + ' was deleted from the upstream repo. Deleting from ' +
                                       self.location_name + ' as well.')
                    else:
                        self.log.debug(source_file + ' was deleted from the upstream repo, but was not found in this ' +
                                       'downstream location: ' + self.location_dir + folderPath + file_name)

                elif file_name.endswith(tuple(details["img_filetypes"])):
                    if ((os.path.isfile(details["source_dir"] + folderAndFile)) and
                            (folderAndFile in self.all_files_dict) and
                            (not details["source_dir"] == 'local')):
                        imageFound = False
                        for entry in self.all_files_dict:
                            if entry.endswith(tuple(details["filetypes"])):
                                if file_name in self.all_files_dict[entry]['fileContents']:
                                    self.log.debug('Confirmed ' + file_name + ' used in ' + entry + '.')
                                    from images.imagesUsed import copyImage
                                    copyImage(self, details, folderAndFile)
                                    imageFound = True
                                    break
                        if imageFound is False:
                            self.log.debug('Image not used in any content files. Not copying over.')
                    else:
                        self.log.debug('Handling images later.')

                # If the file is a text file in the supported text file list, then run the filecleanup loop at the top of the file over it
                elif file_name.endswith(tuple(details["filetypes"])):
                    # The filepaths are the differences between these two sections
                    if not os.path.isdir(self.location_dir + folderPath):
                        self.log.debug('Folder does not exist in working dir: ' + self.location_dir + folderPath)

                    # For Travis, only copy over the file that's being worked with
                    if ((os.path.isfile(details["source_dir"] + folderAndFile)) and
                            (folderAndFile in self.all_files_dict)):
                        fileCleanUpLoop(self, details, allFlagsUsed, allInLinePhrasesUsed, allSnippetsUsed, conrefJSON, file_name, fileNamePrevious, fileStatus,
                                        folderAndFile, folderPath, tags_hide, tags_show)
                    else:
                        self.log.debug('Not working with ' + folderAndFile + '. Does not exist in source dir: ' +
                                       details["source_dir"] + folderAndFile)
                        self.log.debug('folderAndFile = ' + folderAndFile)
                        self.log.debug('file_name = ' + file_name)
                        self.log.debug('folderPath = ' + folderPath)
                        self.log.debug('fileNamePrevious = ' + fileNamePrevious)

        # If every file is being generated, then create these test files
        # For Travis and Jenkins where only a select few files are being generated, don't run these
        if self.location_output_action == 'none':
            allInLinePhrasesUsed = sorted(list(dict.fromkeys(allInLinePhrasesUsed)))
            with open(details["phraseUsageFile"], 'w+', encoding="utf8", errors="ignore") as phraseUsageFileOpen:
                phraseUsageFileOpen.write(",".join(allInLinePhrasesUsed))

            allSnippetsUsed = sorted(list(dict.fromkeys(allSnippetsUsed)))
            with open(details["snippetUsageFile"], 'w+', encoding="utf8", errors="ignore") as snippetUsageFileOpen:
                snippetUsageFileOpen.write(",".join(allSnippetsUsed))

            allFlagsUsed = sorted(list(dict.fromkeys(allFlagsUsed)))
            with open(details["flagUsageFile"], 'w+', encoding="utf8", errors="ignore") as flagUsageFileOpen:
                flagUsageFileOpen.write(",".join(allFlagsUsed))
