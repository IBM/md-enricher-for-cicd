#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

from sre_compile import isstring


def addToList(self, details, log, fileNamePrevious, filePatch, fileStatus, folderAndFile, source_files, location_contents_files, location_contents_folders):

    # Append the details about each file to the source_files dictionary

    from mdenricher.sourceFileList.checkLocationsPaths import checkLocationsPaths
    import os

    # folderAndFile = upstream folder and file location
    # folderPath = downstream folder location - starts and ends with slash
    # file_name = downstream file name - does not start with a slash

    def addToDictionary(dictionary):
        # Add each of these values to the dictionary for this file

        if folderAndFile in dictionary:
            del dictionary[folderAndFile]
        dictionary[folderAndFile] = {}
        dictionary[folderAndFile]['folderAndFile'] = folderAndFile
        dictionary[folderAndFile]['file_name'] = returnedFileName
        dictionary[folderAndFile]['folderPath'] = returnedFolderName
        dictionary[folderAndFile]['fileStatus'] = fileStatus
        dictionary[folderAndFile]['filePatch'] = filePatch
        dictionary[folderAndFile]['fileNamePrevious'] = fileNamePrevious

        log.debug('Adding: ' + folderAndFile + ' (upstream path), ' + returnedFolderName + returnedFileName + ' (downstream path)')

        if (os.path.isfile(details["source_dir"] + folderAndFile)) and (folderAndFile.endswith(tuple(details["filetypes"]))):
            with open(details["source_dir"] + folderAndFile, 'r', encoding="utf8", errors="ignore") as fileName_write:
                fileContents = fileName_write.read()
                dictionary[folderAndFile]['fileContents'] = fileContents
        else:
            dictionary[folderAndFile]['fileContents'] = ''

        return (dictionary)

    # Workaround
    if not isstring(self):
        location_contents_files = self.location_contents_files
        location_contents_folders = self.location_contents_folders

    add, returnedFileName, returnedFolderName = checkLocationsPaths(folderAndFile, location_contents_files, location_contents_folders, log)

    if add is True:
        source_files = addToDictionary(source_files)

    return (source_files)
