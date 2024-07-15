#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def keyrefCheck(self, details, file_name, folderAndFile, folderPath, topicContents):

    # Validate IBM Cloud product names formatting

    import os
    import re
    import yaml

    from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.setup.exitBuild import exitBuild

    if "a ibm" in topicContents.lower():
        aIBMCount = (topicContents.lower()).count(" a ibm")
        if aIBMCount == 1:
            instance = 'instance'
        else:
            instance = 'instances'
        addToWarnings(str(aIBMCount) + ' ' + instance + ' of "a IBM" in the topic. ', folderAndFile, folderPath + file_name,
                      details, self.log, self.location_name, "a IBM", topicContents)

    elif details['ibm_cloud_docs_keyref_check'] is True:

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
                    addToWarnings('Missing starting curly brace for ' + '{site.data.keyword.' + keyref + '}}.',
                                  folderAndFile, folderPath + file_name, details, self.log,
                                  self.location_name, '{site.data.keyword.' + keyref + '}}', topicContents)
                if missingEndCount > 0:
                    addToWarnings('Missing end curly brace for ' + '{{site.data.keyword.' + keyref + '}.',
                                  folderAndFile, folderPath + file_name, details, self.log,
                                  self.location_name, '{{site.data.keyword.' + keyref + '}', topicContents)
                if missingBothCount > 0:
                    addToWarnings('Missing start and end curly brace for ' + '{site.data.keyword.' + keyref + '}.',
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
                        # Check for instances of " a IBM"
                        aIBMCount = (topicContentsAIBM.lower()).count(" a ibm")
                        if aIBMCount > 0:
                            if aIBMCount == 1:
                                instance = 'instance'
                            else:
                                instance = 'instances'
                            addToWarnings(str(aIBMCount) + ' ' + instance + ' of "a IBM" created by "a ' +
                                          '{{site.data.keyword.' + keyref + '}}' + '". ', folderAndFile, folderPath + file_name,
                                          details, self.log, self.location_name, " a " + '{{site.data.keyword.' + keyref + '}}', topicContents)
            # Then check if it's in the keyref.yaml file
            if os.path.isfile(self.location_dir + '/keyref.yaml') and productNameFound is False:
                with open(self.location_dir + '/keyref.yaml', "r", encoding="utf8", errors="ignore") as stream:
                    try:
                        keyrefsAll = yaml.safe_load(stream)
                    except yaml.YAMLError as exc:
                        self.log.warning(exc)
                        addToWarnings('YML not formatted properly. Check keyref.yaml for errors. ' +
                                      str(exc), folderAndFile, '', details, self.log, self.location_name, '', '')
                    else:
                        keyrefs = keyrefsAll['keyword']
                        if keyref not in keyrefs and not details['ibm_cloud_docs_product_names'] == []:
                            addToWarnings('{{site.data.keyword.' + keyref + '}} could not be found in cloudoekeyrefs.yml or in keyref.yaml.',
                                          folderAndFile, folderPath + file_name, details, self.log,
                                          self.location_name, '', topicContents)
            # Since it's not in a keyref, it must be a product name error
            elif productNameFound is False and not details['ibm_cloud_docs_product_names'] == []:
                addToWarnings('{{site.data.keyword.' + keyref + '}} could not be found in cloudoekeyrefs.yml.',
                              folderAndFile, folderPath + file_name, details, self.log,
                              self.location_name, '', topicContents)
