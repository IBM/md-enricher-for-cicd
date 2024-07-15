def tocTagHandling(log, details, all_files_original, tagList):

    from mdenricher.errorHandling.errorHandling import addToErrors
    import copy

    all_files_revised = copy.deepcopy(all_files_original)

    tocTopicContents = all_files_original['/toc.yaml']['fileContents']

    fileList = {}  # type: ignore[var-annotated]

    for tagItem in tagList:
        tag, tagLocations = tagItem.split(':')
        taggedContent: list[str] = []  # type: ignore[misc]
        splitOnEnds = tocTopicContents.split('</' + tag + '>')
        for splitOnEnd in splitOnEnds:
            if '<' + tag + '>' in splitOnEnd:
                isolatedContent = splitOnEnd.split('<' + tag + '>')[1]
                taggedContent.append(isolatedContent)
        for taggedSection in taggedContent:
            taggedLines = taggedSection.split('\n')
            for taggedLine in taggedLines:
                while taggedLine.endswith(' '):
                    taggedLine = taggedLine[:-1]
                taggedNoSpaces = taggedLine.split(' ')
                for taggedLineNoSpaces in taggedNoSpaces:
                    if taggedLineNoSpaces.endswith(tuple(details['filetypes'])):
                        try:
                            fileList[taggedLineNoSpaces]
                        except Exception:
                            fileList[taggedLineNoSpaces] = {}
                        try:
                            fileList[taggedLineNoSpaces]['locations']
                        except Exception:
                            fileList[taggedLineNoSpaces]['locations'] = []
                        if ', ' in tagLocations:
                            tagLocationList = tagLocations.split(', ')
                        elif ',' in tagLocations:
                            tagLocationList = tagLocations.split(',')
                        else:
                            tagLocationList = [tagLocations]
                        for location in tagLocationList:
                            if location not in fileList[taggedLineNoSpaces]['locations']:
                                fileList[taggedLineNoSpaces]['locations'].append(location)

    for file in fileList:

        try:
            errorFound = False
            originalFileContents = all_files_original['/' + file]['fileContents']
            if originalFileContents.startswith('<') and originalFileContents.endswith('>'):
                firstTag, originalFileContents = originalFileContents.split('>', 1)
                firstTag = firstTag.replace('<', '')
                originalFileContents = originalFileContents.rsplit('<', 1)[0]
                if firstTag not in fileList[file]['locations']:
                    errorFound = True
                    addToErrors('The tags in the toc.yaml and the ' + firstTag + ' tag in the ' + '/' +
                                file + ' file conflict.', '/' + file, '',
                                details, log, 'source', '', '')
        except Exception:
            pass
        else:
            try:
                if errorFound is False:
                    newContent = ''
                    for tag in fileList[file]['locations']:
                        # tocTag=draft, fileTag=draft
                        if not '<' + tag + '>' + originalFileContents + '</' + tag + '>' in newContent:
                            newContent = newContent + '<' + tag + '>' + originalFileContents + '</' + tag + '>'
                            log.debug('Adding ' + tag + ' tag around /' + file + ' file contents.')
                    all_files_revised['/' + file]['fileContents'] = newContent
            except Exception:
                log.debug('Cannot change the tagging.')

    return (all_files_revised)
