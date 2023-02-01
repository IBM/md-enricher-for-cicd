#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def getSourceResults(log, outputContents, sourceContents):

    # Get a diff of the source and output files

    import difflib

    sourceContentsSplit = sourceContents.splitlines()
    topicContentsSplit = outputContents.splitlines()
    line_formatter = '{:3d}  {}'.format
    source_lines = [line_formatter(i, line) for i, line in enumerate(sourceContentsSplit, 1)]
    output_lines = [line_formatter(i, line) for i, line in enumerate(topicContentsSplit, 1)]
    results = difflib.Differ().compare(source_lines, output_lines)
    return (results)


def checkResults(errantPhrase, errantPhraseFound, line, log, results):

    # Get a line number of the issue from the source file, then write to the warnings or errors file

    sourceLineNumber = ''
    for resultLine in results:
        # See if the whole line matches
        if (line in resultLine) and (resultLine.startswith('-')):
            lineRevised = resultLine.replace('-', '', 1)
            while lineRevised.startswith(' '):
                lineRevised = lineRevised[1:]
            sourceLineNumber = "#L" + (lineRevised.split(' ', 1)[0])
            errantPhraseFound = True
            break
        # See if the errant phrase is in any removed line
        if errantPhraseFound is False:
            if (errantPhrase in resultLine) and (resultLine.startswith('-')):
                lineRevised = resultLine.replace('-', '', 1)
                while lineRevised.startswith(' '):
                    lineRevised = lineRevised[1:]
                sourceLineNumber = "#L" + (lineRevised.split(' ', 1)[0])
                errantPhraseFound = True
                break
        # Do not look in added lines because it will be in the output
        # See if the errant phrase is in any line at all
        if errantPhraseFound is False:
            if errantPhrase in resultLine and (not resultLine.startswith('+')):
                while resultLine.startswith(' '):
                    resultLine = resultLine[1:]
                sourceLineNumber = "#L" + (resultLine.split(' ', 1)[0])
                errantPhraseFound = True
                break

    return (errantPhraseFound, sourceLineNumber)


