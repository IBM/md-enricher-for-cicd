#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def checkLocationsPaths(details, folderAndFile, location_contents_files, location_contents_folders, remove_all_other_files_folders, log):

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
    locationHandling = 'keep'

    if not location_contents_files == []:
        for location_contents_file in location_contents_files:
            if (location_contents_file['file'].replace('/', '')) == ((folderAndFile).replace('/', '')):
                file_handling = location_contents_file['file_handling']
                if file_handling == 'remove':
                    locationHandling = 'remove'
                elif file_handling == 'keep':
                    locationHandling = 'keep'
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
                locationFileMatch = True
                file_handling = location_contents_folder['file_handling']
                if file_handling == 'remove':
                    locationHandling = 'remove'
                elif file_handling == 'keep':
                    locationHandling = 'keep'
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

    if (locationFileMatch is False) and (locationHandling == 'keep') and (folderAndFile.endswith(tuple(details['img_output_filetypes']))):
        locationHandling = 'keep-if-used'
        locationFileMatch = True

    if locationFileMatch is False and remove_all_other_files_folders is True:
        locationHandling = 'remove'
        locationFileMatch = True

    # See if any of these files should be automatically set to remove
    ignoreFileNames = ['cloudoekeyrefs.yml', 'toc_schema.json', 'user-mapping.json']
    ignoreWholePaths = [details["locations_file"], details["slack_user_mapping"]]
    if (locationFileMatch is False and
            ((folderAndFile in ignoreFileNames) or
             (folderAndFile.endswith(tuple(details["img_src_filetypes"])) and details['unprocessed'] is False) or
             (details["source_dir"] + folderAndFile in ignoreWholePaths) or
             (folderAndFile == details['featureFlagFile'] and details['unprocessed'] is False))):
        locationHandling = 'remove'
        locationFileMatch = True

    return (locationHandling, returnedFileName, returnedFolderName)
