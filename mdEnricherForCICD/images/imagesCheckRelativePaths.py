#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def imagesCheckRelativePaths(self, details, file_name, folderAndFile, folderPath, topicContents):

    # TO DO: Need better looping in here

    import re

    if ((not details["reuse_snippets_folder"] in folderAndFile)):

        slashesCount = folderPath.count('/')

        if slashesCount > 1:

            # Should thumbnails for the landing.json files be added too? Those files should be in the root directory anyhow, so this shouldn't apply.

            # Check the filepath for HTML images and image maps
            htmlImages = re.findall(r'<img.*?/>', topicContents)
            if not htmlImages == []:
                for htmlImage in htmlImages:
                    # TO DO: Should these be ignoring relatives???
                    if (("images/" in htmlImage) and ("../images" not in htmlImage)):
                        relativePathCount = slashesCount - 1
                        relativePath = relativePathCount*'../'
                        replacementFound = False
                        if '"images' in htmlImage:
                            htmlImageFixed = htmlImage.replace('"images', '"' + relativePath + 'images')
                            replacementFound = True
                        elif '"/images' in htmlImage:
                            htmlImageFixed = htmlImage.replace('"/images', '"' + relativePath + 'images')
                            replacementFound = True
                        if replacementFound is True:
                            self.log.debug('Image was not relative: ' + htmlImage + ' in ' + folderPath + file_name +
                                           '. Fixed to ' + htmlImageFixed + '.')
                            topicContents = topicContents.replace(htmlImage, htmlImageFixed)

            # Check the filepath for markdown images
            markdownImages = re.findall(r'\!\[.*?\)', topicContents)
            if not markdownImages == []:
                for markdownImage in markdownImages:
                    if (("images/" in markdownImage) and ("../images" not in markdownImage)):
                        relativePathCount = slashesCount - 1
                        relativePath = relativePathCount*'../'
                        replacementFound = False
                        if '(/images' in markdownImage:
                            markdownImageFixed = markdownImage.replace('(/images', '(' + relativePath + 'images')
                            replacementFound = True
                        elif '(images' in markdownImage:
                            markdownImageFixed = markdownImage.replace('(images', '(' + relativePath + 'images')
                            replacementFound = True
                        if replacementFound is True:
                            self.log.debug('Image was not relative: ' + markdownImage + ' in ' + folderPath + file_name +
                                           '. Fixed to ' + markdownImageFixed + '.')
                            topicContents = topicContents.replace(markdownImage, markdownImageFixed)
        elif slashesCount == 1:

            htmlImages = re.findall(r'<img.*?/>', topicContents)
            if not htmlImages == []:
                for htmlImage in htmlImages:
                    if ("../images" in htmlImage):
                        htmlImageFixed = htmlImage.replace('"../images', '"images')
                        self.log.debug('Image was not relative: ' + htmlImage + ' in ' + folderPath + file_name +
                                       '. Fixed to ' + htmlImageFixed + '.')
                        topicContents = topicContents.replace(htmlImage, htmlImageFixed)

            markdownImages = re.findall(r'\!\[.*?\)', topicContents)
            if not markdownImages == []:
                for markdownImage in markdownImages:
                    if ("../images" in markdownImage):
                        markdownImageFixed = markdownImage.replace('(../images', '(images')
                        self.log.debug('Image was not relative: ' + markdownImage + ' in ' + folderPath + file_name +
                                       '. Fixed to ' + markdownImageFixed + '.')
                        topicContents = topicContents.replace(markdownImage, markdownImageFixed)

    return (topicContents)
