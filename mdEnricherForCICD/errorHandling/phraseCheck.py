#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def phraseCheck(details, log, allSourceFiles, filesForOtherLocations):

    # Check if each of the phrase snippets are actually used in the content

    import json
    import os

    from errorHandling.errorHandling import addToWarnings

    if os.path.isfile(details["source_dir"] + '/' + details["reuse_snippets_folder"] + '/' + str(details["reuse_phrases_file"])):

        # Open the phrases file and get all of those defined
        with open(details["source_dir"] + '/' + details["reuse_snippets_folder"] +
                  '/' + details["reuse_phrases_file"], 'r', encoding="utf8", errors="ignore") as conrefTxtFile:
            # Load the conrefs file as json
            conrefTxt = conrefTxtFile.read()
            conrefJSON = json.loads(conrefTxt)
            phrasesNotUsed = []
            for conref in conrefJSON:
                found = False
                for entry in allSourceFiles:
                    if entry.endswith(tuple(details["filetypes"])):
                        try:
                            if conref in allSourceFiles[entry]['fileContents']:
                                if (details["reuse_snippets_folder"] + '/' + details["reuse_phrases_file"]) in entry:
                                    conrefCount = allSourceFiles[entry]['fileContents'].count(conref)
                                    if conrefCount > 1:
                                        log.debug('Confirmed phrase ' + conref + ' usage in ' + entry + '.')
                                        found = True
                                        break
                                else:
                                    log.debug('Confirmed phrase ' + conref + ' usage in ' + entry + '.')
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
                                if conref in fileContents:
                                    log.debug('Confirmed phrase ' + conref + ' usage in ' + entry + '.')
                                    found = True
                                    break
                if found is False:
                    phrasesNotUsed.append(conref)
                    log.debug('Phrase ' + conref + ' was not used in any content files.')

            if len(phrasesNotUsed) > 0:
                if len(phrasesNotUsed) == 1:
                    intro = 'This snippet phrase is'
                else:
                    intro = 'These snippet phrases are'
                addToWarnings(intro + ' not used in any content files and can be removed: ' + (", ".join(phrasesNotUsed)),
                              details["reuse_snippets_folder"] + '/' + details["reuse_phrases_file"], '', details, log, 'pre-build', '', '')
