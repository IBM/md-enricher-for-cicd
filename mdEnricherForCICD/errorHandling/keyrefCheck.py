#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def keyrefCheck(self, details, file_name, folderAndFile, folderPath, topicContents):

    # Validate IBM Cloud product names formatting

    import os
    import re
    import yaml

    from errorHandling.errorHandling import addToWarnings
    from errorHandling.errorHandling import addToErrors
    # from setup.exitBuild import exitBuild

    # Do not run this in Jenkins or local
    # if not self.location_output_action == 'none':
    if details['ibm_cloud_docs_keyref_check'] is True:

        # Get all keyref names
        keyrefs = re.findall("site.data.keyword.(.*?)}", topicContents)
        # Remove the duplicates
        keyrefs = list(dict.fromkeys(keyrefs))

        for keyref in keyrefs:

            # Check for missing curly braces in product names and service keyrefs
            allUsageCount = topicContents.count('site.data.keyword.' + keyref + '}')
            goodUsageCount = topicContents.count('{{site.data.keyword.' + keyref + '}}')
            if not allUsageCount == goodUsageCount:

                topicContentsNoGood = topicContents.replace('{{site.data.keyword.' + keyref + '}}', '')

                missingEndCount = topicContentsNoGood.count('{{site.data.keyword.' + keyref + '}')
                topicContentsNoGood = topicContentsNoGood.replace('{{site.data.keyword.' + keyref + '}', '')

                missingStartCount = topicContentsNoGood.count('{site.data.keyword.' + keyref + '}}')
                topicContentsNoGood = topicContentsNoGood.replace('{site.data.keyword.' + keyref + '}}', '')

                missingBothCount = topicContentsNoGood.count('{site.data.keyword.' + keyref + '}')

                if missingStartCount > 0:
                    addToErrors('Missing starting curly brace for ' + '{site.data.keyword.' + keyref + '}}.',
                                folderAndFile, folderPath + file_name, details, self.log,
                                self.location_name, '{site.data.keyword.' + keyref + '}}', topicContents)
                if missingEndCount > 0:
                    addToErrors('Missing end curly brace for ' + '{{site.data.keyword.' + keyref + '}.',
                                folderAndFile, folderPath + file_name, details, self.log,
                                self.location_name, '{{site.data.keyword.' + keyref + '}', topicContents)
                if missingBothCount > 0:
                    addToErrors('Missing start and end curly brace for ' + '{site.data.keyword.' + keyref + '}.',
                                folderAndFile, folderPath + file_name, details, self.log,
                                self.location_name, '{site.data.keyword.' + keyref + '}', topicContents)

            # Check first if the keyref is an IBM Cloud Docs product name
            productNameFound = False
            if not details['ibm_cloud_docs_product_names'] == []:
                try:
                    details['ibm_cloud_docs_product_names']
                except Exception:
                    addToErrors('ibm_cloud_docs_product_names could not be found.', folderAndFile, folderPath + file_name, details, self.log,
                                self.location_name, '', topicContents)
                else:
                    if keyref in details['ibm_cloud_docs_product_names']:
                        productNameFound = True
                        topicContentsAIBM = topicContents.replace('{{site.data.keyword.' + keyref + '}}', details['ibm_cloud_docs_product_names'][keyref])
                        # Check for instances of "a IBM"
                        aIBMCount = (topicContentsAIBM.lower()).count("a ibm")
                        if aIBMCount > 0:
                            if aIBMCount == 1:
                                instance = 'instance'
                            else:
                                instance = 'instances'
                            addToWarnings(str(aIBMCount) + ' ' + instance + ' of "a IBM" created by "a ' +
                                          '{{site.data.keyword.' + keyref + '}}' + '". ', folderAndFile, folderPath + file_name,
                                          details, self.log, self.location_name, "a " + '{{site.data.keyword.' + keyref + '}}', topicContents)
            # Then check if it's in the keyref.yaml file
            if os.path.isfile(details['source_dir'] + '/keyref.yaml') and productNameFound is False:
                with open(details['source_dir'] + '/keyref.yaml', "r", encoding="utf8", errors="ignore") as stream:
                    try:
                        keyrefsAll = yaml.safe_load(stream)
                        keyrefs = keyrefsAll['keyword']
                        if keyref not in keyrefs:
                            addToErrors('{{site.data.keyword.' + keyref + '}} could not be found in cloudoekeyrefs.yml or in keyref.yaml.',
                                        folderAndFile, folderPath + file_name, details, self.log,
                                        self.location_name, '', topicContents)
                    except yaml.YAMLError as exc:
                        self.log.warning(exc)
            # Since it's not in a keyref, it must be a product name error
            elif productNameFound is False:
                addToErrors('{{site.data.keyword.' + keyref + '}} could not be found in cloudoekeyrefs.yml.',
                            folderAndFile, folderPath + file_name, details, self.log,
                            self.location_name, '', topicContents)
