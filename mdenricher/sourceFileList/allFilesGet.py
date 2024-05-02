#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def allFilesGet(details, location_contents_files, location_contents_files_keep, location_contents_files_remove,
                location_contents_folders, location_contents_folders_keep,
                location_contents_folders_remove_and_files, location_ibm_cloud_docs,
                log, remove_all_other_files_folders, source_files_original_list):

    # Create a list of all of the files in the repo so we can sort through them and choose which ones to loop over.
    # Like if a conref file changes, this list will be used to look inside each file to see if that conref is used in it

    def allFileCheck(details, path, file, folder_name, all_files_dict, conref_files_list,
                     filesForOtherLocations, image_files_list, sitemap_file):
        # Always ignore the locations file
        if ((path + '/' + file) == (details["locations_file"])):
            # log.debug('Not adding locations file to all files list: ' + file)
            filesForOtherLocations.append(file)
            log.debug('Not handling locations file: ' + file)

        # Always ignore the Slack mapping file
        elif ((path + '/' + file) == (details["slack_user_mapping"])):
            # log.debug('Not adding locations file to all files list: ' + file)
            filesForOtherLocations.append(file)
            log.debug('Not handling user mapping file: ' + file)

        # Always ignore the user mapping file
        elif (((file == 'user-mapping.json') or (file == 'cloudoekeyrefs.yml') or (file == 'toc_schema.json')) and (location_ibm_cloud_docs is True)):
            filesForOtherLocations.append(file)
            log.debug('Not handling IBM Cloud files: ' + file)

        # Keep files that are meant to be kept, no matter what type they are, and use the output location specified
        elif (folder_name + file in location_contents_files_keep):
            log.debug('Handling location_contents_files_keep: ' + file)
            all_files_dict = addToList('None', details, log, 'None', 'None', 'modified',
                                       folder_name + file, all_files_dict, location_contents_files,
                                       location_contents_folders)

        # Remove files that are meant to be removed, no matter what type they are
        elif (folder_name + file in location_contents_files_remove):
            filesForOtherLocations.append(folder_name + file)
            log.debug('Not handling files in location_contents_files_remove: ' + folder_name + file)

        # Always ignore the .travis.yml file
        elif file == '.travis.yml':
            filesForOtherLocations.append(folder_name + file)
            log.debug('Not handling .travis.yml: ' + folder_name + file)

        # If they start with a folder that's going to be removed, don't include them
        elif (folder_name).startswith(tuple(location_contents_folders_remove_and_files)):
            filesForOtherLocations.append(folder_name + file)
            log.debug('Not handling folders in location_contents_folders_remove_and_files: ' + folder_name + file)

        # Include them if they the filetype is supported and all other files aren't removed
        elif (file.endswith(tuple(details["filetypes"])) and
                           (remove_all_other_files_folders is False)):
            # if not file == str(details["reuse_phrases_file"]):
            log.debug('Handling filetypes and remove is False: ' + folder_name + file)
            all_files_dict = addToList('None', details, log, 'None', 'None', 'modified',
                                       folder_name + file, all_files_dict, location_contents_files,
                                       location_contents_folders)

        # Include them if they start with a folder that's meant to be kept
        # Even if all other files are going to be removed
        elif (file.endswith(tuple(details["filetypes"])) and
                           (remove_all_other_files_folders is True) and
                           ((folder_name in location_contents_folders_keep) or folder_name.startswith(tuple(location_contents_folders_keep)))):
            # if not file == str(details["reuse_phrases_file"]):
            log.debug('Handling filetypes and Remove is true and folder name is in folder keep: ' + folder_name + file)
            all_files_dict = addToList('None', details, log, 'None', 'None', 'modified',
                                       folder_name + file, all_files_dict, location_contents_files,
                                       location_contents_folders)

        elif file.endswith(tuple(details["img_filetypes"])) and (
                           (remove_all_other_files_folders is False) or
                           ((remove_all_other_files_folders is True) and
                            ((folder_name in location_contents_folders_keep) or folder_name.startswith(tuple(location_contents_folders_keep))))):
            image_files_list.append(folder_name + file)
            all_files_dict = addToList('None', details, log, 'None', 'None', 'modified',
                                       folder_name + file, all_files_dict, location_contents_files,
                                       location_contents_folders)
            # log.debug('Handling image filetypes: ' + folder_name + file)
            if location_ibm_cloud_docs is True:
                # log.debug('Checking to see if any images are not in the /images or /images-ui-only directories.')
                if (('/images/' not in folder_name) and ('/images-ui-only/' not in folder_name)):
                    if os.path.isdir(details["source_dir"] + '/images-ui-only'):
                        addToWarnings('Image is not stored in either the /images or /images-ui-only directories.',
                                      folder_name + file, folder_name + file, details, log, 'pre-build', '', '')
                    else:
                        addToWarnings('Image is not stored in /images directory.', folder_name + file,
                                      folder_name + file, details, log, 'pre-build', '', '')

        if (details["reuse_snippets_folder"] in path) and (not file == str(details["reuse_phrases_file"])):
            conref_files_list.append(folder_name + file)

        # If this is a sitemap file and it does exist in the all files list,
        # then set it as the sitemap file
        if (sitemap_file == 'None') and (file == 'sitemap.md') and (folder_name + file in all_files_dict):
            sitemap_file = folder_name + file
            log.debug('Setting sitemap_file as ' + sitemap_file)

        return (all_files_dict, conref_files_list, filesForOtherLocations, image_files_list, sitemap_file)

    # All of these list entries always start with a slash

    import os  # for running OS commands like changing directories or listing files in directory

    from mdenricher.sourceFileList.addToList import addToList
    from mdenricher.errorHandling.errorHandling import addToWarnings
    # from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.setup.exitBuild import exitBuild

    # log.debug('Gathering all source files.')
    all_files_dict: dict[dict[str, str], dict[str, str]] = {}  # type: ignore[misc]
    conref_files_list: list[str] = []  # type: ignore[misc]
    image_files_list: list[str] = []  # type: ignore[misc]
    sitemap_file = 'None'
    # filesForOtherLocations to collect all file names from all locations
    # for complete validation even when not all locations are built
    filesForOtherLocations: list[str] = []  # type: ignore[misc]
    allFiles: list[str] = []  # type: ignore[misc]

    for (path, dirs, files) in os.walk(details["source_dir"]):
        # Allow the running of the example and docs directories, but not anything else
        if ((('md-enricher-for-cicd' in details["source_dir"]) and
             ('md-enricher-for-cicd' in str(details["source_github_repo"])) and
             ('doctopus-common' not in path) and
             (details["output_dir"] not in path)) or

                (('md-enricher-for-cicd' in details["source_dir"]) and
                 ('/example' in details["source_dir"]) and
                 ('doctopus-common' not in path) and
                 (details["output_dir"] not in path)) or

                (('.git' not in path) and
                 ('.DS_Store' not in path) and
                 ('environment-variables' not in path) and
                 ('doctopus-common' not in path) and
                 ('md-enricher-for-cicd' not in path) and
                 (details["output_dir"] not in path))):

            folder_name = path.split(details["source_dir"])[1]
            if not folder_name.endswith('/'):
                folder_name = folder_name + '/'
            if not folder_name.startswith('/'):
                folder_name = '/' + folder_name
            allFiles = allFiles + files
            for filesToScanFirst in details['filesToScanFirst']:
                if filesToScanFirst in allFiles:
                    allFiles.remove(filesToScanFirst)
                    allFiles.insert(0, filesToScanFirst)
            for file in sorted(files):

                all_files_dict, conref_files_list, filesForOtherLocations, image_files_list, sitemap_file = allFileCheck(details, path, file, folder_name,
                                                                                                                         all_files_dict,
                                                                                                                         conref_files_list,
                                                                                                                         filesForOtherLocations,
                                                                                                                         image_files_list, sitemap_file)

    for source_file in source_files_original_list:
        if source_file[1:] not in allFiles:
            if '/' in source_file[1:]:
                folder_name, file = source_file[1:].rsplit('/', 1)
                if not folder_name.endswith('/'):
                    folder_name = folder_name + '/'
                if not folder_name.startswith('/'):
                    folder_name = '/' + folder_name
            else:
                folder_name = ''
                file = source_file[1:]
            (all_files_dict, conref_files_list, filesForOtherLocations, image_files_list, sitemap_file) = (allFileCheck
                                                                                                           (details, details["source_dir"],
                                                                                                            file, folder_name, all_files_dict,
                                                                                                            conref_files_list, filesForOtherLocations,
                                                                                                            image_files_list, sitemap_file))

    conref_files_list.sort()
    image_files_list.sort()
    # if not all_files_dict == {}:
    # log.debug('All files gathered.')
    # if not conref_files_list == []:
    # log.debug('Conref files gathered.')
    # if not image_files_list == []:
    # log.debug('Image files gathered.')
    # log.info(json.dumps(all_files_dict, indent=4))
    # log.info('\nIMAGE_FILES_LIST:')
    # log.info(image_files_list)

    return (all_files_dict, conref_files_list, image_files_list, sitemap_file, filesForOtherLocations)
