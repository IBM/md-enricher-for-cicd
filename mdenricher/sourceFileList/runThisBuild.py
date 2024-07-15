#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def runThisBuild(self, details):

    # Compare what is in with commit with what is supposed to be run for this location

    runThisLocation = False

    # log.debug('source_files_location_list:')
    # log.debug(source_files_location_list)

    for x in self.source_files_location_list:
        try:
            if self.all_files_dict[x]['locationHandling'] == 'keep':
                # if any(self.source_files_location_list[x]['locationHandling'] == 'keep'
                # for x in self.source_files_location_list) and (runThisLocation is False):
                self.log.debug('Running this location because a supported filetype is in the original source files list.')
                runThisLocation = True
                break
        except Exception as e:
            self.log.error(x)
            self.log.error('Key error')
            self.log.error(e)

    if runThisLocation is False:
        for x in self.source_files_location_list:
            if self.source_files_location_list[x]['fileStatus'] == 'removed':
                self.log.debug('Running this location because a file was removed upstream.')
                runThisLocation = True
                break

    return (runThisLocation)
