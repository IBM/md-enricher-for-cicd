#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def inlineConrefs(self, details, conrefJSON, file_name, folderAndFile, folderPath, topicContents):

    # Replace short conrefs that are in reuse_phrases_file

    import re

    from mdenricher.errorHandling.errorHandling import addToWarnings
    # from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.setup.exitBuild import exitBuild

    # Get a list of all of the conrefs that are used in the file in the Doctopus styling
    attempts = 0
    # Need to run through some topics multiple times because some inline conrefs contain other inline conrefs
    conrefErrors = []

    # Don't transform snippets in comments
    if '<!--' in topicContents:
        commentList = re.findall('<!--(.*?)-->', topicContents, flags=re.DOTALL)
        for comment in commentList:
            conrefsUsedList = re.findall(r"\{\[.*?(?!\.md)\]\}", comment)
            if not conrefsUsedList == []:
                for conrefUsed in conrefsUsedList:
                    conrefUsedDoNotTransform = conrefUsed.replace('{[', '{[<!--Do not transform-->')
                    commentDoNotTransform = comment.replace(conrefUsed, conrefUsedDoNotTransform)
                    topicContents = topicContents.replace(comment, commentDoNotTransform)

    while attempts < 15:

        if ']}' not in topicContents:
            break

        # Find all reuse that does not have .md in it
        # This seems to still be pulling in the .md instances
        conrefsUsedList = re.findall(r"\{\[.*?(?!\.md)\]\}", topicContents)

        '''
        for conrefUsed in conrefsUsedList:
            formattingCount = conrefUsed.count('{[')
            if formattingCount > 1:
                self.log.debug(conrefUsed + ' has too many')
                conrefsUsedList.remove(conrefUsed)
                while '{[' in conrefUsed:
                    first, conrefUsed = conrefUsed.split('{[', 1)
                    if first.endswith(']}'):
                        conrefsUsedList.append('{[' + first)
                        self.log.debug('Appending ' + '{[' + first)
                    self.log.debug('conrefUsed: ' + conrefUsed)
                if conrefUsed.startswith('{[') and conrefUsed.endswith(']}'):
                        conrefsUsedList.append(conrefUsed)

        '''

        if conrefsUsedList == [] or conrefsUsedList == ['{[FIRST_ANCHOR]}']:
            break

        # Remove duplicates from the list
        conrefsUsedList = list(dict.fromkeys(conrefsUsedList))

        # Go through all of the conrefs found. Ignore the .md or core team ones.
        for conrefUsed in conrefsUsedList:
            if ('.md' not in conrefUsed) and ('<!--Do not transform-->' not in conrefUsed):
                conrefFileName = conrefUsed.replace('{[', '').replace(']}', '')
                if (('site.data' not in conrefUsed) and ('FIRST_ANCHOR' not in conrefUsed)):
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

                            if (('{[' + conrefFileName + ']}') in topicContents):
                                if (conrefUsed not in conrefErrors):
                                    conrefErrors.append(conrefUsed)

                        # If the conref fails, it probably was removed and this instance just wasn't removed from the content.
                        # Add it to a list of possible errant conrefs.
                        except Exception:
                            self.log.debug('Conref not replaced: ' + conrefUsed)
                            if conrefUsed not in conrefErrors:
                                conrefErrors.append(conrefUsed)
                elif '.' in conrefUsed:
                    addToWarnings(str(conrefUsed) + ' is detected, but does not have a .md extension. '
                                  'Convert the file to a markdown file or add the text to the ' + details["reuse_phrases_file"] +
                                  ' file instead.', folderAndFile, folderPath + file_name, details, self.log, self.location_name, conrefUsed, topicContents)
        attempts = attempts + 1

    conrefErrors = list(dict.fromkeys(conrefErrors))
    for conrefError in conrefErrors:
        if 'Do not transform' in str(conrefError):
            continue
        if ' ' in str(conrefError):
            continue
        if '\n' in str(conrefError):
            conrefError = str(conrefError).split('\n', 1)[0]
        addToWarnings(str(conrefError) + ' is detected, but was not found in ' + details["reuse_phrases_file"] +
                      '. Check for typos, remove the reference, or add to ' + details["reuse_phrases_file"] +
                      '.', folderAndFile, folderPath + file_name, details, self.log, self.location_name, conrefError, topicContents)

    return (topicContents)
