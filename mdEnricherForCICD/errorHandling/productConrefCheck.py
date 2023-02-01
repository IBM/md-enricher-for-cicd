#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def productConrefCheck(self, details, file_name, folderAndFile, folderPath, topicContents):

    # Validate IBM Cloud product names formatting

    import re

    # from errorHandling.errorHandling import addToWarnings
    from errorHandling.errorHandling import addToErrors
    # from setup.exitBuild import exitBuild

    # Do not run this in Jenkins or local
    if not self.location_output_action == 'none':

        # Slack error for malformed conrefs, like missing { or }
        def malformedError(potentiallyMalformedConref, details):
            addToErrors('Malformed product conref: ' + potentiallyMalformedConref, folderAndFile, folderPath +
                        file_name, details, self.log, self.location_name, potentiallyMalformedConref, topicContents)

        # Get the product conrefs from the cloudoeconrefs.yml file
        productConrefsUsedList = []

        # Get all of the product conrefs used in the topic that start and end with {{ and }}
        properlyFormedConrefs = re.findall(r"\{\{.*?\}\}", topicContents, re.DOTALL)
        # Remove duplicates
        properlyFormedConrefs = list(dict.fromkeys(properlyFormedConrefs))

        # Get all of the product names with only single ending brace, to figure out maybe if there's one missing
        # from the beginning or end
        potentiallyMalformedConrefs = re.findall(r"site.data.keyword.*?\}", topicContents, re.DOTALL)
        # Remove duplicates
        potentiallyMalformedConrefs = list(dict.fromkeys(potentiallyMalformedConrefs))

        # Go through each potential malformed conref and see if they are in the properly formed conref list
        for potentiallyMalformedConref in potentiallyMalformedConrefs:
            if ('{{' + potentiallyMalformedConref + '}') in properlyFormedConrefs:

                # Get the number of properly used and malformed conrefs and make sure they match, if not then we know that there's a malformed one
                numberOfMalformed = topicContents.count(potentiallyMalformedConref)
                numberOfProper = topicContents.count('{{' + potentiallyMalformedConref + '}')

                if numberOfMalformed == numberOfProper:
                    productConrefsUsedList.append('{{' + potentiallyMalformedConref + '}')
                else:
                    malformedError(potentiallyMalformedConref[:-1], details)
            else:
                malformedError(potentiallyMalformedConref[:-1], details)

        # Remove duplicates
        productConrefsUsedList = list(dict.fromkeys(productConrefsUsedList))

        # Go through the product conref list and verify that they do exist in the cloudoeconrefs.yml file
        if not productConrefsUsedList == [] and details["ibm_cloud_docs_product_name_check"] is True:

            for productConrefUsed in productConrefsUsedList:
                # Parse the yml file and see if you can get a value for each product name. If so, then it's valid.
                # If not, generate an error.
                try:
                    productConrefUsedKey = productConrefUsed.split('.')[3]
                    productConrefUsedKey = productConrefUsedKey.split('}')[0]
                    self.log.debug('Product conref validated: ' + productConrefUsed)
                except Exception:
                    addToErrors('No product name found for: ' + productConrefUsed, folderAndFile, folderPath + file_name, details, self.log,
                                self.location_name, productConrefUsed, topicContents)
