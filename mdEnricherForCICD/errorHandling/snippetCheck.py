#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def snippetCheck(details, log, conref_files_list):

    import os

    from errorHandling.errorHandling import addToWarnings

    if os.path.isdir(details["source_dir"] + '/' + details["reuse_snippets_folder"]):
        # Get the list of conrefs that were used across all of the builds
        if os.path.isfile(details["snippetUsageFile"]):
            # Get the used conref list
            with open(details["snippetUsageFile"], 'r', encoding="utf8", errors="ignore") as snippetUsageFileOpen:
                usedConrefsText = snippetUsageFileOpen.read()
                if ',' in usedConrefsText:
                    usedConrefs = usedConrefsText.split(',')

                    # Open the phrases file and get all of those defined
                    unusedConrefs = []
                    for conref in conref_files_list:
                        conrefName = conref.split('/reuse-snippets/',)[1]
                        if not ('{[' + conrefName + ']}') in usedConrefs:
                            unusedConrefs.append('{[' + conrefName + ']}')

                    if len(unusedConrefs) > 0:
                        if len(unusedConrefs) == 1:
                            intro = 'This snippet file is'
                        else:
                            intro = 'These snippet files are'
                        addToWarnings(intro + ' not used in any content files and can be removed: ' +
                                      (", ".join(unusedConrefs)), details["reuse_snippets_folder"], '', details, log, 'pre-build', '', '')
