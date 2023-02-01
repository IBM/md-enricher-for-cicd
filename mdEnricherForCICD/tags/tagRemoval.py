#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def tagRemoval(self, details, folderAndFile, folderPath, file_name, tags_hide, tags_show, topicContents):

    # Remove the opening tags, closing tags, and maybe the content within them

    # Beautiful soup does not work for our purposes here because they don't preserve
    # newlines and they sort attributes alphabetically, both of which make it impossible to
    # find the text in the document to replace
    # https://bugs.launchpad.net/beautifulsoup/+bug/1589227
    # https://bugs.launchpad.net/beautifulsoup/+bug/1812422

    import re  # for doing finds within the topic content

    # from errorHandling.errorHandling import addToWarnings
    from errorHandling.errorHandling import addToErrors
    # from setup.exitBuild import exitBuild

    def sectionLoop(details, closedTag, openTag, sectionList, topicContents):
        for section in sectionList:
            # Seems like only this first section is getting hit, which is good
            if ((openTag not in section) and (closedTag not in section)):
                topicContents = topicContents.replace(openTag + section + closedTag, '')
            elif openTag in section:
                section = section.split(openTag, 1)[1]
                if closedTag in section:
                    section = section.split(closedTag, 1)[0]
                topicContents = topicContents.replace(openTag + section + closedTag, '')
                # self.log.debug(openTag + ': Removing if 2: ' + section)
            elif closedTag in section:
                section = section.split(closedTag, 1)[0]
                topicContents = topicContents.replace(openTag + section + closedTag, '')
                # self.log.debug(openTag + ': Removing if 3: ' + section)
            else:
                addToErrors(openTag + ': Could not handle' + section, folderAndFile, '', details, self.log, self.location_name, openTag, topicContents)
        return (topicContents)

    if '</' in topicContents:

        self.log.debug('Handling tags in ' + folderAndFile + '.')

        for tagName in tags_hide:
            openTag = '<' + tagName + '>'
            closedTag = '</' + tagName + '>'

            # Remove tags and content that should not display. Example: <prod>Some text</prod>
            if openTag in topicContents or closedTag in topicContents:
                loopCount = 0
                while loopCount < 6:
                    loopCount = loopCount + 1

                    # Get and replace all of the single line tags first
                    sectionList = re.findall(openTag + '(.*?)' + closedTag, topicContents)

                    # while not sectionList == []:
                    topicContents = sectionLoop(details, closedTag, openTag, sectionList, topicContents)

                    # Double check for single line phrases
                    sectionList = re.findall(openTag + '(.*?)' + closedTag, topicContents, flags=re.DOTALL)
                    topicContents = sectionLoop(details, closedTag, openTag, sectionList, topicContents)

                    # Get and replace all of the multi-line tags
                    sectionList = re.findall(openTag + '(.*)' + closedTag, topicContents)
                    topicContents = sectionLoop(details, closedTag, openTag, sectionList, topicContents)

                    # Double check for multi-line phrases
                    sectionList = re.findall(openTag + '(.*)' + closedTag, topicContents, flags=re.DOTALL)
                    topicContents = sectionLoop(details, closedTag, openTag, sectionList, topicContents)

            '''
            # Moved error handling solely to htmlValidator
            if openTag in topicContents:
                addToErrors(openTag + ' not handled properly. A closing tag might be missing.', folderAndFile,
                            folderPath + file_name, details, self.log, self.location_name, openTag, topicContents)

            if closedTag in topicContents:
                addToErrors(closedTag + ' not handled properly. An opening tag might be missing.', folderAndFile,
                            folderPath + file_name, details, self.log, self.location_name, closedTag, topicContents)
            '''

        for tagName in tags_show:
            openTag = '<' + tagName + '>'
            closedTag = '</' + tagName + '>'

            if ((openTag in topicContents) or (closedTag in topicContents)):

                # Replace all of the tags but leave the content within them
                topicContents = re.sub(openTag, '', topicContents, flags=re.DOTALL)
                topicContents = re.sub(closedTag, '', topicContents, flags=re.DOTALL)

    else:
        self.log.debug('No tags in this file to handle.')

    return (topicContents)
