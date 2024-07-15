def createTestTopicContents(topicContents):

    import re

    codeblockErrors = 0
    codephraseErrors = 0
    htmlCodeErrors = 0

    htmlComments1 = re.findall('<!--.*?-->', topicContents, flags=re.DOTALL)
    htmlComments2 = re.findall('<!--.*-->', topicContents, flags=re.DOTALL)
    removedSections = htmlComments1 + htmlComments2
    for removedSection in removedSections:
        topicContents = topicContents.replace(removedSection, '')

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
