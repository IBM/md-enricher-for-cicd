#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def removeUneededFiles(self, details):

    import os
    import shutil
    from mdenricher.errorHandling.errorHandling import addToWarnings

    # Check for these directories and delete them to avoid accidental pushes
    directories_to_delete = ['/source']
    for folder in self.location_contents_folders_remove:
        directories_to_delete.append(folder)

    # Should these be within the location_dir or the output_dir
    for directory_to_delete in directories_to_delete:
        if not directory_to_delete.startswith('/') and not directory_to_delete.startswith('includes'):
            directory_to_delete = '/' + directory_to_delete
        if os.path.isdir(self.location_dir + directory_to_delete):
            self.log.debug('Deleted: ' + self.location_dir + directory_to_delete)
            shutil.rmtree(self.location_dir + directory_to_delete)

    if os.path.isdir(self.location_dir + '/doctopus-common'):
        shutil.rmtree(self.location_dir + '/doctopus-common')
        self.log.debug('Removing: ' + self.location_dir + '/doctopus-common')

    try:
        self.all_files_dict['/toc.yaml']['fileContents']
        testExistenceInTOC = True
    except Exception:
        testExistenceInTOC = False
    ignoredFileList = ['/.build.yaml', '/.pre-commit-config.yaml', '/.travis.yml', '/conref.md',
                       '/ignoreLinks.txt', '/glossary/glossary.json', '/keyref.yaml',
                       '/landing.json', '/readme.md', '/README.md', '/toc.yaml', '/user-mapping.json',
                       '/utterances.json']
    ignoredFolderList = ['/.github/', '/_include-segments/', '/images/']
    for (path, dirs, files) in os.walk(self.location_dir):
        if self.location_dir == path:
            folder = '/'
        else:
            folder = path.split(self.location_dir)[1]
            if not folder.endswith('/'):
                folder = folder + '/'
            if not folder.startswith('/'):
                folder = '/' + folder
        for file in files:
            folderAndFile = folder + file
            try:
                if (('.git' not in path) and
                        ('.git' not in file) and
                        ((file) not in self.expected_output_files) and
                        ((folder + file) not in self.expected_output_files) and
                        ((folder[1:] + file) not in self.expected_output_files) and
                        (file.endswith(tuple(details["filetypes"]))) and
                        (os.path.isfile(path + '/' + file)) and
                        (not folder + file in ignoredFileList) and
                        (not (folder.startswith(tuple(ignoredFolderList)))) and
                        (details['rebuild_all_files'] is True or details['builder'] == 'local')):
                    os.remove(path + '/' + file)
                    self.log.info('Removing old file from ' + self.location_name + ': ' + folder + file)

                elif ((testExistenceInTOC is True) and
                        ('.git' not in path) and
                        ('.git' not in file) and
                        (not (path + '/' + file) == details['locations_file']) and
                        file.endswith(tuple(details["filetypes"])) and
                        (not (' ' + folder + file) in self.all_files_dict['/toc.yaml']['fileContents']) and
                        (not (' ' + folder[1:] + file) in self.all_files_dict['/toc.yaml']['fileContents']) and
                        ('reuse-snippets' not in folder) and
                        (not '/' + file in ignoredFileList) and
                        ('conref' not in file and not file.endswith('.yaml') and not file.endswith('.yml')) and
                        (not folder + file in ignoredFileList) and
                        (not (folder.startswith(tuple(ignoredFolderList))))):
                    for item in self.all_files_dict:
                        if self.all_files_dict[item]['folderPath'] == folder and self.all_files_dict[item]['file_name'] == file:
                            folderAndFile = item
                            break
                    addToWarnings('The file is not used in the ' + self.location_name +
                                  ' toc.yaml so it is not included downstream: ' + folder + file,
                                  folderAndFile, folder + file, details, self.log, self.location_name, '', '')
                    if os.path.isfile(path + '/' + file):
                        os.remove(path + '/' + file)
                        self.log.debug('Removing undefined file from ' + self.location_name + ': ' + folder + file)
            except Exception as e:
                self.log.error('Traceback')
                self.log.error('Could not issue warning for or remove: ' + folder + file)
                self.log.error(e)

        if details['rebuild_all_files'] is True or details['builder'] == 'local':
            if (('.git' not in path) and
                    (not folder.startswith(tuple(self.expected_output_files))) and
                    (not folder.startswith(tuple(ignoredFolderList)))):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    self.log.info('Removing old folder from ' + self.location_name + ': ' + folder)
