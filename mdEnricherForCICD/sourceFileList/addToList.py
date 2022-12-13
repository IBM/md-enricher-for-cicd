#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

from sre_compile import isstring


def addToList(self, details, log, fileNamePrevious, filePatch, fileStatus, folderAndFile, source_files, location_contents_files, location_contents_folders):

    # Append the details about each file to the source_files dictionary
    from sourceFileList.checkLocationsPaths import checkLocationsPaths
    import os

    # folderAndFile = upstream folder and file location
    # folderPath = downstream folder location - starts and ends with slash
    # file_name = downstream file name - does not start with a slash

    # Workaround
    if not isstring(self):
        location_contents_files = self.location_contents_files
        location_contents_folders = self.location_contents_folders

    add, returnedFileName, returnedFolderName = checkLocationsPaths(folderAndFile, location_contents_files, location_contents_folders, log)

    if add is True:

        # Add each of these values to the dictionary for this file

        if folderAndFile in source_files:
            del source_files[folderAndFile]
        source_files[folderAndFile] = {}
        source_files[folderAndFile]['folderAndFile'] = folderAndFile
        source_files[folderAndFile]['file_name'] = returnedFileName
        source_files[folderAndFile]['folderPath'] = returnedFolderName
        source_files[folderAndFile]['fileStatus'] = fileStatus
        source_files[folderAndFile]['filePatch'] = filePatch
        source_files[folderAndFile]['fileNamePrevious'] = fileNamePrevious
        log.debug('Adding: ' + folderAndFile)

        if (os.path.isfile(details["source_dir"] + folderAndFile)) and (folderAndFile.endswith(tuple(details["filetypes"]))):
            with open(details["source_dir"] + folderAndFile, 'r', encoding="utf8", errors="ignore") as fileName_write:
                fileContents = fileName_write.read()
                source_files[folderAndFile]['fileContents'] = fileContents
        else:
            source_files[folderAndFile]['fileContents'] = ''
    else:
        log.debug('Not adding: ' + folderAndFile)

    return (source_files)
