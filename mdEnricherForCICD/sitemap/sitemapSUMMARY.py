#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def sitemapSUMMARY(self, details):

    # Create a sitemap from an IBM Docs SUMMARY.md file

    # !/usr/bin/env python
    import os
    import traceback
    import re
    import shutil

    self.log.info("\n")
    self.log.info("Creating the sitemap from the SUMMARY.md file.")
    if details["builder"] == 'local':
        self.log.info('Locally, the sitemap might be incomplete.' +
                      'Credentials are not configured locally to go to Github and retrieve the' +
                      'content defined in the TOC that is reused from other services.')

    self.log.debug("\n\n")
    self.log.debug("-------------------------------------------------------------")
    self.log.debug("UPDATE SITEMAP")
    self.log.debug("-------------------------------------------------------------\n")

    self.CONTENT_REUSE_PAGES_FOLDER = 'reuse-pages'
    self.CONTENT_REUSE_SNIPPETS_FOLDER = 'reuse-snippets'

    # Break down one variable into 3
    if (details["ibm_cloud_docs_sitemap_depth"]).lower() == 'h1':
        H2_ENABLED = False
        H3_ENABLED = False
    elif (details["ibm_cloud_docs_sitemap_depth"]).lower() == 'h2':
        H2_ENABLED = True
        H3_ENABLED = False
    elif (details["ibm_cloud_docs_sitemap_depth"]).lower() == 'h3':
        H2_ENABLED = True
        H3_ENABLED = True
    else:
        self.log.info(details["ibm_cloud_docs_sitemap_depth"])
        self.log.info(details["ibm_cloud_docs_sitemap_depth"].lower())

    self.log.info('IBM_CLOUD_DOCS_SITEMAP_DEPTH: ' + details["ibm_cloud_docs_sitemap_depth"])
    self.log.info('H1_ENABLED: True')
    self.log.info('H2_ENABLED: ' + str(H2_ENABLED))
    self.log.info('H3_ENABLED: ' + str(H3_ENABLED))

    workingDir = self.location_dir
    self.log.debug('Working directory: ' + workingDir)

    os.chdir(workingDir)
    self.log.debug('Current directory: ' + os.getcwd())

    if not os.path.isfile(workingDir + '/SUMMARY.md'):
        self.log.warning('No SUMMARY.md file to work with. Not creating a sitemap.')
    else:
        file2 = workingDir + '/sitemap.md'
        self.log.debug('Sitemap location: ' + workingDir + '/sitemap.md')

        # Define types to empty declarations
        source: dict[dict[str, str], dict[str, str]] = {}  # type: ignore[misc]
        fileList: list[str] = []  # type: ignore[misc]
        h1: list[str] = []  # type: ignore[misc]
        sitemapAnchorList: list[str] = []  # type: ignore[misc]

        # Go through every file and get a list of files that will be included in the sitemap
        for root, dirs, files in os.walk(workingDir):
            for file in files:
                if ((not file == file2) and (file.endswith('.md') and
                                                          (self.CONTENT_REUSE_PAGES_FOLDER not in root) and
                                                          (self.CONTENT_REUSE_SNIPPETS_FOLDER not in root) and
                                                          ('.git' not in root) and
                                                          ('sitemap' not in file) and
                                                          ('images' not in root) and
                                                          ('README.md' not in file))):
                    fileList.append(root + '/' + file)
        for file in sorted(fileList):
            # Get the content from each file
            with open(file, "r+", encoding="utf8", errors="ignore") as f:
                topicContent = f.read()

                # Check to see if there is an anchor in the topic.
                # If there isn't, don't include it in the dictionary at all.
                # Helps eliminate some files that might be in progress or a
                # readme or something that might have snuck through
                idList = re.findall('{: #(.*?)}', topicContent, flags=re.DOTALL)

                if idList == []:
                    contentExists = False
                else:
                    contentExists = True

                if contentExists is True:
                    # Create a dictionary with an entry for that file name
                    source[file] = {}
                    h2 = ''
                    h3 = ''

                    # Gather a comment list so that way we can make sure not to include a heading that is within a comment
                    with open(file, "r+", encoding="utf8", errors="ignore") as f:
                        topicContent = f.read()
                        if '<!--' in topicContent:
                            commentList = re.findall('<!--(.*?)-->', topicContent, flags=re.DOTALL)
                        else:
                            commentList = []
                        if '```' in topicContent:
                            codeblockList = re.findall('```(.*?)```', topicContent, flags=re.DOTALL)
                        else:
                            codeblockList = []

                    # Read the file and go line by line to collect headings and the anchors under them
                    with open(file, "r+", encoding="utf8", errors="ignore") as f:
                        linecount = 0
                        anchorline = 0
                        lines = f.readlines()
                        for line in lines:
                            linecount = linecount + 1
                            anchorline = linecount
                            lineNumberLength = len(str(anchorline))
                            if lineNumberLength == 5:
                                anchorlineString = '0' + str(anchorline)
                            elif lineNumberLength == 4:
                                anchorlineString = '00' + str(anchorline)
                            elif lineNumberLength == 3:
                                anchorlineString = '000' + str(anchorline)
                            elif lineNumberLength == 2:
                                anchorlineString = '0000' + str(anchorline)
                            elif lineNumberLength == 1:
                                anchorlineString = '00000' + str(anchorline)
                            lineNoNewlines = line.replace('\n', '')

                            if ((not str(lineNoNewlines) in str(commentList)) and (not str(lineNoNewlines) in str(codeblockList))):
                                fileShort = file.split(workingDir + '/')[1]

                                if ((line.startswith("### ")) and (H3_ENABLED is True)):
                                    line1 = line.replace("### ", "")
                                    # self.log.debug('line 1 = ' + line1)
                                    line2 = line1.rstrip()
                                    # self.log.debug('line2 = ' + line2)
                                    title = line2+']'.rstrip()
                                    h3 = h3 + ';' + str(anchorlineString) + '$[' + title + '(' + fileShort
                                    source[file]['h3'] = h3

                                elif ((line.startswith("## ")) and (H2_ENABLED is True)):
                                    line1 = line.replace("## ", "")
                                    # self.log.debug('line 1 = ' + line1)
                                    line2 = line1.rstrip()
                                    # self.log.debug('line2 = ' + line2)
                                    title = line2+']'.rstrip()
                                    h2 = h2 + ';' + str(anchorlineString) + '$[' + title + '(' + fileShort
                                    source[file]['h2'] = h2

                                elif line.startswith('# '):
                                    count = 0
                                    line.count('#')
                                    count = count + 1
                                    if count > 1:
                                        break
                                    elif count == 1:
                                        title = line.replace('# ', '')
                                        title = title.rstrip()
                                        title = title + ']'.rstrip()
                                        h1 = '[' + str(anchorlineString) + '$[' + title + '(' + fileShort
                                        try:
                                            source[file]['draft-h1']
                                        except Exception:
                                            source[file]['draft-h1'] = str(h1)

        # get h1s and append anchor
        self.log.info('Including H1 headers.')
        # self.log.info(list(source.items()))

        for filename in source:
            # self.log.debug('Getting values for: ' + filename)
            try:
                h1all = source[filename]['draft-h1']
            except Exception as e:
                self.log.warning('There is an issue processing the conrefs.' +
                                 'There might be a file that is entirely removed by staging tags, ' +
                                 'though the file is referenced in the prod TOC. Check to see if ' +
                                 'there are staging tags that need to be removed from conref files ' +
                                 'or if a staging-only topic needs tags around it in the TOC.')
                self.log.warning(filename)
                self.log.warning(e)
            else:
                linenumber, goodlink = h1all.rsplit('$', 1)
                linenumber = linenumber.replace('[', '')
                # self.log.debug(linenumber)

                if os.path.isfile(str(filename)):
                    with open(str(filename), "r", encoding="utf8", errors="ignore") as file_open:
                        file_read = file_open.readlines()
                        for i, anchor in enumerate(file_read):

                            if int(i) == int(linenumber):
                                if 'notoc' not in anchor:
                                    if "{: #" in anchor:
                                        anchor = anchor.replace('{: #', '')
                                        anchor = anchor.replace('}', ')')
                                        goodh1 = goodlink + ')'
                                        source[filename]['h1'] = goodh1.rstrip()
                                        source[filename]['topicID'] = anchor
                                    else:
                                        source[filename]['topicID'] = ''

        # get h2 and append anchors
        if H2_ENABLED is not True:
            self.log.info('Skipping H2 headers.')
        else:
            self.log.info('Including H2 headers.')
            for filename in source:
                goodh2 = ''
                # source[filename]['h2'] = {}
                # self.log.info('h2: ' + filename)
                try:
                    h2all = source[filename]['h2']
                except Exception:
                    self.log.debug(str(filename) + ' No H2s')
                else:
                    try:
                        # self.log.debug(h1all)
                        h2list = h2all.split(';')
                        with open(str(filename), "r", encoding="utf8", errors="ignore") as file_openh2:
                            file_readh2 = file_openh2.readlines()
                        # self.log.debug(h2list)
                        for h2 in h2list:
                            noTocFound = False
                            # self.log.debug(h2list)
                            countColons = h2.count('$')
                            if countColons == 1:
                                linenumber, goodlink = h2.split('$')
                                linenumber = linenumber.replace('[', '')
                                anchorFound = False
                                for i, anchor in enumerate(file_readh2):
                                    if int(i) == (int(linenumber) + 1):
                                        if "{: notoc}" in str(anchor):
                                            noTocFound = True
                                            break
                                    if int(i) == int(linenumber):
                                        # self.log.debug(linenumber)
                                        if 'notoc' not in anchor:
                                            if "{: #" in str(anchor):
                                                # self.log.debug('anchor =' + anchor)
                                                anchor = anchor.replace('{: ', '')
                                                # self.log.debug(anchor)
                                                anchor = anchor.replace('}', ')')
                                                # self.log.debug(anchor)
                                                anchorFound = True
                                                goodAnchor = anchor
                                    try:
                                        topicID = source[filename]['topicID']
                                    except Exception:
                                        self.log.debug('Topic ID NOT found in: ' + str(filename))
                                    else:
                                        topicID = topicID.replace(')', '').rstrip()

                                if anchorFound is False:
                                    goodtitle = goodlink.split('[')[1]
                                    goodtitle = goodtitle.split(']')[0]
                                    goodAnchor = goodtitle.replace(' ', '-').replace(':', '').replace('#', '').replace('.', '')
                                    goodAnchor = goodAnchor.lower()
                                    goodAnchor = '#' + goodAnchor + ')'
                                    anchorFound = True
                                if ((noTocFound is False) and (anchorFound is True)):
                                    goodh2 = goodh2 + ';' + linenumber + '$' + goodlink + goodAnchor
                        source[filename]['goodh2'] = goodh2.rstrip()

                    except Exception as e:
                        self.log.debug('\n' + str(filename) + ': error')
                        self.log.debug('Not found:' + str(e))
                        self.log.debug(source[filename])
                        traceback.print_exc()

        # get h3 and append anchors
        if H3_ENABLED is not True:
            self.log.info('Skipping H3 headers.')
        else:
            self.log.info('Including H3 headers.')
            for filename in source:
                goodh3 = ''
                # source[filename]['h2'] = {}
                # self.log.debug(filename)
                try:
                    h3all = source[filename]['h3']
                except Exception:
                    self.log.debug(str(filename) + ' No H3s')
                else:
                    try:
                        # self.log.debug(h1all)
                        h3list = h3all.split(';')
                        # self.log.debug(h2list)
                        with open(str(filename), "r+", encoding="utf8", errors="ignore") as file_openh3:
                            file_readh3 = file_openh3.readlines()
                        for h3 in h3list:
                            noTocFound = False
                            # self.log.debug(h2list)
                            countColons = h3.count('$')
                            if countColons == 1:
                                linenumber, goodlink = h3.split('$')
                                linenumber = linenumber.replace('[', '')

                                anchorFound = False
                                for i, anchor in enumerate(file_readh3):
                                    if int(i) == (int(linenumber) + 1):
                                        if "{: notoc}" in str(anchor):
                                            noTocFound = True
                                            break
                                    if int(i) == int(linenumber):
                                        if 'notoc' not in anchor:
                                            if "{: #" in str(anchor):
                                                # self.log.debug('anchor =' + anchor)
                                                anchor = anchor.replace('{: ', '')
                                                # self.log.debug(anchor)
                                                anchor = anchor.replace('}', ')')
                                                # self.log.debug(anchor)
                                                goodAnchor = anchor
                                                anchorFound = True

                                        try:
                                            topicID = source[filename]['topicID']
                                        except Exception:
                                            self.log.debug('Topic ID NOT found in: ' + str(filename))
                                        else:
                                            topicID = topicID.replace(')', '').rstrip()

                                if anchorFound is False:
                                    goodtitle = goodlink.split('[')[1]
                                    goodtitle = goodtitle.split(']')[0]
                                    goodAnchor = goodtitle.replace(' ', '-').replace(':', '').replace('#', '').replace('.', '')
                                    goodAnchor = goodAnchor.lower()
                                    goodAnchor = '#' + goodAnchor + ')'
                                    anchorFound = True
                                if ((noTocFound is False) and (anchorFound is True)):
                                    goodh3 = goodh3 + ';' + linenumber + '$' + goodlink + goodAnchor

                        source[filename]['goodh3'] = goodh3.rstrip()

                    except Exception as e:
                        self.log.debug('\n' + str(filename) + ': error')
                        self.log.debug('Not found:' + str(e))
                        self.log.debug(source[filename])
                        traceback.print_exc()

        self.log.debug('-------------')
        self.log.debug('-------------')
        self.log.debug('-------------')

        with open(file2, "a", encoding="utf8", errors="ignore") as g:

            def loop(tocFilename):
                if (('.md' in tocFilename) and (not tocFilename.endswith('sitemap.md'))):

                    # Next get the repo name and the file name of what's stored in the source list
                    for filename in source:

                        filenameShort = str(filename).replace(' ', '').replace('	', '').replace('	', '').replace('  ', ' ').replace('\t', '').replace('\n', '')
                        # self.log.info('Comparing: ' + filenameShort + ' and ' + tocFilename)

                        if str(filenameShort) == str(tocFilename):
                            # Now compare the repo names and file names of the two and if they match, then continue
                            # self.log.info(filenameShort + ' is in ' + tocFilename)
                            self.log.debug('\n')
                            debugFilename = str(source[filename])
                            self.log.debug('Working with: ' + str(debugFilename.encode('utf-8', errors='ignore')))
                            try:
                                self.log.debug('H1: ' + str(source[filename]['h1']))
                            except Exception:
                                self.log.error('Check for missing anchors.')

                            topicTitle = source[filename]['h1']
                            topicTitle = topicTitle.split(']')[0]
                            if '[' in topicTitle:
                                topicTitle = topicTitle.split('[')[1]
                            # Write once without a link
                            g.write('\n\n\n## ' + topicTitle)
                            topicTitleNoSpaces = topicTitle.lower()
                            # Not sure why blockchain has these extra tabs in their headings - must be how the toc is configured with tabs?
                            topicTitleNoSpaces = topicTitleNoSpaces.replace(' ', '_').replace('	', '')
                            topicTitleNoSpaces = topicTitleNoSpaces.replace('	', '').replace('  ', ' ')
                            topicTitleNoSpaces = topicTitleNoSpaces.replace('\t', '').replace('(', '').replace(')', '')
                            topicTitleNoSpaces = topicTitleNoSpaces.replace('.', '').replace('  ', ' ')
                            while '{{' in topicTitleNoSpaces:
                                firstpart, ignore = topicTitleNoSpaces.split('{{', 1)
                                secondpart = ignore.split('}}', 1)[1]
                                topicTitleNoSpaces = firstpart + secondpart
                            while '{: #sitemap_' + topicTitleNoSpaces + '}' in sitemapAnchorList:
                                topicTitleNoSpaces = topicTitleNoSpaces + '_'
                            g.write('\n{: #sitemap_' + topicTitleNoSpaces + '}\n')
                            sitemapAnchorList.append('{: #sitemap_' + topicTitleNoSpaces + '}')
                            # Write once with the link
                            g.write('\n\n' + source[filename]['h1'])

                            if H2_ENABLED is True:
                                h2Listed = []
                                try:
                                    h2s = source[filename]['goodh2']
                                except Exception:
                                    self.log.debug('    No h2s in this MD topic.')

                                else:
                                    h2List = h2s.split(';')
                                    h2ListEncoded = str(h2List).encode('utf-8', errors='ignore')
                                    try:
                                        self.log.debug('h2List:' + str(h2ListEncoded))
                                    except Exception:
                                        self.log.debug('h2List: ASCII error. Could not log.')
                                    for h2 in h2List:
                                        h2ed = h2.replace('$', '$H2$')
                                        h2Listed.append(h2ed)

                                    self.log.debug('h2Listed:' + str(str(h2Listed).encode('utf-8', errors='ignore')))

                            if H3_ENABLED is True:
                                h3Listed = []
                                try:
                                    h3s = source[filename]['goodh3']
                                except Exception:
                                    self.log.debug('        No h3s in this MD topic.')
                                else:
                                    h3List = h3s.split(';')
                                    self.log.debug('h3List:' + str(str(h3List).encode('utf-8', errors='ignore')))
                                    for h3 in h3List:
                                        h3ed = h3.replace('$', '$H3$')
                                        h3Listed.append(h3ed)
                                    self.log.debug('h3Listed:' + str(str(h3Listed).encode('utf-8', errors='ignore')))

                                combinedListed: list[str] = []  # type: ignore[misc]
                                if H2_ENABLED is True:
                                    combinedListed = combinedListed + h2Listed
                                if H3_ENABLED is True:
                                    combinedListed = combinedListed + h3Listed

                                sortedListed = sorted(combinedListed)

                                sortedListedEncoded = str(sortedListed).encode('utf-8', errors='ignore')
                                self.log.debug('sortedListed: ' + str(sortedListedEncoded))

                                for listItem in sortedListed:
                                    dollarCount = listItem.count('$')
                                    if dollarCount == 2:

                                        level = listItem.split('$')[1]
                                        link = listItem.split('$')[2]
                                        # self.log.debug('lineNumber: ' + lineNumber)
                                        # self.log.debug('level: ' + level)
                                        # self.log.debug('link: ' + link)
                                        if level == 'H2':
                                            if not link == '':
                                                linkEncoded = str(link.rstrip()).encode('utf-8', errors='ignore')
                                                self.log.debug('    H2: ' + str(linkEncoded))
                                                g.write('\n\n* ' + link.rstrip())
                                                # self.log.debug('Writing H2: ' + str(linkEncoded))
                                        elif level == 'H3':
                                            if not link == '':
                                                linkEncoded = str(link.rstrip()).encode('utf-8', errors='ignore')
                                                self.log.debug('        H3: ' + str(linkEncoded))
                                                g.write('\n    * ' + link.rstrip())
                                                # self.log.debug('Writing H3: ' + str(linkEncoded))
                                # else:
                                        # self.log.debug('Not enough dollar signs to split: ' + listItem)
                            break
                        # elif str(filenameShort) in str(tempTocFilename):
                            # self.log.info('Did not find: ' + filenameShort + ' in ' + tempTocFilename)
                            # self.log.info('"' + filenameShort + '"')
                            # self.log.info('"' + tempTocFilename + '"')

            with open(workingDir + '/SUMMARY.md', "r+", encoding="utf8", errors="ignore") as file_open_summary:
                file_read_summary = file_open_summary.readlines()
                # subcollectionList = re.findall(r'subcollection\=\".*?\"',f)
                for line in file_read_summary:
                    if '.md' in line:
                        tocFilename = line.split('](')[1]
                        tocFilename = tocFilename.replace(')', '')
                        tocFilename = tocFilename.replace(' ', '').replace('	', '').replace('	', '').replace('  ', ' ').replace('\t', '').replace('\n', '')
                        # self.log.info('Running on ' + tocFilename)
                        loop(tocFilename)

        self.log.info('Success!')

    if os.path.isdir(workingDir + '/sitemap-temp/'):
        shutil.rmtree(workingDir + '/sitemap-temp/')
        self.log.debug('Removing: ' + '/sitemap-temp/')