def writeIssue(issueType, issueTypeFile, message, folderAndFile, folderPlusFile, details, log, stages, errantPhrase, topicContents):

    # Figure out if the problem is in a reused file piece or not

    import os
    import re
    # One problem with getting the output line numbers is that the logs branch is used rather than the commit

    # Get line numbers
    sourceLineNumber = ''
    outputLineNumber = ''
    lineFound = ''
    if not topicContents == '' and not errantPhrase == '':
        # Get the line number of the problem in the output file
        errantPhraseFound = False
        linesAssignedNumbers = []
        for lineNumber, line in enumerate(topicContents.split('\n'), 1):
            linesAssignedNumbers.append('#L' + str(lineNumber) + ': ' + line)
            if errantPhrase in line:
                outputLineNumber = "#L" + str(lineNumber)
                errantPhraseFound = True
                lineFound = line
        # Check which snippets are used, if the output line number is within a snippet, then use that as the source file
        if (errantPhraseFound is True) and ('{[' not in errantPhrase):
            if '<!--Snippet ' in topicContents:
                linesTopicContents = "\n".join(linesAssignedNumbers)
                snippetStarts = re.findall(r"<!--Snippet .*? start-->", linesTopicContents)
                allSnippets = []
                for snippet in snippetStarts:
                    snippetName = snippet.split(' ')[1]
                    snippetsFound = re.findall("<!--Snippet " + snippetName + " start-->.*?<!--Snippet " + snippetName +
                                               " end-->", linesTopicContents, flags=re.DOTALL)
                    for snippetFound in snippetsFound:
                        allSnippets.append(snippetFound)
                # Too many commas - join together and then split on ends
                allSnippetsJoined = "".join(allSnippets)
                allSnippetsJoined = allSnippetsJoined.replace(',', '&comma;')
                allSnippetsSplit = allSnippetsJoined.split('end-->')

                withinASnippet = 'False'
                for snippet in allSnippetsSplit:
                    if (outputLineNumber in snippet) and (errantPhrase.replace(',', '&comma;') in snippet):
                        withinASnippet = re.findall(r"<!--Snippet .*? start-->", snippet)[0]
                        withinASnippet = withinASnippet.split(' ')[1]
                        break

                if withinASnippet != 'False':
                    if '.md' in withinASnippet:
                        folderAndFile = '/' + details["reuse_snippets_folder"] + withinASnippet
                    else:
                        folderAndFile = '/' + details["reuse_snippets_folder"] + '/' + details["reuse_phrases_file"]

        # Get the line number of the problem in the source file
        if os.path.isfile(details["source_dir"] + folderAndFile):

            # Get a diff of the two files
            with open(details["source_dir"] + folderAndFile, "r") as file1:
                sourceTopicContents = file1.read()
                errantPhraseFound = False
                while errantPhrase.startswith('../'):
                    errantPhrase = errantPhrase[3:]
                if errantPhrase in sourceTopicContents:
                    results = getSourceResults(log, topicContents, sourceTopicContents)
                    errantPhraseFound = True

            if errantPhraseFound is True and sourceLineNumber == '':
                errantPhraseFound, sourceLineNumber = checkResults(errantPhrase, False, lineFound, log, results)

    # Check if the error is already in the file so it's not duplicated
    issueFileSplit = []
    if os.path.isfile(issueTypeFile):
        with open(issueTypeFile, 'r', encoding="utf8") as file_open1:
            file_open1Open = file_open1.read()
            issueFileSplit = file_open1Open.split('\n\n')

    issueAlreadyAdded = False
    for issue in issueFileSplit:
        if (((('File: ' + folderAndFile) in issue) or
                (('Source: ' + folderAndFile) in issue) or
                (("|" + folderAndFile + ">") in issue)) and
                (('Description: ' + message) in issue)):
            issueAlreadyAdded = True
            break

    # Add the issue to the file
    if issueAlreadyAdded is False:
        with open(issueTypeFile, 'a+', encoding="utf8") as file_open:
            if folderAndFile.endswith('.md'):
                if ',' in stages:
                    stage = stages.split(',')[0]
                else:
                    stage = stages
                if details["builder"] == 'local':
                    outputURL = stage + ' output: ' + folderPlusFile + ' ' + outputLineNumber
                    sourceURL = "Source: " + folderAndFile + ' ' + sourceLineNumber
                else:
                    outputURL = ('Output: <https://' + str(details["source_github_domain"]) + "/" +
                                 str(details["source_github_org"]) + "/" + str(details["source_github_repo"]) +
                                 "/edit/" + str(details["log_branch"]) + '/' + stage + folderPlusFile +
                                 outputLineNumber + "|" + folderPlusFile + "> " + outputLineNumber)
                    sourceURL = ('Source: <https://' + str(details["source_github_domain"]) + "/" +
                                 str(details["source_github_org"]) + "/" + str(details["source_github_repo"]) +
                                 "/edit/" + str(details["current_github_branch"] + folderAndFile + sourceLineNumber +
                                                "|" + folderAndFile + "> " + sourceLineNumber))
                file_open.write('\n\n\n' + issueType.upper() + ':\n' + outputURL + "\n" + sourceURL +
                                '\nDescription: ' + message + '\n\n' + errantPhrase)
            else:
                file_open.write('\n\n\n' + issueType.upper() + ':\nFile: ' + folderAndFile + '\nDescription: ' + message + '\n\n' + errantPhrase)


def addToErrors(errorMessage, folderAndFile, folderPlusFile, details, log, buildStage, errantPhrase, topicContents):
    log.error(errorMessage)
    writeIssue('error', details["error_file"], errorMessage, folderAndFile, folderPlusFile, details, log, buildStage, errantPhrase, topicContents)


def addToWarnings(warningMessage, folderAndFile, folderPlusFile, details, log, buildStage, errantPhrase,
                  topicContents):
    log.warning(warningMessage)
    writeIssue('warning', details["warning_file"], warningMessage, folderAndFile, folderPlusFile, details, log, buildStage, errantPhrase, topicContents)
