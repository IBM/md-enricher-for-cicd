#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def comments(self, details, folderAndFile, topicContents):

    # Handle HTML comments based on what is specified for the location's location_comments

    import re  # for doing finds within the topic content

    self.log.debug('Handling comments in ' + folderAndFile + '.')

    # If location_comments is off, replace all of the comments with nothing unless they are in style tags
    if folderAndFile.endswith(tuple(details["filetypes"])):

        linkCheckerSkipText = 'Link checker skip'
        searchTermList = 'meta name="searchTerms"'

        commentList = re.findall('<!--(.*?)-->', topicContents, flags=re.DOTALL)

        for comment in commentList:

            if 'SPDX-License-Identifier' in comment:
                self.log.debug('Not removing IBM Copyright.')

            # Always remove the snippet insertion comments because they can screw up links and tables
            elif comment.startswith('Snippet'):
                topicContents = topicContents.replace('<!--' + comment + '-->', '')

            elif linkCheckerSkipText in comment:
                self.log.debug('Not removing link checker skip text.')

            elif 'ME_ignore' in comment:
                self.log.debug('Not removing comment to ignore.')

            # Don't remove comments that have style tags around them
            elif '<style><!--' + comment + '--></style>' in topicContents:
                self.log.debug('Not removing comment because it is within style tags: ' + comment)

            elif searchTermList in comment:
                self.log.debug('Leaving search terms comment because it includes terms for internal SEO testing.')

            # If there's a heading in the section, just remove it to avoid having it added into the sitemap
            elif '# ' in comment and not self.sitemap_file == 'None':
                topicContents = topicContents.replace('<!--' + comment + '-->', '')
                self.log.debug('Removing comment because a heading is in it. Avoiding including it in the sitemap.')

            elif self.location_comments == 'off':
                topicContents = topicContents.replace('<!--' + comment + '-->', '')

            # else self.location_comments == 'on', leave it

        return (topicContents)
