#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def ymlCheck(details, log, ISSUE_WARNINGS, yml_files_list, yml_files_list_folderAndFile, location_dir, location_name):

    # Verify the YML/YAML syntax is valid
    # Validate IBM Cloud Docs toc.yamls against their schema

    # Most common issues:
    # Line breaks with spaces in it
    # Lists not lined up with the parent, like - topic under topics:
    # Tagging that leaves behind line breaks in the output
    # Extra spaces at the beginning of a key

    import yaml  # for sending data with and parsing data from requests
    import os  # for running OS commands like changing directories or listing files in directory
    import jsonschema

    # from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.setup.exitBuild import exitBuild

    if not yml_files_list == []:
        # Conditional log
        if ISSUE_WARNINGS == 'False':
            path = details["source_dir"]
            build = ''
        else:
            path = location_dir
            build = location_name

        for ymlFile in yml_files_list:
            # Get the position in the list of the file to get the folderAndFile entry in the other list
            listPosition = yml_files_list.index(ymlFile)
            folderAndFile = yml_files_list_folderAndFile[listPosition]

            # Open the yml file and read it
            if os.path.isfile(path + ymlFile):
                try:
                    log.debug('Validating YML.')
                    with open(path + ymlFile, 'r', encoding="utf8", errors="ignore") as ymlFileVar:
                        try:
                            configuration = yaml.safe_load(ymlFileVar)
                        except yaml.YAMLError as exc:
                            log.warning(exc)
                            addToErrors('YML not formatted properly. Check ' + ymlFile + ' for errors. ' +
                                        exc, folderAndFile, '', details, log, build, '', '')
                        else:
                            log.debug('YML validated: ' + ymlFile)
                    # For IBM Cloud, verify the toc.yaml against the toc_schema.json
                    if (ymlFile == '/toc.yaml') and (details["ibm_cloud_docs"] is True):
                        if os.path.isfile(details["workspace"] + '/toc_schema.json'):
                            log.debug('IBM Cloud toc_schema.json exists. toc.yaml can be verified.')
                            with open(details["workspace"] + '/toc_schema.json', "r", encoding="utf8", errors="ignore") as stream:
                                try:
                                    config_schema = yaml.safe_load(stream)
                                    log.debug(str(config_schema)[0:500])
                                except yaml.YAMLError as exc:
                                    log.warning(exc)

                                try:
                                    jsonschema.validate(configuration, config_schema, cls=None)
                                except Exception as e:
                                    log.error(e)
                                    error = str(e)
                                    if ':' in error:
                                        error = error.split(':')[0]
                                    addToErrors('YML not formatted properly. Check the toc.yaml for tagging errors. ' +
                                                error, folderAndFile, '', details, log, build, '', '')
                        else:
                            log.debug('toc_schema.json was not found. The toc.yaml cannot be verified.')

                except Exception as e:
                    log.error(e)
                    error = str(e)
                    if 'did not validate' in error:
                        error = error.split('did not validate')[1]
                    addToErrors('YML not formatted properly. ' + error, folderAndFile, '', details, log, build, '', '')
