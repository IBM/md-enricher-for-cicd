#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def gatherUsedImages(self, details, imagePath, sourceFile, topicContents):

    # import os

    # from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.cleanupEachFile.createTestTopicContents import createTestTopicContents

    def processImageName(self, imageName, imagePathUnique):
        if not imageName.startswith('http'):
            if (details['ibm_cloud_docs'] is True) and ('../icons' in imageName):
                self.log.debug('Not processing IBM Cloud Docs icons: ' + imageName)
            else:
                originalImageName = imageName
                if '../' in imageName:
                    # ../images in the conref.md file can go outside of the repo
                    # since it can be reused in content that is in a subdirectory
                    if (details['ibm_cloud_docs'] is True) and ('conref.md' in sourceFile) and ('/images/' in imageName):
                        imageName = imageName.replace('../', '')
                    while '../' in imageName:
                        imageName = imageName.replace('../', '', 1)
                        imagePathUnique = imagePathUnique.rsplit('/', 1)[0]
                if imageName.startswith('./'):
                    imageName = imageName[1:]
                if '?raw=true' in imageName:
                    imageName = imageName.replace('?raw=true', '')
                if imageName.startswith('/'):
                    imageName = imageName[1:]
                if not imagePathUnique.startswith('/'):
                    imagePathUnique = '/' + imagePathUnique
                if not imagePathUnique.endswith('/'):
                    imagePathUnique = imagePathUnique + '/'

                try:
                    self.imagesUsedInThisBuild[imagePathUnique + imageName]
                except Exception:
                    self.imagesUsedInThisBuild[imagePathUnique + imageName] = {}

                try:
                    self.imagesUsedInThisBuild[imagePathUnique + imageName][originalImageName]
                except Exception:
                    self.imagesUsedInThisBuild[imagePathUnique + imageName][originalImageName] = {}

                try:
                    self.imagesUsedInThisBuild[imagePathUnique + imageName][originalImageName]['files']
                except Exception:
                    self.imagesUsedInThisBuild[imagePathUnique + imageName][originalImageName]['files'] = []

                if sourceFile not in self.imagesUsedInThisBuild[imagePathUnique + imageName][originalImageName]['files']:
                    self.imagesUsedInThisBuild[imagePathUnique + imageName][originalImageName]['files'].append(sourceFile.split(self.location_dir)[1])

        return (self.imagesUsedInThisBuild)

    import re

    # /subfolder/a-test.md
    # ../images/icloud.png

    topicContents, htmlCodeErrors, codeblockErrors, codephraseErrors, htmlCodeBlocks, codeblocks, codephrases = createTestTopicContents(topicContents)

    if codeblockErrors > 0:
        self.log.debug(sourceFile + ' contains code block errors, so code blocks and phrases cannot be removed before checking images.')
    if codephraseErrors > 0:
        self.log.debug(sourceFile + ' contains code phrase errors, so code phrases cannot be removed before checking images.')
    if htmlCodeErrors > 0:
        self.log.debug(sourceFile + ' contains HTML code errors, so code cannot be removed before checking images.')

    # Get images in HTML format
    htmlImages = re.findall(r'<img.*?/>', topicContents)
    htmlImages = list(dict.fromkeys(htmlImages))

    htmlImagesNoEndSlash = re.findall(r'<img.*?>', topicContents)
    htmlImagesNoEndSlash = list(dict.fromkeys(htmlImagesNoEndSlash))

    htmlImages = htmlImages + htmlImagesNoEndSlash

    # Get images from JSON
    jsonImages = re.findall(r'"thumbnail": ".*?"', topicContents)
    jsonImages = list(dict.fromkeys(jsonImages))

    # Replace all markdown alt text with nothing just in case there are parens in the alt text before getting images in markdown format
    markdownAltTexts = re.findall(r'\!\[.*?\]', topicContents)
    for markdownAltText in markdownAltTexts:
        topicContents = topicContents.replace(markdownAltText, '!')
    # Get images in markdown format
    markdownImages = re.findall(r'\!\(.*?\)', topicContents)
    markdownImages = list(dict.fromkeys(markdownImages))

    # If the image name is used in the content, then copy the image over
    for htmlImage in htmlImages:
        if 'src=\\"' in htmlImage:
            htmlImage = htmlImage.replace('\\"', '"')
        imageName = htmlImage.split('src="', 1)[1]
        imageName = imageName.split('"', 1)[0]

        self.imagesUsedInThisBuild = processImageName(self, imageName, imagePath)

    # "./non-existent-image.png"
    for markdownImage in markdownImages:
        # Don't check videos that use image markdown styling
        if not markdownImage + '{: video output="iframe"' in topicContents:
            imageName = markdownImage.split('(', 1)[1]
            if ' "' in imageName:
                imageName = imageName.split(' "', 1)[0]
            else:
                imageName = imageName.split(')', 1)[0]
            self.imagesUsedInThisBuild = processImageName(self, imageName, imagePath)

    for jsonImage in jsonImages:
        imageName = jsonImage.split('"',)[3]
        self.imagesUsedInThisBuild = processImageName(self, imageName, imagePath)

    # If images are not all stored in the /images directory, issue a warning
    # if ((not os.path.isdir(self.location_dir + '/images')) and
    # (not self.imagesUsedInThisBuild == {}) and (self.location_ibm_cloud_docs is True)):
    # addToWarnings('Images were found in the repo, but they were not all stored in a single ' +
    # '/images/ directory in the root of the repo.', '/images/', '', details, self.log,
    # self.location_name, '', '')

    return (self.imagesUsedInThisBuild)
