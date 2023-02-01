#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def checkLocationsPaths(folderAndFile, location_contents_files, location_contents_folders, log):

    # Based on what is in the locations_contents, parse the downstream paths of files and folders

    if folderAndFile.count("/") > 1:
        # /tagging-a-subrepo/a-test-subrepo.md
        # /tagging-a-subrepo/anotherfolder/a-test-subrepo.md
        returnedFolderName, returnedFileName = folderAndFile.rsplit('/', 1)
        # /tagging-a-subrepo   a-test-subrepo.md
        # /tagging-a-subrepo/anotherfolder   a-test-subrepo.md
    else:
        returnedFolderName = '/'
        returnedFileName = folderAndFile

    locationFileMatch = False
    add = True

    if not location_contents_files == []:
        for location_contents_file in location_contents_files:
            if (location_contents_file['file'].replace('/', '')) == ((folderAndFile).replace('/', '')):
                file_handling = location_contents_file['file_handling']
                if file_handling == 'remove':
                    add = False
                elif (file_handling is None):
                    returnedFolderName = folderAndFile.rsplit('/', 1)[0]
                elif (file_handling == ''):
                    returnedFolderName = '/'
                elif '/' in file_handling:
                    returnedFolderName = file_handling.rsplit('/', 1)[0]
                else:
                    returnedFolderName = '/'
                locationFileMatch = True
                break
    if (not location_contents_folders == []) and (locationFileMatch is False):
        for location_contents_folder in location_contents_folders:
            # /tagging-a-subrepo
            # /tagging-a-subrepo/anotherfolder
            if folderAndFile.startswith('/' + location_contents_folder['folder'] + '/'):
                file_handling = location_contents_folder['file_handling']
                if file_handling == 'remove':
                    add = False
                elif (file_handling == '') or (file_handling is None):
                    # /tagging-a-subrepo/
                    if (returnedFolderName + '/') == '/' + location_contents_folder['folder'] + '/':
                        returnedFolderName = '/'
                    else:
                        # /tagging-a-subrepo/anotherfolder
                        returnedFolderName = ((returnedFolderName + '/').split('/' + location_contents_folder['folder'] + '/', 1)[1])
                        # anotherfolder
                else:
                    returnedFolderName = file_handling
                break

    if not returnedFolderName.startswith('/'):
        returnedFolderName = '/' + returnedFolderName
    if not returnedFolderName.endswith('/'):
        returnedFolderName = returnedFolderName + '/'
    if '/' in returnedFileName:
        returnedFileName = returnedFileName.replace('/', '')

    return (add, returnedFileName, returnedFolderName)
