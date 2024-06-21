#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def gatherUsedImages(self, details, imagePath, topicContents):

    import os

    from mdenricher.errorHandling.errorHandling import addToWarnings

    def processImageName(self, imageName, imagePathUnique):
        if '../' in imageName:
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
        if not imagePathUnique + imageName in self.imagesUsedInThisBuild:
            self.imagesUsedInThisBuild.append(imagePathUnique + imageName)

        return (self.imagesUsedInThisBuild)

    import re

    # /subfolder/a-test.md
    # ../images/icloud.png
    # ../images/icloud.png

    # Remove HTML comments to not collect image names in comments.
    # Blockchain had an instance of an image name in a comment and that image did not exist in the repo.
    htmlComments1 = re.findall('<!--(.*?)-->', topicContents, flags=re.DOTALL)
    htmlComments2 = re.findall('<!--(.*)-->', topicContents, flags=re.DOTALL)
    htmlComments = htmlComments1 + htmlComments2
    for htmlComment in htmlComments:
        topicContents = topicContents.replace(htmlComment, '')

    # Get images in HTML format
    htmlImages = re.findall(r'<img.*?/>', topicContents)
    htmlImages = list(dict.fromkeys(htmlImages))

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
    if ((not os.path.isdir(self.location_dir + '/images')) and
            (not self.imagesUsedInThisBuild == []) and self.location_ibm_cloud_docs is True):
        addToWarnings('Images were found in the repo, but they were not stored in a single ' +
                      '/images/ directory in the root of the repo.', '/images/', '', details, self.log,
                      self.location_name, '', '')

    return (self.imagesUsedInThisBuild)
