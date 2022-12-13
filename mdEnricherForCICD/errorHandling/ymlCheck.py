#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

# Verify the JSON syntax passes in the files listed

def ymlCheck(details, log, ISSUE_WARNINGS, yml_files_list, yml_files_list_folderAndFile, location_dir, location_name):

    # Most common issues:
    # Line breaks with spaces in it
    # Lists not lined up with the parent, like - topic under topics:
    # Tagging that leaves behind line breaks in the output
    # Extra spaces at the beginning of a key

    # Import the json library
    import yaml  # for sending data with and parsing data from requests
    import os  # for running OS commands like changing directories or listing files in directory
    import jsonschema

    # from errorHandling.errorHandling import addToWarnings
    from errorHandling.errorHandling import addToErrors
    # from setup.exitBuild import exitBuild

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
                        configuration = yaml.safe_load(ymlFileVar)
                    # For IBM Cloud, verify the toc.yaml against the toc_schema.json
                    if (ymlFile == '/toc.yaml') and (details["ibm_cloud_docs"] is True):
                        if os.path.isfile(details["workspace"] + '/toc_schema.json'):
                            log.debug('IBM Cloud toc_schema.json exists. toc.yaml can be verified.')
                            with open(details["workspace"] + '/toc_schema.json', "r", encoding="utf8", errors="ignore") as stream:
                                try:
                                    config_schema = yaml.safe_load(stream)
                                    log.debug(str(config_schema)[0:500])
                                    os.remove(details["workspace"] + '/toc_schema.json')
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
                    log.debug('YML validated: ' + ymlFile)
                except Exception as e:
                    log.error(e)
                    error = str(e)
                    if 'did not validate' in error:
                        error = error.split('did not validate')[1]
                    addToErrors('YML not formatted properly. ' + error, folderAndFile, '', details, log, build, '', '')
                '''
                else:
                    # Check TOC files for weird spacing
                    if ymlFile == '/toc.yaml':
                        # Open the TOC file and read as a string
                        with open(path + ymlFile, 'r', encoding="utf8", errors="ignore") as ymlFileVar:
                            fileRead = ymlFileVar.read()
                        # Open the TOC file again and load it as YAML and then dump it
                        with open(path + ymlFile, 'r', encoding="utf8", errors="ignore") as ymlFileVar:
                            yamlLoaded = yaml.safe_load(ymlFileVar)
                            yamlDumped = yaml.dump(yamlLoaded, sort_keys=False,
                                                   width=10000000000)
                        # Remove extra newlines because the dumping process adds them
                            commentsList = re.findall('\n# (.*)\n', fileRead)
                            for comment in commentsList:
                                fileRead = fileRead.replace('\n# ' + comment, '\n')
                            log.debug('Removed comments: ' + str(commentsList))
                            while '\n \n' in fileRead:
                                fileRead = fileRead.replace('\n \n', '\n')
                            while '\n\n' in fileRead:
                                fileRead = fileRead.replace('\n\n', '\n')
                            while ' \n' in fileRead:
                                fileRead = fileRead.replace(' \n', '\n')
                            while '\n\n' in yamlDumped:
                                yamlDumped = yamlDumped.replace('\n\n', '\n')
                        # Do a diff of the original TOC and the dumped version to see what's different
                        if not fileRead == yamlDumped:
                            originalTOC = fileRead.splitlines()
                            reformattedTOC = yamlDumped.splitlines()
                            line_formatter = '{:3d}  {}'.format
                            file1_lines = [line_formatter(i, line) for i, line in enumerate(reformattedTOC, 1)]
                            file2_lines = [line_formatter(i, line) for i, line in enumerate(originalTOC, 1)]
                            results = difflib.Differ().compare(file1_lines, file2_lines)
                            for resultLine in results:
                                log.info(resultLine)
                                if resultLine.startswith('-') or resultLine.startswith('+'):
                                    lineRevised = resultLine.replace('-', '', 1).replace('+', '', 1)
                                    while lineRevised.startswith(' '):
                                        lineRevised = lineRevised[1:]
                                    countSpaces = 0
                                    lineNumber, lineShortened = lineRevised.split(' ', 1)
                                    while lineShortened.startswith(' '):
                                        lineShortened = lineShortened[1:]
                                        countSpaces = countSpaces + 1
                                    # If a topic list has extra spaces, it gets moved up to the previous line
                                    if lineShortened.count('-') > 1:
                                        guess = "Check the spacing of the line before and after."
                                        addToErrors('TOC formatting issue near ' + build + ' output L#' +
                                                    str(lineNumber) + '. ' + guess + '\n' + lineShortened,
                                                    folderAndFile, '', details, log, build,
                                                    lineShortened, fileRead)
                                    # Lists might not be right under the parent
                                    elif lineShortened.startswith('-'):
                                        guess = "Check that the spacing matches the line above it."
                                        addToWarnings('TOC formatting issue near ' + build + ' output L#' +
                                                      str(lineNumber) + '. ' + guess + '\n' + lineShortened,
                                                      folderAndFile, '', details, log,
                                                      build, lineShortened, fileRead)
                                    # If there's an odd number of spaces at the beginning of the line
                                    elif not (countSpaces % 2) == 0:
                                        guess = "Check the spacing at the beginning of the line."
                                        addToWarnings('TOC formatting issue near ' + build + ' output L#' +
                                                      str(lineNumber) + '. ' + guess + '\n' + lineShortened,
                                                      folderAndFile, '', details, log,
                                                      build, lineShortened, fileRead)
                                    else:
                                        addToWarnings('TOC formatting issue near ' + build + ' output L#' +
                                                      str(lineNumber) + '\n' + lineShortened, folderAndFile, '',
                                                      details, log, build, lineShortened, fileRead)
                                    # Only report 1 issue at a time because the first one could be creating more issues
                                    break
'''
