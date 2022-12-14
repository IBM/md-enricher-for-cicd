#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def copySourceImage(self, details, imageFileName, imgOutputDir):
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
                        if os.path.isfile(self.location_dir + '/' + imgOutputDir + '/' + imgSource):
                            os.remove(self.location_dir + '/' + imgOutputDir + '/' + imgSource)
                        # Copy the new version of the image
                        shutil.copy(details["source_dir"] + '/' + imgSource, imgOutputDir)
                        # self.log.debug(imgSourceLong + ': Copying source file')
                    # else:
                        # self.log.debug(imgSource + ': Up to date already')


def copyImage(self, details, imageFileName):
    import os
    import shutil
    from errorHandling.errorHandling import addToWarnings

    # In staging or if the image is used in a supported image file, then the image is copied over
    # self.log.debug("image name: " + imageFileName)
    imgOutputDir = imageFileName.rsplit('/', 1)[0]
    if imgOutputDir.startswith('/'):
        imgOutputDir = imgOutputDir[1:]

    imgOutputDir = (imgOutputDir.replace('../', ''))
    # self.log.debug("image imgOutputDir: " + imgOutputDir)
    imageFileNameNotRelative = imageFileName.replace('../', '')
    if not imageFileNameNotRelative.startswith('/'):
        imageFileNameNotRelative = '/' + imageFileNameNotRelative
    if not os.path.isdir(self.location_dir + '/' + imgOutputDir + '/'):
        os.makedirs(self.location_dir + '/' + imgOutputDir + '/')

    if imageFileName.endswith(tuple(details["img_output_filetypes"])):
        # Delete the old version
        if os.path.isfile(self.location_dir + imageFileNameNotRelative):
            self.log.debug('Removing old version: ' + imageFileNameNotRelative)
            os.remove(self.location_dir + '/' + imageFileNameNotRelative)
        # Copy the new version
        if os.path.isfile(details["source_dir"] + imageFileNameNotRelative):
            shutil.copy(details["source_dir"] + imageFileNameNotRelative, self.location_dir + '/' + imgOutputDir + '/')
            self.log.debug('Copying: ' + imageFileNameNotRelative)
            from images.imagesUsed import copySourceImage
            copySourceImage(self, details, imageFileNameNotRelative, self.location_dir + '/' + imgOutputDir + '/')
        else:
            addToWarnings(imageFileName + ': Does not exist in the referenced path (as ' +
                          imageFileNameNotRelative + ').', imageFileName, imageFileNameNotRelative, details, self.log,
                          self.location_name, imageFileName, '')


