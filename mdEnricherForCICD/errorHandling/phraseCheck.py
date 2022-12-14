#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def phraseCheck(details, log):

    import json
    import os

    from errorHandling.errorHandling import addToWarnings

    if os.path.isfile(details["source_dir"] + '/' + details["reuse_snippets_folder"] + '/' + str(details["reuse_phrases_file"])):
        # Get the list of conrefs that were used across all of the builds
        if os.path.isfile(details["phraseUsageFile"]):
            # Get the used conref list
            with open(details["phraseUsageFile"], 'r', encoding="utf8", errors="ignore") as phraseUsageFileOpen:
                usedConrefsText = phraseUsageFileOpen.read()
                usedConrefs = usedConrefsText.split(',')

            # Open the phrases file and get all of those defined
            with open(details["source_dir"] + '/' + details["reuse_snippets_folder"] +
                      '/' + details["reuse_phrases_file"], 'r', encoding="utf8", errors="ignore") as conrefTxtFile:
                # Load the conrefs file as json
                conrefTxt = conrefTxtFile.read()
                conrefJSON = json.loads(conrefTxt)

            # Compare the two lists
            unusedConrefs = []
            for conref in conrefJSON:
                if conref not in usedConrefs:
                    if conref.startswith('{['):
                        unusedConrefs.append(conref)
            if len(unusedConrefs) > 0:
                if len(unusedConrefs) == 1:
                    intro = 'This snippet phrases is'
                else:
                    intro = 'These snippet phrases are'
                addToWarnings(intro + ' not used in any content files and can be removed: ' + (", ".join(unusedConrefs)),
                              details["reuse_snippets_folder"] + '/' + details["reuse_phrases_file"], '', details, log, 'pre-build', '', '')
