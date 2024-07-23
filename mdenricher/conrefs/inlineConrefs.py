#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def inlineConrefs(self, details, conrefJSON, file_name, folderAndFile, folderPath, topicContents):

    # Replace short conrefs that are in reuse_phrases_file

    import re

    from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.setup.exitBuild import exitBuild

    # Get a list of all of the conrefs that are used in the file in the Doctopus styling
    attempts = 0
    # Need to run through some topics multiple times because some inline conrefs contain other inline conrefs
    conrefErrors = []

    ignoreText = '***IgnoreSnippetIndicator***'
    ignoreTextStandard = '<!--ME_ignore-->'

    topicContents = topicContents.replace(ignoreTextStandard, ignoreText)

    # Don't transform snippets in comments
    if '<!--' in topicContents:
        commentList = re.findall('<!--(.*?)-->', topicContents, flags=re.DOTALL)
        for comment in commentList:
            commentRevised = comment.replace('{[', '{[' + ignoreText)
            topicContents = topicContents.replace('<!--' + comment + '-->', '<!--' + commentRevised + '-->')

    while attempts < 20:

        if ']}' not in topicContents:
            break

        # Find all reuse that does not have .md in it
        # This seems to still be pulling in the .md instances

        conrefsUsedList = re.findall(r"\{\[.*?(?!\.md)\]\}", topicContents)
        minimizedConrefsUsedList = []

        for conrefUsed in conrefsUsedList:
            if (('.md]}' not in conrefUsed) and (ignoreText not in conrefUsed) and
                    (ignoreTextStandard not in conrefUsed) and ('site.data' not in conrefUsed) and
                    ('{[FIRST_ANCHOR]}' not in conrefUsed) and (conrefUsed not in minimizedConrefsUsedList)):
                minimizedConrefsUsedList.append(conrefUsed)

        if minimizedConrefsUsedList == []:
            break

        # Go through all of the conrefs found. Ignore the .md or core team ones.
        for conrefUsed in minimizedConrefsUsedList:

            conrefFileName = conrefUsed.replace('{[', '').replace(']}', '')
            if (conrefUsed.count('{[') > 1) or (conrefUsed.count(']}') > 1) or ((conrefUsed.count('{[') + conrefUsed.count(']}')) != 2):
                addToWarnings('Snippet is not formatted properly and could not be replaced: "' + str(conrefUsed[0:50] +
                              '"'), folderAndFile, folderPath + file_name, details, self.log, self.location_name, conrefUsed, topicContents)
            else:
                try:
                    # Try to get the conref and its value from the JSON
                    conrefValue = conrefJSON[str(conrefUsed)]
                    topicContents = topicContents.replace(conrefUsed, '<!--Snippet ' + str(conrefFileName) +
                                                          ' start-->' + conrefValue + '<!--Snippet ' +
                                                          str(conrefFileName) + ' end-->')

                # If the conref fails, it probably was removed and this instance just wasn't removed from the content.
                # Add it to a list of possible errant conrefs.
                except Exception:
                    self.log.debug('Conref not replaced: ' + conrefUsed)
                    if conrefUsed not in conrefErrors:
                        conrefErrors.append(conrefUsed)
        attempts = attempts + 1

    conrefErrors = list(dict.fromkeys(conrefErrors))
    for conrefError in conrefErrors:
        if 'ME_ignore' in str(conrefError):
            continue
        if ' ' in str(conrefError):
            continue
        if '\n' in str(conrefError):
            conrefError = str(conrefError).split('\n', 1)[0]
        addToWarnings(str(conrefError) + ' is detected, but was not found in ' + details["reuse_phrases_file"] +
                      '. Check for typos, remove the reference, or add to ' + details["reuse_phrases_file"] +
                      '.', folderAndFile, folderPath + file_name, details, self.log, self.location_name, conrefError, topicContents)

    topicContents = topicContents.replace(ignoreText, ignoreTextStandard)
    for conref in conrefJSON:
        if '_COMMENT' not in conref:

            conrefName = conref.replace('{', '').replace('[', '').replace(']', '').replace('}', '')

            if topicContents.count('{[' + conrefName + ']}') > 0:
                addToWarnings(str('{[' + conrefName + ']}') + ' was not replaced.', folderAndFile,
                              folderPath + file_name, details, self.log, self.location_name, '{[' + conrefName + ']}', topicContents)

            elif topicContents.count('{[' + conrefName + ']') > 0:
                addToErrors(str('{[' + conrefName + ']') + ' was not replaced because of a missing curly brace.',
                            folderAndFile, folderPath + file_name, details, self.log, self.location_name,
                            '{[' + conrefName + ']', topicContents)

            elif topicContents.count('[' + conrefName + ']}') > 0:
                addToErrors(str('[' + conrefName + ']}') + ' was not replaced because of a missing curly brace.',
                            folderAndFile, folderPath + file_name, details, self.log, self.location_name,
                            '[' + conrefName + ']}', topicContents)

            if topicContents.count('{{' + conrefName + '}}') > 0:
                addToErrors(str('{{' + conrefName + '}}') + ' was not replaced because the wrong formatting was used.',
                            folderAndFile, folderPath + file_name, details, self.log, self.location_name,
                            '{{' + conrefName + '}}', topicContents)

    return (topicContents)
