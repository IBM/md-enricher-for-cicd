#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def checkUsedImages(self, details):

    try:
        import os
        import shutil

        from mdenricher.errorHandling.errorHandling import addToErrors
        from mdenricher.errorHandling.errorHandling import addToWarnings
        from mdenricher.images.gatherUsedImages import gatherUsedImages

        self.imagesUsedInThisBuild = {}
        self.unusedInThisLocation = []

        self.log.debug('\n\nImage usage check:')

        # Get a list of all used images across all supported filetypes
        filesChecked = []
        for (path, dirs, files) in os.walk(self.location_dir):
            for entry in files:
                if entry.endswith(tuple(details["filetypes"])) and os.path.isfile(path + '/' + entry) and ('.git' not in path):
                    with open(path + '/' + entry, 'r', encoding="utf8", errors="ignore") as fileName_open:
                        topicContentsCheckImages = fileName_open.read()
                    self.imagesUsedInThisBuild = gatherUsedImages(self, details, path, path + '/' + entry, topicContentsCheckImages)
                    filesChecked.append(path + '/' + entry)

        if not filesChecked == [] and not filesChecked == [self.location_dir + '/README.md']:
            # Go through the original list of images in the source directory and compare it against the used images list
            usedInThisLocation = []
            for upstreamImage in self.image_files_list:
                upstreamShortName = upstreamImage.replace(details["source_dir"], '')
                try:
                    downstreamShortName = self.all_files_dict[upstreamShortName]['folderPath'] + self.all_files_dict[upstreamShortName]['file_name']
                except Exception:
                    self.log.debug('Image not handled: ' + upstreamImage + ' (upstream)')
                else:
                    downstreamImage = self.location_dir + downstreamShortName

                    if ((downstreamImage in str(self.imagesUsedInThisBuild) and self.all_files_dict[upstreamShortName]['locationHandling'] == 'keep-if-used') or
                            (self.all_files_dict[upstreamShortName]['locationHandling'] == 'keep')):
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
                        if downstreamImage in self.imagesUsedInThisBuild:
                            self.log.debug(upstreamShortName + ': Copied downstream because it is used in a downstream content file.')
                        elif self.all_files_dict[upstreamShortName]['locationHandling'] == 'keep':
                            self.log.debug(upstreamShortName + ': Copied downstream because it is defined in the locations file.')
                        usedInThisLocation.append(downstreamImage)

                    elif os.path.isfile(downstreamImage):
                        self.log.debug(upstreamShortName + ': Removed from ' + self.location_name + ' because it is not used in a downstream content file.')
                        os.remove(downstreamImage)
                        self.unusedInThisLocation.append(upstreamShortName)

                    else:
                        self.log.debug('Image not handled: ' + upstreamImage + ' (upstream),' + downstreamImage + ' (downstream)')

            # Check which downstream images were not found upstream
            for downstreamImage in self.imagesUsedInThisBuild:
                if (downstreamImage not in usedInThisLocation and
                        ((details['ibm_cloud_docs'] is False) or (details['ibm_cloud_docs'] is True and '/icons/' not in downstreamImage))):

                    for originalFileName in self.imagesUsedInThisBuild[downstreamImage]:
                        try:
                            if ('reuse-snippets' not in ','.join(self.imagesUsedInThisBuild[downstreamImage][originalFileName]['files'])):
                                addToWarnings(originalFileName + ' does not exist as referenced in downstream ' + self.location_name + ': ' +
                                              ','.join(self.imagesUsedInThisBuild[downstreamImage][originalFileName]['files']),
                                              originalFileName, originalFileName, details, self.log, self.location_name, '', '')
                        except Exception:
                            addToWarnings(originalFileName + ' could not be validated in downstream ' + self.location_name + ': ' +
                                          ','.join(self.imagesUsedInThisBuild[downstreamImage][originalFileName]['files']),
                                          originalFileName, originalFileName, details, self.log, self.location_name, '', '')
    except Exception as e:
        addToWarnings('Image check could not be completed. ' + str(e),
                      downstreamImage, downstreamImage, details, self.log, self.location_name, '', '')

    return (self.unusedInThisLocation)