def imagesUsed(self, details, file_name, folderAndFile, folderPath, topicContents):

    import os
    import re
    from errorHandling.errorHandling import addToWarnings
    # from errorHandling.errorHandling import addToErrors
    # from setup.exitBuild import exitBuild

    def imageNameHandling(imageName):
        if '"' in imageName:
            imageName = imageName.replace('"', '')
        if imageName.startswith('./'):
            imageName = imageName.replace('./', '', 1)
        if imageName.startswith('/'):
            imageName = imageName[1:]
        return (imageName)

    def imageCheck(imageName):
        imageNameVerified = 'False'
        os.chdir(self.location_dir + folderPath)
        # self.log.info('Checking in ' + self.location_dir + folderPath)
        # self.log.debug('imageName: ' + imageName)
        if imageName.startswith('http'):
            imageNameVerified = 'http'
        elif os.path.isfile(imageName):
            self.log.debug('Image path verified: ' + imageName)
            imageNameVerified = 'True'
        else:
            # Look through the list of images found and see if that image is even there to compare against
            for image in self.image_files_list:
                if '/' in imageName:
                    imageNameShort = imageName.rsplit('/', 1)[1]
                else:
                    imageNameShort = imageName
                if image.endswith('/' + imageNameShort):
                    # Compare the file path of the image from the list of all images with the filepath of the markdown file
                    # and see if the suggested relative path between those two files matches the image path used in the
                    # markdown file
                    # self.log.debug('imageNameShort from all images list: ' + imageNameShort)
                    # self.log.debug('Comparing: ' + self.location_dir + image)
                    # self.log.debug('With: ' + self.location_dir + folderPath)
                    expectedRelativePath = os.path.relpath(self.location_dir + image, self.location_dir + folderPath)
                    # self.log.debug('expectedRelativePath: ' + expectedRelativePath)
                    if expectedRelativePath == imageName:
                        self.log.debug('Image path verified: ' + imageName)
                        imageNameVerified = 'True'
                        break
        if imageNameVerified == 'http':
            self.log.debug('Not checking HTTP images: ' + imageName)
        elif imageNameVerified == 'True':
            copyImage(self, details, imageName)
        else:
            addToWarnings(imageName + ': Does not exist in the referenced path.', folderAndFile, folderPath + file_name, details, self.log,
                          self.location_name, imageName, topicContents)
        os.chdir(self.location_dir)

    # This allows writers to only put images in the root images directory,
    # then if they're used in the files in the CLI/subrepo, then they'll get automatically copied over

    # Create the images dir in the downstream repo if it doesn't exist already
    # TO DO: Handle all images wherever they are, regardless of whether or not there's a root images directory.
    # Probably should be if is anything in the self.image_files_list list
    # TO DO: Need to remove the imgOutputDir directory bit so that the path matches whatever is in source in the location
    # TO DO: If you remove an image in the markdown, the image does not get removed downstream from the images directory.
    if not self.image_files_list == []:

        # /subfolder/a-test.md
        # ../images/icloud.png
        # Get the subdirectory path to resolve the image path used in the file
        # relativeFilePath = ((folderPath + file_name).rsplit('/', 1)[0]) + '/'
        # /subfolder
        # /vpc/networking

        if os.path.isfile(self.location_dir + folderPath + file_name):
            fileName_open = open(self.location_dir + folderPath + file_name, 'r', encoding="utf8", errors="ignore")
            imgTextCheck = fileName_open.read()
            fileName_open.close()

            # Remove HTML comments for collecting image names.
            # Blockchain had an instance of an image name in a comment and that image did not exist in the repo.
            htmlComments1 = re.findall('<!--(.*?)-->', imgTextCheck, flags=re.DOTALL)
            htmlComments2 = re.findall('<!--(.*)-->', imgTextCheck, flags=re.DOTALL)
            htmlComments = htmlComments1 + htmlComments2
            for htmlComment in htmlComments:
                imgTextCheck = imgTextCheck.replace(htmlComment, '')

            # If the image name is used in the content, then copy the image over
            # Added or for removing the first slash just in case the writer didn't include it

            # Get images in HTML format
            htmlImages = re.findall(r'<img.*?/>', imgTextCheck)
            htmlImages = list(dict.fromkeys(htmlImages))

            # Get images from landing.json
            jsonImages = re.findall(r'"thumbnail": ".*?"', imgTextCheck)
            jsonImages = list(dict.fromkeys(jsonImages))

            # Replace all markdown alt text with nothing just in case there are parens in the alt text before getting images in markdown format
            markdownAltTexts = re.findall(r'\!\[.*?\]', imgTextCheck)
            for markdownAltText in markdownAltTexts:
                imgTextCheck = imgTextCheck.replace(markdownAltText, '!')
            # Get images in markdown format
            markdownImages = re.findall(r'\!\(.*?\)', imgTextCheck)
            markdownImages = list(dict.fromkeys(markdownImages))

            for htmlImage in htmlImages:
                if 'src=\\"' in htmlImage:
                    htmlImage = htmlImage.replace('\\"', '"')
                imageName = htmlImage.split('src="', 1)[1]
                imageName = imageName.split('"', 1)[0]

                # TO DO: Should this icons dir condition only apply to IBM Cloud
                if '../icons' not in imageName:
                    imageName = imageNameHandling(imageName)
                    if imageName.endswith(tuple(details["img_output_filetypes"])):
                        imageCheck(imageName)

            # "./non-existent-image.png"
            for markdownImage in markdownImages:
                # Don't check videos that use image markdown styling
                if not markdownImage + '{: video output="iframe"' in imgTextCheck:
                    imageName = markdownImage.split('(', 1)[1]
                    if '../icons' not in imageName:
                        if ' "' in imageName:
                            imageName = imageName.split(' "', 1)[0]
                        else:
                            imageName = imageName.split(')', 1)[0]
                        imageName = imageNameHandling(imageName)
                        if imageName.endswith(tuple(details["img_output_filetypes"])):
                            imageCheck(imageName)

            for jsonImage in jsonImages:
                imageName = jsonImage.split('"',)[3]
                if '../icons' not in imageName:
                    imageName = imageNameHandling(imageName)
                    if imageName.endswith(tuple(details["img_output_filetypes"])):
                        imageCheck(imageName)
