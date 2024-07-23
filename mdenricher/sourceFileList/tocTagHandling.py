def tocTagHandling(log, details, all_files_original, tagList):

    from mdenricher.errorHandling.errorHandling import addToErrors
    import copy
    import re

    all_files_revised = copy.deepcopy(all_files_original)

    tocTopicContents = all_files_original['/toc.yaml']['fileContents']

    fileList = {}  # type: ignore[var-annotated]

    for tagItem in tagList:
        tag, tagLocations = tagItem.split(':')
        taggedContent: list[str] = []  # type: ignore[misc]
        singleLines = re.findall('<' + tag + '>' + '(.*?)' + '</' + tag + '>', tocTopicContents)
        multiLines = re.findall('<' + tag + '>' + '(.*?)' + '</' + tag + '>', tocTopicContents, flags=re.DOTALL)

        taggedContent = singleLines + multiLines
        for taggedSection in taggedContent:
            taggedLines = taggedSection.split('\n')
            for taggedLine in taggedLines:
                while taggedLine.endswith(' '):
                    taggedLine = taggedLine[:-1]
                if 'include:' not in str(taggedLine):
                    taggedNoSpaces = taggedLine.split(' ')
                    for taggedLineNoSpaces in taggedNoSpaces:
                        taggedLineNoSpaces = '/' + taggedLineNoSpaces
                        if taggedLineNoSpaces.endswith(tuple(details['filetypes'])):
                            try:
                                fileList[taggedLineNoSpaces]
                            except Exception:
                                fileList[taggedLineNoSpaces] = {}
                            try:
                                fileList[taggedLineNoSpaces]['locations']
                            except Exception:
                                fileList[taggedLineNoSpaces]['locations'] = []
                            try:
                                fileList[taggedLineNoSpaces]['tagsInTOC']
                            except Exception:
                                fileList[taggedLineNoSpaces]['tagsInTOC'] = []

                            if ', ' in tagLocations:
                                tagLocationList = tagLocations.split(', ')
                            elif ',' in tagLocations:
                                tagLocationList = tagLocations.split(',')
                            else:
                                tagLocationList = [tagLocations]
                            for location in tagLocationList:
                                if location not in fileList[taggedLineNoSpaces]['locations']:
                                    fileList[taggedLineNoSpaces]['locations'].append(location)
                            if tag not in fileList[taggedLineNoSpaces]['tagsInTOC']:
                                fileList[taggedLineNoSpaces]['tagsInTOC'].append(tag)

    for file in fileList:

        try:
            applyTag = True
            originalFileContents = all_files_original[file]['fileContents']
            if originalFileContents.startswith('<') and originalFileContents.endswith('>'):
                firstTag, originalFileContents = originalFileContents.split('>', 1)
                firstTag = firstTag.replace('<', '')
                originalFileContents = originalFileContents.rsplit('<', 1)[0]
                if firstTag in fileList[file]['tagsInTOC']:
                    applyTag = False
                else:
                    for tagPossibility in tagList:
                        if tagPossibility.startswith(firstTag + ':'):
                            tagPossibilityLocations = tagPossibility.split(':')[1]
                            tagPossibilityLocationsList = tagPossibilityLocations.split(',')
                            break
                    if tagPossibilityLocationsList == fileList[file]['locations']:
                        applyTag = False
                    else:
                        applyTag = False
                        addToErrors('The ' + ','.join(fileList[file]['tagsInTOC']) + ' tag in the toc.yaml and the ' + firstTag + ' tag in the ' +
                                    file + ' file conflict.', file, '',
                                    details, log, 'source', '', '')
        except Exception:
            addToErrors(file + ' is referenced in the TOC, but the file does not exist.', 'toc.yaml', '',
                        details, log, 'source', '', '')
        else:
            try:
                if applyTag is True:
                    newContent = ''
                    for tag in fileList[file]['locations']:
                        # tocTag=draft, fileTag=draft
                        if not '<' + tag + '>' + originalFileContents + '</' + tag + '>' in newContent:
                            newContent = newContent + '<' + tag + '>' + originalFileContents + '</' + tag + '>'
                            log.debug('Adding ' + tag + ' tag around /' + file + ' file contents.')
                    all_files_revised[file]['fileContents'] = newContent
            except Exception:
                log.debug('Cannot change the tagging.')

    return (all_files_revised)
