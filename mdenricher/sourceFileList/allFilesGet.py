#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def allFilesGet(details, location_contents_files, location_contents_files_keep, location_contents_files_remove,
                location_contents_folders, location_contents_folders_keep,
                location_contents_folders_remove_and_files, location_ibm_cloud_docs,
                log, remove_all_other_files_folders, source_files_original_list):

    from mdenricher.sourceFileList.tocTagHandling import tocTagHandling

    # Create a list of all of the files in the repo so we can sort through them and choose which ones to loop over.
    # Like if a conref file changes, this list will be used to look inside each file to see if that conref is used in it

    def allFileCheck(details, path, file, folder_name, all_files_dict, conref_files_list,
                     filesForOtherLocations, image_files_list, sitemap_file):

        try:
            userMapping = str(details["slack_user_mapping"].rsplit('/', 1)[1])
        except Exception:
            userMapping = ''

        # This wasn't being handled properly in checkLocationsPaths
        filesToRemove = ['.travis.yml',
                         'cloudoekeyrefs.yml',
                         'toc_schema.json',
                         'user-mapping.json',
                         str(details["locations_file"].rsplit('/', 1)[1]),
                         userMapping]

        # Remove files that are meant to be removed, no matter what type they are
        if (folder_name + file in location_contents_files_remove):
            filesForOtherLocations.append(folder_name + file)

        # If they start with a folder that's going to be removed, don't include them
        elif (folder_name).startswith(tuple(location_contents_folders_remove_and_files)):
            filesForOtherLocations.append(folder_name + file)

        # Always ignore the user mapping file
        elif ((file in filesToRemove) and (location_ibm_cloud_docs is True)):
            filesForOtherLocations.append(file)

        # Include them if they start with a folder that's meant to be kept
        # Even if all other files are going to be removed
        if file.endswith(tuple(details["filetypes"])) and (file not in filesToRemove):
            # if not file == str(details["reuse_phrases_file"]):
            # log.info('Handling filetypes: ' + folder_name + file)
            all_files_dict = addToList('None', details, log, 'None', 'None', 'modified',
                                       folder_name + file, all_files_dict, location_contents_files,
                                       location_contents_folders, remove_all_other_files_folders)

        elif file.endswith(tuple(details["img_output_filetypes"])):
            image_files_list.append(path + '/' + file)
            all_files_dict = addToList('None', details, log, 'None', 'None', 'modified',
                                       folder_name + file, all_files_dict, location_contents_files,
                                       location_contents_folders, remove_all_other_files_folders)
            # log.info('Handling image filetypes: ' + folder_name + file)

        elif file.endswith(tuple(details["img_src_filetypes"])):
            # Will be automatically removed
            all_files_dict = addToList('None', details, log, 'None', 'None', 'modified',
                                       folder_name + file, all_files_dict, location_contents_files,
                                       location_contents_folders, remove_all_other_files_folders)

        if (details["reuse_snippets_folder"] in path):
            if (not file == str(details["reuse_phrases_file"])) and details['unprocessed'] is False:
                conref_files_list.append(folder_name + file)
            elif details['unprocessed'] is True:
                all_files_dict = addToList('None', details, log, 'None', 'None', 'modified',
                                           folder_name + file, all_files_dict, location_contents_files,
                                           location_contents_folders, remove_all_other_files_folders)

        # If this is a sitemap file and it does exist in the all files list,
        # then set it as the sitemap file
        if (sitemap_file == 'None') and (file == 'sitemap.md') and (folder_name + file in all_files_dict):
            sitemap_file = folder_name + file
            log.debug('Setting sitemap_file as ' + sitemap_file)

        return (all_files_dict, conref_files_list, filesForOtherLocations, image_files_list, sitemap_file)

    # All of these list entries always start with a slash

    import os  # for running OS commands like changing directories or listing files in directory

    from mdenricher.sourceFileList.addToList import addToList
    # from mdenricher.errorHandling.errorHandling import addToWarnings
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

    for (path, dirs, files) in os.walk(details["source_dir"]):
        # Allow the running of the example and docs directories, but not anything else
        if ((('md-enricher-for-cicd' in details["source_dir"]) and
             ('md-enricher-for-cicd' in str(details["source_github_repo"])) and
             ('doctopus-common' not in path) and
             (details["output_dir"] not in path)) or

                (('.git' not in path) and
                 ('.DS_Store' not in path) and
                 ('environment-variables' not in path) and
                 ('doctopus-common' not in path) and
                 ('md-enricher-for-cicd' not in path) and
                 (details["output_dir"] not in path))):

            allFiles: list[str] = []  # type: ignore[misc]
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
            for file in sorted(allFiles):
                (all_files_dict,
                 conref_files_list,
                 filesForOtherLocations,
                 image_files_list,
                 sitemap_file) = allFileCheck(details, path, file, folder_name,
                                              all_files_dict,
                                              conref_files_list,
                                              filesForOtherLocations,
                                              image_files_list, sitemap_file)

    # Add things that might have been deleted
    for source_file in source_files_original_list:
        if source_file[1:] not in allFiles:
            if '/' in source_file[1:]:
                folder_name, file = source_file[1:].rsplit('/', 1)
                if not folder_name.endswith('/'):
                    folder_name = folder_name + '/'
                if not folder_name.startswith('/'):
                    folder_name = '/' + folder_name
            else:
                folder_name = '/'
                file = source_file[1:]
            (all_files_dict,
             conref_files_list,
             filesForOtherLocations,
             image_files_list,
             sitemap_file) = (allFileCheck(details, details["source_dir"],
                                           file, folder_name, all_files_dict,
                                           conref_files_list, filesForOtherLocations,
                                           image_files_list,
                                           sitemap_file))

    # Check TOC files for tagging to apply to the content files
    if ('/toc.yaml' in all_files_dict) and (details['ibm_cloud_docs'] is True) and ('<' in all_files_dict['/toc.yaml']['fileContents']):  # type: ignore
        log.debug('Found tags in toc.yaml')

        tagList = []

        # Location tags
        for tag in details['location_tags']:
            if '<' + tag + '>' in str(all_files_dict['/toc.yaml']['fileContents']):  # type: ignore[index]
                tagList.append(tag + ':' + tag)

        # Extra default tags
        if '<hidden>' in all_files_dict['/toc.yaml']['fileContents']:  # type: ignore[index]
            tagList.append('hidden:hidden')

        if '<all>' in all_files_dict['/toc.yaml']['fileContents']:  # type: ignore[index]
            tagList.append('all:' + ','.join(details['location_tags']))

        # Feature flag tags
        for tagJSON in details['featureFlags']:
            tagList.append(tagJSON['name'] + ':' + tagJSON['location'])

        log.debug('Tag list: ' + ', '.join(tagList))

        all_files_dict = tocTagHandling(log, details, all_files_dict, tagList)

    conref_files_list.sort()
    image_files_list.sort()
    # if not all_files_dict == {}:
    # log.debug('All files gathered.')
    # if not conref_files_list == []:
    # log.debug('Conref files gathered.')
    # if not image_files_list == []:
    # log.debug('Image files gathered.')
    # import json, sys
    # log.info(json.dumps(all_files_dict, indent=4))
    # log.info('\nIMAGE_FILES_LIST:')
    # log.info(image_files_list)

    return (all_files_dict, conref_files_list, image_files_list, sitemap_file, filesForOtherLocations)
