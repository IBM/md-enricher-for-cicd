#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def checkUsedImages(self, details):

    import os
    import shutil

    from mdenricher.errorHandling.errorHandling import addToErrors
    from mdenricher.images.gatherUsedImages import gatherUsedImages

    self.imagesUsedInThisBuild = []

    self.log.debug('\n\nImage usage check:')

    # Get a list of all used images across all supported filetypes
    for (path, dirs, files) in os.walk(self.location_dir):
        for entry in files:
            if entry.endswith(tuple(details["filetypes"])) and os.path.isfile(path + '/' + entry) and ('.git' not in path):
                with open(path + '/' + entry, 'r', encoding="utf8", errors="ignore") as fileName_open:
                    topicContentsCheckImages = fileName_open.read()
                self.imagesUsedInThisBuild = gatherUsedImages(self, details, path, topicContentsCheckImages)

    # Go through the original list of images in the source directory and compare it against the used images list
    for upstreamImage in self.image_files_list:
        upstreamShortName = upstreamImage.replace(details["source_dir"], '')
        try:
            downstreamShortName = self.all_files_dict[upstreamShortName]['folderPath'] + self.all_files_dict[upstreamShortName]['file_name']
        except Exception:
            self.log.error('Image does not exist: ' + upstreamShortName)
        downstreamImage = self.location_dir + downstreamShortName
        if downstreamImage in self.imagesUsedInThisBuild:
            if not os.path.isdir(self.location_dir + self.all_files_dict[upstreamShortName]['folderPath']):
                try:
                    os.makedirs(self.location_dir + self.all_files_dict[upstreamShortName]['folderPath'])
                except Exception:
                    if os.path.isfile(self.location_dir + self.all_files_dict[upstreamShortName]['folderPath']):
                        os.remove(self.location_dir + self.all_files_dict[upstreamShortName]['folderPath'])
                        os.makedirs(self.location_dir + self.all_files_dict[upstreamShortName]['folderPath'])
                    if not os.path.isdir(self.location_dir + self.all_files_dict[upstreamShortName]['folderPath']):
                        addToErrors('Could not create directory: ' + self.location_dir + self.all_files_dict[upstreamShortName]['folderPath'],
                                    upstreamShortName, downstreamShortName, details, self.log, self.location_name,
                                    '', '')
            shutil.copy(upstreamImage, self.location_dir + self.all_files_dict[upstreamShortName]['folderPath'])
            self.log.debug(upstreamShortName + ': Copied downstream because it is used in a downstream content file.')
        else:
            if os.path.isfile(downstreamImage):
                self.log.debug(upstreamShortName + ': Removing from ' + self.location_dir + ' because it is not used in a downstream content file.')
                os.remove(downstreamImage)
            else:
                self.log.debug(upstreamShortName + ' is not used in a downstream content file.')
