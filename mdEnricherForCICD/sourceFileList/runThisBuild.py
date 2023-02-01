#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def runThisBuild(details, all_files_dict, location_name, log, source_files_location_list):

    # Compare what is in with commit with what is supposed to be run for this location

    runThisLocation = False

    if any(x in list(all_files_dict) for x in source_files_location_list):
        log.debug('Running this location because file is in the list for this location.')
        runThisLocation = True

    if (('/images/') in str(source_files_location_list)) and (runThisLocation is False):
        log.debug('Running this location because /images/ is in the original source files list.')
        runThisLocation = True

    if (('/' + details["reuse_snippets_folder"] + '/') in str(source_files_location_list)) and (runThisLocation is False):
        log.debug('Running this location because ' + details["reuse_snippets_folder"] + '/ is in the original source files list.')
        runThisLocation = True

    if (details["featureFlagFile"] in source_files_location_list) and (runThisLocation is False):
        log.debug('Running this location because feature_flags.json is in the original source files list.')
        runThisLocation = True

    return (runThisLocation)
