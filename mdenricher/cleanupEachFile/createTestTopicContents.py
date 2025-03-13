def createTestTopicContents(topicContents, file_name):

    import re

    codeblockErrors = 0
    codephraseErrors = 0
    htmlCodeErrors = 0

    htmlComments1 = re.findall('<!--.*?-->', topicContents)  # inline comments
    for removedSection in htmlComments1:
        topicContents = topicContents.replace(removedSection, '')

    htmlComments2 = re.findall('<!--.*?-->', topicContents, flags=re.DOTALL)
    for removedSection in htmlComments2:
        topicContents = topicContents.replace(removedSection, '')

    htmlComments3 = re.findall('<!--.*-->', topicContents)  # inline comments
    for removedSection in htmlComments3:
        topicContents = topicContents.replace(removedSection, '')

    htmlComments4 = re.findall('<!--.*-->', topicContents, flags=re.DOTALL)
    for removedSection in htmlComments4:
        topicContents = topicContents.replace(removedSection, '')

    # Replace YAML header in MD if it has comments
    # Tags will not be checked in this removed section
    if file_name.endswith('.md'):
        removeYAMLFromMDs = re.findall('---.*?---', topicContents, flags=re.DOTALL)
        try:
            if '#' in removeYAMLFromMDs[0]:
                topicContents = topicContents.replace(removeYAMLFromMDs[0], '')
        except Exception:
            pass

    # Remove fours
    codeTickCountFours = topicContents.count('````')
    codeblocksFours = re.findall('````.*?````', topicContents, flags=re.DOTALL)
    if (codeTickCountFours % 2) == 0:
        for codeblock in codeblocksFours:
            topicContents = topicContents.replace(codeblock, '')
    else:
        codeblockErrors = codeblockErrors + 1
        topicContents = topicContents.replace('````', '')

    # Replace threes
    codeTickCount = topicContents.count('```')
    codeblocks = re.findall('```.*?```', topicContents, flags=re.DOTALL)
    if (codeTickCount % 2) == 0:
        for codeblock in codeblocks:
            topicContents = topicContents.replace(codeblock, '')
    else:
        codeblockErrors = codeblockErrors + 1
        topicContents = topicContents.replace('```', '')

    # Replace twos
    codeTickCount = topicContents.count('``')
    codeblocks = re.findall('``.*?``', topicContents)
    if (codeTickCount % 2) == 0:
        for codeblock in codeblocks:
            topicContents = topicContents.replace(codeblock, '')
    else:
        codephraseErrors = codephraseErrors + 1
        topicContents = topicContents.replace('``', '')

    # Replace ones
    codeTickCount = topicContents.count('`')
    codephrases = re.findall('`.*?`', topicContents)
    for codephrase in codephrases:
        topicContents = topicContents.replace(codephrase, '')
    if not (codeTickCount % 2) == 0:
        codeTickCount = topicContents.count('`')
        codephraseErrors = codephraseErrors + codeTickCount

    # Replace HTML
    codeStartCount = topicContents.count('<code')
    codeEndCount = topicContents.count('</code>')
    htmlCodeBlocksOneLine = re.findall('<code.*?</code>', topicContents)
    for codeblock in htmlCodeBlocksOneLine:
        topicContents = topicContents.replace(codeblock, '')
    htmlCodeBlocks = re.findall('<code.*?</code>', topicContents, flags=re.DOTALL)
    if codeStartCount == codeEndCount:
        for codeblock in htmlCodeBlocks:
            topicContents = topicContents.replace(codeblock, '')
    else:
        htmlCodeErrors = 1

    return (topicContents, htmlCodeErrors, codeblockErrors, codephraseErrors, htmlCodeBlocks, codeblocks, codephrases)
