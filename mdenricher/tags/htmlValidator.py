#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def htmlValidator(self, details, file_name, folderAndFile, folderPath, topicContents):

    # Check to make sure there are no unhandled tags left behind

    import re

    from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.setup.exitBuild import exitBuild

    validHtmlTags = ["/a", "a", "abbr", "acronym", "address", "area", "article", "b", "base", "bdo", "big",
                     "blockquote", "body", "/br", "br", "br /", "br/", "button", "caption", "cite", "code",
                     "codeblock", "col", "colgroup", "dd", "del", "details", "dfn", "diagram", "div", "dl", "DOCTYPE",
                     "dt", "em", "fieldset", "fig", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5",
                     "h6", "head", "html", "hr", "hr/", "i", "img", "iframe", "input", "ins", "kbd", "label", "legend", "li",
                     "link", "main", "map", "meta", "mxfile", "noscript", "object", "ol", "optgroup", "option", "p",
                     "p=\"note\"", "param", "ph", "pre", "q", "samp", "script", "section", "select", "small", "span",
                     "strong", "style", "sub", "summary", "sup", "table", "tbody", "td", "textarea", "tfoot", "th",
                     "thead", "title", "tr", "tt", "ul", "var", "varname", "wintitle"]

    validHtmlTagsWithSpaces = []
    for validHtmlTag in validHtmlTags:
        validHtmlTagsWithSpaces.append(validHtmlTag + ' ')

    def errorFound(folderAndFile, errorTag, topicContentsCheck):

        # Removed the guess about where the instance was in the text since that's handled later to get the line
        '''
        instances = topicContentsCheck.count(errorTag)

        topicContentsSplit = topicContentsCheck.splitlines()
        lineNumber = 0
        lineNumberList = ''
        instanceNumber = 0
        for line in topicContentsSplit:
            lineNumber = lineNumber + 1
            if errorTag in line:
                instanceNumber = instanceNumber + 1
                partitioned_string = line.partition(errorTag)
                beforeError = partitioned_string[0]
                if len(beforeError) > 50:
                    beforeError = beforeError[-50]
                afterError = partitioned_string[2]
                if len(afterError) > 50:
                    afterError = afterError[50]
                lineAbbr = '#' + str(instanceNumber) + '. ' + beforeError + errorTag + afterError

                if lineNumberList == '':
                    lineNumberList = lineAbbr
                else:
                    lineNumberList = lineNumberList + ', ' + lineAbbr
        '''

        if not errorTag == '`':
            # Check if the error is a defined tag, if so make it an error, otherwise warning
            errorTagSlim = errorTag.replace('<', '').replace('>', '').replace('/', '')
            if (errorTagSlim in self.tags_show) or (errorTagSlim in self.tags_hide):
                addToErrors(errorTag + ' not removed or handled properly. ', folderAndFile, folderPath + file_name,
                            details, self.log, self.location_name, errorTag, topicContentsCheck)
            else:
                addToWarnings(errorTag + ' not removed or handled properly. ', folderAndFile, folderPath + file_name,
                              details, self.log, self.location_name, errorTag, topicContentsCheck)

    def check(topicContents, folderPath, file_name, htmlCodeList, tag):

        validInstances = []

        if ((tag in validHtmlTags) or (tag[1:] in validHtmlTags) or tag.startswith(tuple(validHtmlTagsWithSpaces))):
            validInstances.append(tag)
        elif ((tag in TAGS_HIDE_AND_SHOW) or (tag[1:] in TAGS_HIDE_AND_SHOW)):
            errorFound(folderAndFile, '<' + tag + '>', topicContents)
        elif ('!--') in tag:
            validInstances.append(tag)
        elif ('<' + tag + '>') in str(htmlCodeList):
            addToWarnings('Variables in HTML code must use &lt/;' + tag + '&gt/;, not <' + tag + '>', folderAndFile,
                          folderPath + file_name, details, self.log, self.location_name, '<' + tag + '>',
                          topicContents)
        elif ('<' + tag + '>') in str(mdCodeList):
            validInstances.append(tag)
        # elif ((('<' + tag + '>') in str(mdCodeList)) or (('<' + tag + ' ') in str(mdCodeList)) or (('<' + tag) in str(mdCodeList))):
            # validInstances.append(tag)
        elif ('<' + tag) in str(mdCodeList):
            addToWarnings('Variable needs >: ' + tag.split('\n', 1)[0], folderAndFile, folderPath + file_name,
                          details, self.log, self.location_name, '<' + tag, topicContents)
        elif ((tag.startswith('/')) and (('<' + tag + '>') in topicContents)):
            errorFound(folderAndFile, '<' + tag + '>', topicContents)
        elif tag not in topicContents:
            addToWarnings('Variable not handled properly: ' + tag, folderAndFile, folderPath + file_name, details,
                          self.log, self.location_name, tag, topicContents)
            with open(self.variableFile, 'a+', encoding="utf8", errors="ignore") as variableFile_open:
                if not self.location_output_action == 'none':
                    variableFile_open.write("<https://" + details["source_github_domain"] + "/" +
                                            details["source_github_org"] + "/" + details["source_github_repo"] +
                                            "/edit/" + details["current_github_branch"] + "/" +
                                            folderAndFile + "|" + folderAndFile + '>: ' + tag + ' (<https://' +
                                            self.location_github_domain + "/" + self.location_github_org + "/" +
                                            self.location_github_repo + '/edit/' + self.location_github_branch + folderPath + file_name + "|" +
                                            self.location_name + " output)>: " + '\n')
                else:
                    variableFile_open.write(folderAndFile + ': ' + tag + ' (' + self.location_name + " output)\n")
        elif '\n' in tag:
            tagSplit = tag.split('\n', 1)[0]
            tagSplit = '<' + tagSplit + '\\n'
            if tagSplit in str(mdCodeList):
                validInstances.append(tag)
            else:
                addToWarnings('Variable needs >: ' + tagSplit, folderAndFile, folderPath + file_name, details, self.log, self.location_name, '', '')
        else:
            errorFound(folderAndFile, '<' + tag + '>', topicContents)

    TAGS_HIDE_AND_SHOW = self.tags_hide + self.tags_show

    if not ('/' + details["reuse_snippets_folder"] + '/') in folderPath:

        # 1. Make sure there are an even number of code blocks. This will help determine if the problem is with the code blocks or code phrases.
        instances = topicContents.count('```')
        if not (instances % 2) == 0:
            addToWarnings('There are ' + str(instances) +
                          ' code block tags. ' +
                          'Check if there is a code block missing a closing tag.', folderAndFile,
                          folderPath + file_name, details, self.log, self.location_name, '', '')
        else:
            # 2. Check for correct code ticks, because otherwise the results are inccurate.

            # Get a list of the codeblocks
            mdCodeblockList = re.findall('```(.*?)```', topicContents, flags=re.DOTALL)

            # Get a list of code phrases from a version of the topicContents that DO NOT have the code blocks in them.
            # There are instances in satellite where there are backticks in code blocks.
            # This makes sure that that doesn't mess up our list of code phrases.
            topicContentsCodeCheck = topicContents
            for codeListItem in mdCodeblockList:
                topicContentsCodeCheck = topicContentsCodeCheck.replace('```' + codeListItem + '```', '')

            # Check for uneven number of single ticks
            instancesSingle = topicContentsCodeCheck.count('`')
            if not (instancesSingle % 2) == 0:
                # Try to figure out where the errant code tick is
                inlineCodePhrases = re.findall('`(.*?)`', topicContentsCodeCheck)
                for phrase in inlineCodePhrases:
                    topicContentsCodeCheck = topicContentsCodeCheck.replace('`' + phrase + '`', '')
                topicContentsCodeCheckLines = topicContentsCodeCheck.split('\n')
                for line in topicContentsCodeCheckLines:
                    if '`' in line:
                        head, sep, tail = line.partition('`')
                        break
                try:
                    if (head[-10:] + "`" + tail[10]) in topicContents:
                        errantPhrase = head[-10:] + "`" + tail[10]
                    elif (not head[-10:] == '') and ((head[-10:] + "`") in topicContents):
                        errantPhrase = head[-10:] + "`"
                    elif (tail[10] == '') and (("`" + tail[10]) in topicContents):
                        errantPhrase = "`" + tail[10]
                    else:
                        errantPhrase = ''
                except Exception:
                    errantPhrase = ''
                addToWarnings('Missing code tick. Check for an incomplete code phrase in: ' + line, folderAndFile,
                              folderPath + file_name, details, self.log, self.location_name, errantPhrase, topicContents)

            mdInlineCodeList = re.findall('`(.*?)`', topicContentsCodeCheck, flags=re.DOTALL)
            # Combine the code blocks and code phrases into one list
            mdCodeList = mdCodeblockList + mdInlineCodeList

            htmlCodeList = []
            # pre and codeblocks aren't necessary because they both have code tags within them
            codeList = re.findall('<code(.*?)</code>', topicContents, flags=re.DOTALL)
            for codeListItem in codeList:
                htmlCodeList.append(codeListItem)

            # Get a version of the topicContents that now does not have code blocks or code ticks in it
            mdInlineCodeList2 = re.findall('`(.*?)`', topicContentsCodeCheck, flags=re.DOTALL)
            for codeListItem in mdInlineCodeList2:
                topicContentsCodeCheck = topicContentsCodeCheck.replace('`' + codeListItem + '`', '')

            # Get a version of the topicContents that now does not have HTML code blocks and phrases in it either
            codeList2 = re.findall('<code(.*?)</code>', topicContentsCodeCheck, flags=re.DOTALL)
            for codeListItem in codeList2:
                topicContentsCodeCheck = topicContentsCodeCheck.replace('<code' + codeListItem + '</code>', '')

            codeErrorFound = False
            if 'code>' in topicContentsCodeCheck:
                codeErrorFound = True
                errorCodeTag = 'code>'
                errorFound(folderAndFile, errorCodeTag, topicContentsCodeCheck)
            if '`' in topicContentsCodeCheck:
                codeErrorFound = True
                errorCodeTag = '`'
                errorFound(folderAndFile, errorCodeTag, topicContentsCodeCheck)

            # If the number of backticks is correct, then check for the rest of the issues
            if codeErrorFound is False:
                potentialTagList = re.findall('<(.*?)>', topicContents, flags=re.DOTALL)
                potentialTagList = list(dict.fromkeys(potentialTagList))

                for potentialTag in sorted(potentialTagList):
                    if ((not potentialTag == '') and (' ' not in potentialTag) and ('</code' not in potentialTag)):
                        # pattern = '(!<code>)<[/]?' + potentialTag + '>(!</code>)'  # or anything else
                        # for m in re.finditer(pattern, topicContents):
                        # self.log.debug(m.group(0))
                        # start = m.start()
                        # lineno = topicContents.count('\n', 0, start) + 1
                        # offset = start - topicContents.rfind('\n', 0, start)
                        # try:
                        # word = m.group(1)
                        # self.log.debug("(%s,%s): %s" % (lineno, offset, word))
                        # except Exception:
                        # self.log.debug('Exception')
                        check(topicContents, folderPath, file_name, htmlCodeList, potentialTag)
