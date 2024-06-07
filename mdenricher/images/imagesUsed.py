#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def copySourceImage(self, details, imageFileName, imgOutputDir):

    # Copy the source image downstream

    import os
    import shutil
    # If a supported image file is copied over, check for its source file to copy over too.
    # Mainly for translation packaging.
    # List of source file types that will be checked for
    for sourceImgType in details["img_src_filetypes"]:
        # If we're working with a file type, don't check for that file type again, like svg
        if sourceImgType not in imageFileName:
            # Get the name of the image, remove the old extension, and add the source file type
            imgSource = (imageFileName.split('.', 1)[0]) + sourceImgType
            # Do the same thing with the folder and image name
            # imgSourceLong = (imageFileName.split('.', 1)[0]) + sourceImgType
            if os.path.isfile(details["source_dir"] + imgSource):
                if not os.path.isfile(self.location_dir + imgSource):
                    shutil.copy(details["source_dir"] + '/' + imgSource, imgOutputDir)
                    # self.log.debug(imgSourceLong + ': Copying source file')
                else:
                    imageTimeStampMain = str(os.path.getmtime(details["source_dir"] + imgSource))
                    imageTimeStampOtherRepo = str(os.path.getmtime(self.location_dir + imgSource))
                    oldTimeStamp = float(imageTimeStampMain)
                    newTimeStamp = float(imageTimeStampOtherRepo)
                    if float(newTimeStamp) > float(oldTimeStamp):
                        # Remove the old version of the file
                        if os.path.isfile(self.location_dir + imgOutputDir + imgSource):
                            os.remove(self.location_dir + imgOutputDir + imgSource)
                        # Copy the new version of the image
                        shutil.copy(details["source_dir"] + '/' + imgSource, imgOutputDir)
                        # self.log.debug(imgSourceLong + ': Copying source file')
                    # else:
                        # self.log.debug(imgSource + ': Up to date already')


def copyImage(self, details, file_name, folderAndFile, folderPath):

    # Copy the image downstream

    import os
    import shutil
    from mdenricher.errorHandling.errorHandling import addToWarnings

    # In staging or if the image is used in a supported image file, then the image is copied over
    # self.log.debug("image name: " + imageFileName)
    if not os.path.isdir(self.location_dir + folderPath):
        os.makedirs(self.location_dir + folderPath)

    # Delete the old version
    if os.path.isfile(self.location_dir + folderPath + file_name):
        self.log.debug('Removing old version: ' + self.location_dir + folderPath + file_name)
        os.remove(self.location_dir + folderPath + file_name)
    # Copy the new version
    if os.path.isfile(details['source_dir'] + folderAndFile):
        shutil.copy(details['source_dir'] + folderAndFile, self.location_dir + folderPath)
        self.log.debug('Copying: ' + details['source_dir'] + folderAndFile + ' to ' + self.location_dir + folderPath + file_name)
        # from mdenricher.images.imagesUsed import copySourceImage
        # copySourceImage(self, details, folderPath + file_name, self.location_dir + folderPath)
    else:
        addToWarnings(folderPath + file_name + ': Does not exist at ' +
                      details['source_dir'] + folderAndFile, folderPath + file_name, folderPath + file_name, details, self.log,
                      self.location_name, folderPath + file_name, '')


def imagesUsed(self, details, file_name, folderAndFile, folderPath, topicContents):

    import os
    import re
    # from mdenricher.errorHandling.errorHandling import addToWarnings
    # from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.setup.exitBuild import exitBuild

    def imageNameHandling(imageName):
        if '"' in imageName:
            imageName = imageName.replace('"', '')
        if imageName.startswith('./'):
            imageName = imageName.replace('./', '', 1)
        if imageName.startswith('/'):
            imageName = imageName[1:]
        return (imageName)

    def imageCheck(imageNameOriginal):
        if imageNameOriginal.endswith(tuple(details["img_output_filetypes"])):

            imageName = imageNameHandling(imageNameOriginal)
            # imageNameVerified = 'False'
            if not imageName.startswith('http'):
                # imageNameVerified = 'http'
                # else:
                # Get the folder path and file name of the image referenced
                if '/' in imageName:
                    img_folderPath, img_file_name = imageName.rsplit('/', 1)
                else:
                    img_file_name = imageName
                    img_folderPath = '/'
                expectedFolderPath = folderAndFile.rsplit('/', 1)[0]
                if '../' in img_folderPath:
                    while '../' in img_folderPath:
                        img_folderPath = img_folderPath.replace('../', '', 1)
                        expectedFolderPath = expectedFolderPath.rsplit('/', 1)[0]
                if not img_folderPath.startswith('/'):
                    img_folderPath = '/' + img_folderPath
                if not img_folderPath.endswith('/'):
                    img_folderPath = img_folderPath + '/'
                imgfolderAndFile = expectedFolderPath + img_folderPath + img_file_name

                # if imgfolderAndFile in self.image_files_list:
                if os.path.isfile(details['source_dir'] + imgfolderAndFile):
                    copyImage(self, details, img_file_name, imgfolderAndFile, expectedFolderPath + img_folderPath)
                    # imageNameVerified = 'True'

            # if imageNameVerified == 'False':
            # addToWarnings(imageNameOriginal + ' does not exist.', folderAndFile, folderPath + file_name, details, self.log,
            # self.location_name, imageNameOriginal, topicContents)

    if not self.image_files_list == []:

        # /subfolder/a-test.md
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

        # Get images from landing.json
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

            if '../icons' not in imageName:
                imageCheck(imageName)

        # "./non-existent-image.png"
        for markdownImage in markdownImages:
            # Don't check videos that use image markdown styling
            if not markdownImage + '{: video output="iframe"' in topicContents:
                imageName = markdownImage.split('(', 1)[1]
                if '../icons' not in imageName:
                    if ' "' in imageName:
                        imageName = imageName.split(' "', 1)[0]
                    else:
                        imageName = imageName.split(')', 1)[0]
                    imageCheck(imageName)

        for jsonImage in jsonImages:
            imageName = jsonImage.split('"',)[3]
            if '../icons' not in imageName:
                imageCheck(imageName)
