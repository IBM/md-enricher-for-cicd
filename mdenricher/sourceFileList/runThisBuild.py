#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def runThisBuild(self, details):

    # Compare what is in with commit with what is supposed to be run for this location

    runThisLocation = False

    # log.debug('source_files_location_list:')
    # log.debug(source_files_location_list)

    if any(x in list(self.all_files_dict) for x in self.source_files_location_list):
        self.log.debug('Running this location because file is in the list for this location.')
        runThisLocation = True

    if (('/images/') in str(self.source_files_location_list)) and (runThisLocation is False):
        self.log.debug('Running this location because /images/ is in the original source files list.')
        runThisLocation = True

    if (('/' + details["reuse_snippets_folder"] + '/') in str(self.source_files_location_list)) and (runThisLocation is False):
        self.log.debug('Running this location because ' + details["reuse_snippets_folder"] + '/ is in the original source files list.')
        runThisLocation = True

    if (details["featureFlagFile"] in self.source_files_location_list) and (runThisLocation is False):
        self.log.debug('Running this location because feature_flags.json is in the original source files list.')
        runThisLocation = True

    if runThisLocation is False:
        for x in self.source_files_location_list:
            if self.source_files_location_list[x]['fileStatus'] == 'removed':
                self.log.debug('Running this location because a file was removed upstream.')
                runThisLocation = True
                break

    return (runThisLocation)
