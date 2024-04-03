#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def snippetCheck(details, log, allSourceFiles, conref_files_list, filesForOtherLocations):

    # Check if the markdown snippet files are actually used in content files

    import os

    from mdenricher.errorHandling.errorHandling import addToWarnings

    if os.path.isdir(details["source_dir"] + '/' + details["reuse_snippets_folder"]):
        snippetsNotUsed = []
        for conref in conref_files_list:
            conrefName = conref.split('/' + details["reuse_snippets_folder"] + '/')[1]
            conrefName = '{[' + conrefName + ']}'
            found = False
            for entry in allSourceFiles:
                if entry.endswith(tuple(details["filetypes"])):
                    try:
                        fileContents = allSourceFiles[entry]['fileContents']
                        if conrefName in fileContents:
                            log.debug('Confirmed snippet ' + conrefName + ' usage in ' + entry + '.')
                            found = True
                            break
                    except Exception:
                        continue
            # If it's not found, try the files from builds that might not have been enabled
            if found is False:
                for entry in filesForOtherLocations:
                    if entry.endswith(tuple(details["filetypes"])):
                        with open(details["source_dir"] + entry, 'r', encoding="utf8", errors="ignore") as checkFile:
                            fileContents = checkFile.read()
                            if conrefName in fileContents:
                                log.debug('Confirmed snippet ' + conrefName + ' usage in ' + entry + '.')
                                found = True
                                break
            if found is False:
                snippetsNotUsed.append(conrefName)
                log.debug('Feature flag ' + conrefName + ' was not used in any content files.')

        if len(snippetsNotUsed) > 0:
            if len(snippetsNotUsed) == 1:
                intro = 'This snippet file is'
            else:
                intro = 'These snippet files are'
            addToWarnings(intro + ' not used in any content files and can be removed: ' +
                          (", ".join(snippetsNotUsed)), details["reuse_snippets_folder"], '', details, log, 'pre-build',
                          '', '')
