#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def htmlValidator(self, details, file_name, folderAndFile, folderPath, topicContents):

    # Check to make sure there are no unhandled tags left behind

    import re

    from mdenricher.cleanupEachFile.createTestTopicContents import createTestTopicContents
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

    def errorFound(folderAndFile, errorTag, topicContentsCheck):

        if not errorTag == '`' and not errorTag == '<->' and not errorTag == '<-->':
            # solution-tutorials uses <->
            # Check if the error is a defined tag, if so make it an error, otherwise warning
            errorTagSlim = errorTag.replace('<', '').replace('>', '').replace('/', '')
            if (errorTagSlim in self.tags_show) or (errorTagSlim in self.tags_hide):
                addToErrors(errorTag + ' tag not removed or handled properly. ', folderAndFile, folderPath + file_name,
                            details, self.log, self.location_name, errorTag, topicContentsCheck)
            elif '_' in errorTagSlim:
                self.log.debug('Underscore in tags indicates a variable instead of a tag: ' + errorTagSlim)
            elif errorTagSlim == 'value' or errorTagSlim == 'username' or errorTagSlim == 'password':
                self.log.debug('Common variable names used and interpreted as a variable instead of a tag: ' + errorTagSlim)
            else:
                addToWarnings(errorTag + ' appears to be a tag and is not removed or handled properly. ', folderAndFile, folderPath + file_name,
                              details, self.log, self.location_name, errorTag, topicContentsCheck)

    def check(topicContents, folderPath, file_name, tag):

        validInstances = []

        if ((tag in validHtmlTags) or (tag[1:] in validHtmlTags) or (tag.replace(' ', '') in validHtmlTags)):
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

        (topicContentsCodeCheck, htmlCodeErrors, codeblockErrors, codephraseErrors,
            htmlCodeList, mdCodeblockList, mdInlineCodeList) = createTestTopicContents(topicContents, file_name)

        mdCodeList = mdCodeblockList + mdInlineCodeList

        if ((file_name.endswith('.md')) and
                (topicContentsCodeCheck.count('\n# ') > 1) and
                (not file_name == 'conref.md') and
                ('content-type: api-docs' not in topicContents)):
            addToWarnings('Too many H1 headings.', folderAndFile, folderPath + file_name, details, self.log,
                          self.location_name, '', topicContents)

        if htmlCodeErrors > 0:
            topicContentsCodeCheckLines = topicContentsCodeCheck.split('\n')
            for line in topicContentsCodeCheckLines:
                if '<code' in line or '</code)' in line:
                    if '<code>' in line:
                        tag = '<code>'
                    elif '</code>' in line:
                        tag = '</code>'
                    else:
                        tag = '<code'
                    head, sep, tail = line.partition(tag)
                    try:
                        if (head[-10:] + tag + tail[10]) in topicContents:
                            errantPhrase = head[-10:] + tag + tail[10]
                        elif (not head[-10:] == '') and ((head[-10:] + tag) in topicContents):
                            errantPhrase = head[-10:] + tag
                        elif (tail[10] == '') and ((tag + tail[10]) in topicContents):
                            errantPhrase = tag + tail[10]
                        else:
                            errantPhrase = line[0:50]
                    except Exception:
                        errantPhrase = line
                    addToWarnings('HTML code block issue. Check for an incomplete code blocks in ' + ': ' + errantPhrase, folderAndFile,
                                  folderPath + file_name, details, self.log, self.location_name, '', topicContents)

        if codeblockErrors > 0:
            addToWarnings('Markdown code block issue. Check for an incomplete code blocks.', folderAndFile,
                          folderPath + file_name, details, self.log, self.location_name, '', topicContents)

        if codephraseErrors > 0:
            topicContentsCodeCheckLines = topicContentsCodeCheck.split('\n')
            for line in topicContentsCodeCheckLines:
                if '`' in line:
                    head, sep, tail = line.partition('`')
                    try:
                        if (head[-10:] + "`" + tail[10]) in topicContents:
                            errantPhrase = head[-10:] + "`" + tail[10]
                        elif (not head[-10:] == '') and ((head[-10:] + "`") in topicContents):
                            errantPhrase = head[-10:] + "`"
                        elif (tail[10] == '') and (("`" + tail[10]) in topicContents):
                            errantPhrase = "`" + tail[10]
                        else:
                            errantPhrase = line[0:50]
                    except Exception:
                        errantPhrase = line
                    addToWarnings('Missing code tick. Check for an incomplete code phrase in ' + ': ' + errantPhrase, folderAndFile,
                                  folderPath + file_name, details, self.log, self.location_name, errantPhrase, topicContents)

        if htmlCodeErrors == 0 and codeblockErrors == 0:
            # If the number of backticks is correct, then check for the rest of the issues
            potentialTagList = re.findall('<(.*?)>', topicContentsCodeCheck, flags=re.DOTALL)
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
                    check(topicContents, folderPath, file_name, potentialTag)
