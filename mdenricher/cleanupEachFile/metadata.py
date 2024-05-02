#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def metadata(self, details, file_name, firstAnchor, folderAndFile, folderPath, topicContents):

    # Replace the metadata variables
    # Retrieve the dates from the previous version of the file, if possible, to get an accurate changed file list

    # import os
    # import re  # for doing finds within the topic content

    # Rather than us using our own metadata attributes list, we'll use the core team's. After everyone stops using this conref, remove this section.
    if '[{METADATA_ATTRIBUTES}]' in topicContents:
        topicContents = topicContents.replace('[{METADATA_ATTRIBUTES}]', '{{site.data.keyword.attribute-definition-list}}')
        self.log.debug(r'Replaced [{METADATA_ATTRIBUTES}] with {{site.data.keyword.attribute-definition-list}}.')

    # This is for Blockchain's version links at the beginning of each file
    if '{[FIRST_ANCHOR]}' in topicContents:
        topicContents = topicContents.replace('{[FIRST_ANCHOR]}', firstAnchor)
        self.log.debug(r'Replaced [{FIRST_ANCHOR}] with ' + firstAnchor + '.')

    return (topicContents)
