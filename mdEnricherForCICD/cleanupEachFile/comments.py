#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def comments(self, details, folderAndFile, topicContents):

    import re  # for doing finds within the topic content

    self.log.debug('Handling comments in ' + folderAndFile + '.')

    # If location_comments is off, replace all of the comments with nothing unless they are in style tags
    if folderAndFile.endswith(tuple(details["filetypes"])):

        linkCheckerSkipText = 'Link checker skip'
        searchTermList = 'meta name="searchTerms"'

        if ((searchTermList in topicContents) or
                (linkCheckerSkipText in topicContents) or
                ('<style>' in topicContents) or
                (self.location_comments == 'on') or
                ('<!--Do not transform-->' in topicContents) or
                ('SPDX-License-Identifier' in topicContents) or
                ('<!-Snippet' in topicContents)):

            commentList = re.findall('<!--(.*?)-->', topicContents, flags=re.DOTALL)
            for comment in commentList:

                if 'SPDX-License-Identifier' in comment:
                    self.log.debug('Not removing IBM Copyright.')

                # If there's a heading in the section, just remove it to avoid having it added into the sitemap
                elif '# ' in comment:
                    topicContents = topicContents.replace('<!--' + comment + '-->', '')
                    self.log.debug('Removing comment because a heading is in it. Avoiding including it in the sitemap.')

                # Always remove the snippet insertion comments because they can screw up links and tables
                elif comment.startswith('Snippet'):
                    topicContents = topicContents.replace('<!--' + comment + '-->', '')

                # For transforming on the md-enricher-for-cicd docs
                # Do not remove so that the example code phrases to show the metadata variables won't be replaced
                elif 'Do not transform' in comment:
                    self.log.debug('Not removing <!--Do not transform-->.')

                elif searchTermList in comment:
                    if details["source_github_branch"] == 'None':
                        self.log.debug('Leaving search terms comment because it includes terms for internal SEO testing.')
                    else:
                        topicContents = topicContents.replace('<!--' + comment + '-->', '')

                # Don't remove comments that have style tags around them
                elif '<style>' in topicContents:
                    styleTags = re.findall('<style>(.*?)</style>', topicContents, flags=re.DOTALL)
                    commentInStyle = False
                    for styleTag in styleTags:
                        if comment in styleTag:
                            self.log.debug('Not removing comment because it is within style tags: ' + comment)
                            commentInStyle = True
                            break
                    if ((commentInStyle is False) and
                            (linkCheckerSkipText not in comment) and
                            (self.location_comments == 'off')):
                        topicContents = topicContents.replace('<!--' + comment + '-->', '')

                # Don't remove comments that have the link checker skip text in it
                elif (linkCheckerSkipText not in comment) and (self.location_comments == 'off'):
                    topicContents = topicContents.replace('<!--' + comment + '-->', '')

        else:
            if self.location_comments == 'off':
                topicContents = re.sub('<!--(.*?)-->', '', topicContents, flags=re.DOTALL)

    return (topicContents)
