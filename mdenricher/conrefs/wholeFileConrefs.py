#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def wholeFileConrefs(self, details, file_name, folderAndFile, folderPath, topicContents):

    # Replace the conrefs that are in their own .md file.
    # Added the loop count just in case a conref .md file is being called
    # that doesn't actually exist in the conrefs directory

    import re
    import os

    from mdenricher.errorHandling.errorHandling import addToWarnings
    # from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.setup.exitBuild import exitBuild

    loopCount = 0

    if '.md]}' in topicContents:

        # Don't transform snippets in comments
        if '<!--' in topicContents:
            commentList = re.findall('<!--(.*?)-->', topicContents, flags=re.DOTALL)
            for comment in commentList:
                conrefsUsedList = re.findall(r"\{\[.*?.md\]\}", topicContents)
                if not conrefsUsedList == []:
                    for conrefUsed in conrefsUsedList:
                        conrefUsedDoNotTransform = conrefUsed.replace('{[', '{[<!--Do not transform-->')
                        commentDoNotTransform = comment.replace(conrefUsed, conrefUsedDoNotTransform)
                        topicContents = topicContents.replace(comment, commentDoNotTransform)

        while '.md]}' in topicContents:
            snippetsUsedList = re.findall(r"\{\[.*?.md\]\}", topicContents)
            snippetsUsedList = list(dict.fromkeys(snippetsUsedList))
            for snippet in snippetsUsedList:
                if 'Do not transform' in snippet:
                    continue
                # This is getting picked up sometimes: {[SatStorage]} | {[def-storage.md]}
                if ' ' in snippet:
                    snippetsWithSpaces = snippet.split(' ')
                    for snippetWithSpace in snippetsWithSpaces:
                        if '{[' in snippetWithSpace and '.md]}' in snippetWithSpace:
                            snippet = snippetWithSpace
                            break
                conrefFileName = snippet.replace('{[', '').replace(']}', '')
                if os.path.isfile(details["source_dir"] + '/' + details["reuse_snippets_folder"] + '/' +
                                  conrefFileName):
                    conrefFile = open(details["source_dir"] + '/' + details["reuse_snippets_folder"] + '/' +
                                      conrefFileName, 'r', encoding="utf8", errors="ignore")
                    conrefFileContents = conrefFile.read()
                    # Remove newline from the end of the file contents. It messes up tables.
                    if conrefFileContents.endswith('\n'):
                        conrefFileContents = conrefFileContents[:-1]
                    if snippet in conrefFileContents:
                        conrefFileContents = conrefFileContents.replace(snippet, '')
                    topicContents = topicContents.replace(snippet, '<!--Snippet ' + str(conrefFileName) + ' start-->' +
                                                          conrefFileContents + '<!--Snippet ' + str(conrefFileName) +
                                                          ' end-->')
            loopCount = loopCount + 1
            if (loopCount > 100) or ('.md]}' not in topicContents):
                break

    if '.md]}' in topicContents:
        errantMDConrefs = re.findall(r"\{\[.*?\.md\]\}", topicContents)
        mdConrefErrors = ''
        mdConrefErrorsSlack = ''
        for errantMDConref in errantMDConrefs:
            if 'Do not transform' in errantMDConref:
                continue
            if '\n' in errantMDConref:
                errantMDConrefList = errantMDConref.split('\n')
                for newLineSection in errantMDConrefList:
                    if '.md]}' in newLineSection:
                        errantMDConref = newLineSection
                        break
            if ' ' in errantMDConref:
                continue
            if errantMDConref not in mdConrefErrors:
                mdConrefErrors = mdConrefErrors + ',' + errantMDConref

                addToWarnings(errantMDConref + ' is detected, but a matching file could not be found in the ' + details["reuse_snippets_folder"] +
                              ' directory. Check if there is a .md file that is used in this file that does not ' +
                              'actually exist in the ' + details["reuse_snippets_folder"] + ' directory.', folderAndFile, folderPath + file_name,
                              details, self.log, self.location_name, errantMDConref, topicContents)

                lineNumber = '1'
                with open(details["source_dir"] + folderAndFile, 'r+', encoding="utf8") as sourceFile_read:
                    for num, line in enumerate(sourceFile_read, 1):
                        if errantMDConref in line:
                            lineNumber = str(num)
                            break

                if self.location_output_action == 'none':
                    mdConrefErrorsSlack = mdConrefErrorsSlack + errantMDConref + ', ' + folderAndFile + ' L' + lineNumber + '\n'
                else:
                    mdConrefErrorsSlack = (mdConrefErrorsSlack + errantMDConref + ', ' + "<https://" +
                                           details["source_github_domain"] + "/" + details["source_github_org"] + "/" +
                                           details["source_github_repo"] + "/edit/" + details["current_github_branch"] + "/"
                                           + folderAndFile + "#L" + lineNumber + "|" + folderAndFile + ' L' + lineNumber +
                                           '>\n')

    return (topicContents)
