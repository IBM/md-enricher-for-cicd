#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def locationContentList(self):

    # Parse the locations_contents bit of the locations file

    location_contents_folders_remove = []
    location_contents_folders_remove_and_files = []
    location_contents_folders_keep = {}
    location_contents_files_remove = []
    location_contents_files_keep = {}
    try:
        location_contents_folders = self.location_contents["folders"]
    except Exception:
        self.log.debug('No folders in location_contents.')
        location_contents_folders = {}
    else:
        for location_contents_folder in location_contents_folders:

            location_contents_folder_name = location_contents_folder['folder']

            # Make sure all folders start and end with a /
            if not location_contents_folder_name.startswith('/'):
                location_contents_folder_name = '/' + location_contents_folder_name
            if not location_contents_folder_name.endswith('/'):
                location_contents_folder_name = location_contents_folder_name + '/'

            # Get a list of the folders
            if (location_contents_folder['folder_handling'] == 'remove') and (location_contents_folder['file_handling'] == 'remove'):
                location_contents_folders_remove.append(location_contents_folder_name)
                location_contents_folders_remove_and_files.append(location_contents_folder_name)
            elif (location_contents_folder['folder_handling'] == 'remove'):
                location_contents_folders_keep[location_contents_folder_name] = location_contents_folder_name
                location_contents_folders_remove.append(location_contents_folder_name)
            else:
                location_contents_folders_keep[location_contents_folder_name] = location_contents_folder_name
                location_contents_folders_keep[location_contents_folder_name] = {}
                location_contents_folders_keep[location_contents_folder_name]['file_handling'] = location_contents_folder['file_handling']

    if not location_contents_folders_keep == {}:
        self.log.debug('Folders to keep:')
        for folder in location_contents_folders_keep:
            self.log.debug(folder)

    if not location_contents_folders_remove == []:
        self.log.debug('Folders to remove:')
        for folder in location_contents_folders_remove:
            self.log.debug(folder)

    try:
        location_contents_files = self.location_contents["files"]
    except Exception:
        self.log.debug('No files in location_contents.')
        location_contents_files = {}
    else:
        for location_contents_file in location_contents_files:

            location_contents_file_name = location_contents_file['file']

            # Make sure all files start with a /
            if not location_contents_file_name.startswith('/'):
                location_contents_file_name = '/' + location_contents_file_name

            # Get a list of the files
            if (location_contents_file['file_handling'] == 'remove'):
                location_contents_files_remove.append(location_contents_file_name)
            else:
                location_contents_files_keep[location_contents_file_name] = location_contents_file_name
                location_contents_files_keep[location_contents_file_name] = {}
                location_contents_files_keep[location_contents_file_name]['file_handling'] = str(location_contents_file['file_handling'])

    if not location_contents_files_keep == {}:
        self.log.debug('Files to keep:')
        for file in location_contents_files_keep:
            self.log.debug(file)

    if not location_contents_files_remove == []:
        self.log.debug('Files to remove:')
        for file in location_contents_files_remove:
            self.log.debug(file)

    if not location_contents_folders_remove_and_files == []:
        self.log.debug('Folders remove and files:')
        for file in location_contents_folders_remove_and_files:
            self.log.debug(file)

    return (location_contents_files_keep, location_contents_files_remove,
            location_contents_folders, location_contents_folders_keep, location_contents_folders_remove, location_contents_folders_remove_and_files)
