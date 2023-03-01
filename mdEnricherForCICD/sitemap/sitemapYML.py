#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def sitemapYML(self, details, source_files):

    def getReuseFile(reuseTopic):

        # - include: ../va/va_index.md
        # {{../account/account_settings.md#view-acct-settings}}
        while '../' in reuseTopic:
            reuseTopic = reuseTopic.replace('../', '')
        reuseTopic = reuseTopic.replace('\n', '')
        # account   account_settings.md#view-acct-settings
        reuseRepo, pathAndReuseTopic = reuseTopic.split('/', 1)
        if '#' in pathAndReuseTopic:
            pathAndReuseTopic = pathAndReuseTopic.split('#', 1)[0]
        if '/' in pathAndReuseTopic:
            pathToReuseTopic = pathAndReuseTopic.rsplit('/', 1)[0]
        else:
            pathToReuseTopic = ''
        fileContentsText = ''
        if os.path.isfile(self.location_dir + '/.build.yaml'):
            with open(self.location_dir + '/.build.yaml', "r+", encoding="utf8", errors="ignore") as yaml_read:
                yamlContents = yaml.safe_load(yaml_read)
            for repo in yamlContents["includes"]:
                tempRepo = repo.split('/')
                # 0: http, 1: nothing, 2: domain, 3: org, 4: repo
                if tempRepo[4] == reuseRepo:
                    self.log.info('Getting ' + tempRepo[3] + '/' + tempRepo[4] + '/' + pathAndReuseTopic + ' for reuse.')
                    fileContents = requests.get('https://raw.' + tempRepo[2] + '/' + tempRepo[3] + '/' +
                                                tempRepo[4] + '/' + self.location_github_branch + '/' +
                                                pathAndReuseTopic, auth=(details["username"], details["token"]))
                    # self.log.info(fileContents.status_code)
                    if fileContents.status_code == 200:
                        # Keyrefs in the same repo don't need to be resolved, but
                        # keyrefs in content other repos need to be resolved to be inserted into the sitemap
                        fileContentsText = str(fileContents.text)

                        # Get the keyref.yaml file, if it exists
                        if '{{site.data.keyword.' in fileContentsText:
                            # If a reuse section contains a keyword from their own keyref.yaml file
                            keyrefFile = requests.get('https://raw.' + tempRepo[2] + '/' + tempRepo[3] + '/' +
                                                      tempRepo[4] + '/' + self.location_github_branch + '/keyref.yaml',
                                                      auth=(details["username"], details["token"]))
                            if os.path.isfile(self.location_dir + '/sitemap-temp/' + tempRepo[4] + '/keyref.yaml'):
                                with open(self.location_dir + '/sitemap-temp/' + tempRepo[4] + '/keyref.yaml',
                                          "w+", encoding="utf8", errors="ignore") as keyrefFileOpen:
                                    keyrefFileOpen.write(keyrefFile.text)

                        # Get the conref.md file, if it exists
                        if '{{site.data.content.' in fileContentsText:
                            # If a reuse section contains a keyword from their own keyref.yaml file
                            conrefFile = requests.get('https://raw.' + tempRepo[2] + '/' + tempRepo[3] + '/' +
                                                      tempRepo[4] + '/' + self.location_github_branch + '/conref.md',
                                                      auth=(details["username"], details["token"]))
                            with open(self.location_dir + '/sitemap-temp/' + tempRepo[4] + '/conref.md',
                                      "w+", encoding="utf8", errors="ignore") as conrefFileOpen:
                                conrefFileOpen.write(conrefFile.text)

                        if not os.path.isdir(self.location_dir + '/sitemap-temp/' + tempRepo[4] + '/' + pathToReuseTopic):
                            os.makedirs(self.location_dir + '/sitemap-temp/' + tempRepo[4] + '/' + pathToReuseTopic)
                        with open(self.location_dir + '/sitemap-temp/' + tempRepo[4] + '/' + pathAndReuseTopic,
                                  "w+", encoding="utf8", errors="ignore") as reuseFile:
                            reuseFile.write(fileContentsText)
                        # For Jenkins and local, also write the include file to be processed with the markdown transform
                        if not details["builder"] == 'travis':
                            # if not os.path.isfile(details["output_dir"] + '/' + tempRepo[4] + '/' + pathAndReuseTopic):
                            if not os.path.isdir(details["output_dir"] + '/' + tempRepo[4] + '/' + pathToReuseTopic):
                                os.makedirs(details["output_dir"] + '/' + tempRepo[4] + '/' + pathToReuseTopic)
                            with open(details["output_dir"] + '/' + tempRepo[4] + '/' + pathAndReuseTopic,
                                      "w+", encoding="utf8", errors="ignore") as reuseFile:
                                reuseFile.write(fileContentsText)
                    else:
                        self.log.error(fileContents.text)
                        self.log.error('No file contents returned.')
        return (reuseRepo, fileContentsText)

    def conrefMDReplacement(conrefMDFilepath, topicContents, srcFile):
        if '/' in srcFile:
            srcFile = srcFile.rsplit('/', 1)[1]
        srcFile = srcFile.replace('.md', '')
        headingLevel = 0
        startingHeadingLevel = 0
        headings = ['## ', '### ', '#### ', '##### ', '###### ']
        with open(conrefMDFilepath, "r", encoding="utf8", errors="ignore") as conrefFileOpen:
            conrefLines = conrefFileOpen.readlines()
        conrefsUsed = re.findall('{{site.data.content.(.*?)}}', topicContents)
        conrefsUsed = list(dict.fromkeys(conrefsUsed))

        for conrefUsed in conrefsUsed:
            getHeadingAnchor = False
            startingHeading = ''
            startingAnchor = ''
            sectionToInsert = []
            storeLines = False
            for line in conrefLines:
                if getHeadingAnchor is True:
                    # If the heading has an anchor and it matches the one being evaluated
                    # Then start tracking the subsquent lines until it reaches a breaking ppoint
                    # Which is either the end of the file, a heading without an anchor
                    # Or a heading that has the same level as the starting one
                    if '{: #' in line:
                        if (startingAnchor == '') and (re.findall('{: #(.*?)}', line)[0] == conrefUsed):
                            startingAnchor = line
                            storeLines = True
                            insertRevisedAnchor = True
                        else:
                            startingHeading == ''
                            storeLines = False
                            insertRevisedAnchor = False

                    getHeadingAnchor = False

                # First get to a line that's a heading,
                # if it is, then jump above to see if that heading has an anchor
                if line.startswith(tuple(headings)):
                    getHeadingAnchor = True
                    startingHeading = line
                    if startingHeading == '':
                        hCount = startingHeading.split(' ', 1)[0]
                        startingHeadingLevel = hCount.count('#')
                        self.log.info('Starting heading: ')
                        self.log.info(startingHeading)
                    if storeLines is True:
                        anotherHeading = line
                        hCount = anotherHeading.split(' ', 1)[0]
                        headingLevel = hCount.count('#')
                        if startingHeadingLevel <= headingLevel:
                            storeLines = False

                if storeLines is True:
                    if (insertRevisedAnchor is True) and ('{: #' in line):
                        sectionToInsert.append(startingHeading)
                        line = line.replace('{: #', '{: #' + srcFile + '-include-')
                        insertRevisedAnchor = False
                    sectionToInsert.append(line)
                else:
                    startingHeading == ''

            if not sectionToInsert == []:
                sectionToInsertString = ''.join(sectionToInsert)
                topicContents = topicContents.replace('{{site.data.content.' + conrefUsed + '}}', sectionToInsertString)
            else:
                self.log.info('{{site.data.content.' + conrefUsed + '}} is empty')
        return (topicContents)

    def checkForReusedSections(topicContents, srcFile):

        import re

        # keyref.yaml replacements are not needed for content in this subcollection
        # Because they can get resolved in the sitemap during markdown processor build time

        # {{site.data.content.someconrefname}} from conref.md in this subcollection
        if '{{site.data.content.' in topicContents:
            topicContents = conrefMDReplacement(self.location_dir + '/conref.md', topicContents, srcFile)

        # {{../account/account_settings.md#view-acct-settings}}
        if '{{../' in topicContents:
            # Get a list of all reused sections in the topic
            reusedSections = re.findall('{{../(.*?)}}', topicContents)
            # For each reuse section
            for reuseTopic in reusedSections:
                # Get the contents of that file
                self.log.info(' Getting: ' + reuseTopic)
                reuseRepo, reuseTopicContents = getReuseFile(reuseTopic)
                # Get the anchor
                if '#' in reuseTopic:
                    anchor = reuseTopic.split('#')[1]
                # If there is no anchor specified, grab the first one in the topic
                else:
                    anchor = re.findall('{: #(.*?)}', topicContents)[0]
                # Turn the topic contents into a list
                reuseTopicContentsLines = reuseTopicContents.split('\n')
                reusedSection = ''
                # For every line in the topic contents
                previousLine = ''
                for line in reuseTopicContentsLines:
                    # Find the anchor referenced
                    if '{: #' + anchor + '}' in line:
                        # Then split the section on the heading before the anchor
                        reusedSectionWithoutHeading = reuseTopicContents.split(previousLine)[1]
                        reusedSection = previousLine + '\n' + reusedSectionWithoutHeading
                        reusedSectionLines = reusedSectionWithoutHeading.split('\n')
                        # Go through every line of the reused section content and look for the
                        # next heading of the same level or higher to end on
                        for reusedLine in reusedSectionLines:
                            if reusedSection.startswith('#### '):
                                if reusedLine.startswith('#### ') or reusedLine.startswith('### ') or reusedLine.startswith('## '):
                                    reusedSection = reusedSection.split(reusedLine)[0]
                            elif reusedSection.startswith('### '):
                                if reusedLine.startswith('### ') or reusedLine.startswith('## '):
                                    reusedSection = reusedSection.split(reusedLine)[0]
                            elif reusedSection.startswith('## '):
                                if reusedLine.startswith('## '):
                                    reusedSection = reusedSection.split(reusedLine)[0]
                        break
                    previousLine = line
                if reusedSection == '':
                    self.log.warning('The section could not be found: ' + '{{../' + reuseTopic + '}}')
                else:
                    # {{site.data.content.someconrefname}} from conref.md in another subcollection
                    if '{{site.data.content.' in reusedSection:
                        reusedSection = conrefMDReplacement(self.location_dir + '/sitemap-temp/' + reuseRepo + '/conref.md', reusedSection, srcFile)

                    # {{site.data.keyword.somekeyword name}} from keyref.yaml in another subcollection
                    if '{{site.data.keyword.' in reusedSection:
                        if os.path.isfile(self.location_dir + '/sitemap-temp/' + reuseRepo + '/keyref.yaml'):
                            with open(self.location_dir + '/sitemap-temp/' + reuseRepo + '/keyref.yaml',
                                      "r", encoding="utf8", errors="ignore") as keyrefFileOpen:
                                keyrefFileYAML = yaml.safe_load(keyrefFileOpen)
                            keywords = re.findall('{{site.data.keyword.(.*?)}}', reusedSection)
                            keywords = list(dict.fromkeys(keywords))
                            for keyword in keywords:
                                try:
                                    value = keyrefFileYAML['keyword'][keyword]
                                except Exception:
                                    pass
                                else:
                                    reusedSection = reusedSection.replace('{{site.data.keyword.' + keyword + '}}', value)
                    topicContents = topicContents.replace('{{../' + reuseTopic + '}}', reusedSection)

        return (topicContents)

    # Create a sitemap from a marked-it version 2 toc.yaml file

    try:

        # !/usr/bin/env python
        import os
        import re
        import requests
        import shutil
        import subprocess
        import yaml

        from errorHandling.errorHandling import addToWarnings
        from errorHandling.errorHandling import addToErrors
        # from setup.exitBuild import exitBuild
        from cleanupEachFile.writeResult import writeResult

        input_file = '/toc.yaml'
        relativeLinks = ['/apidocs', '/catalog', '/docs/faqs', '/observe', '/status', '/unifiedsupport']
        sitemapAnchorList: list[str] = []  # type: ignore[misc]

        if (details["username"] is None) or (details["token"] is None) or (self.location_github_branch is None) or (self.location_github_domain is None):
            self.log.debug('Locally, the sitemap might be incomplete.' +
                           'Credentials are not configured locally to go to Github and retrieve the content ' +
                           'defined in the TOC that is reused from other services.')

        self.log.debug("\n\n")
        self.log.debug("-------------------------------------------------------------")
        self.log.debug("UPDATE SITEMAP")
        self.log.debug("-------------------------------------------------------------\n")

        # Break down one variable into 3
        if (details["ibm_cloud_docs_sitemap_depth"]).lower() == 'h1':
            H2_ENABLED = False
            H3_ENABLED = False
            H4_ENABLED = False
        elif (details["ibm_cloud_docs_sitemap_depth"]).lower() == 'h2':
            H2_ENABLED = True
            H3_ENABLED = False
            H4_ENABLED = False
        elif (details["ibm_cloud_docs_sitemap_depth"]).lower() == 'h3':
            H2_ENABLED = True
            H3_ENABLED = True
            H4_ENABLED = False
        elif (details["ibm_cloud_docs_sitemap_depth"]).lower() == 'h4':
            H2_ENABLED = True
            H3_ENABLED = True
            H4_ENABLED = True
        else:
            self.log.debug(details["ibm_cloud_docs_sitemap_depth"])
            self.log.debug(details["ibm_cloud_docs_sitemap_depth"].lower())

        self.log.debug('ibm_cloud_docs_sitemap_depth: ' + details["ibm_cloud_docs_sitemap_depth"])
        self.log.debug('H1_ENABLED: True')
        self.log.debug('H2_ENABLED: ' + str(H2_ENABLED))
        self.log.debug('H3_ENABLED: ' + str(H3_ENABLED))
        self.log.debug('H4_ENABLED: ' + str(H4_ENABLED))

        location_sitemap_file_name = source_files[self.sitemap_file]['file_name']
        location_sitemap_folderPath = source_files[self.sitemap_file]['folderPath']
        location_sitemap_file = location_sitemap_folderPath + location_sitemap_file_name

        self.log.info("\n")
        self.log.info('Creating ' + location_sitemap_file + ' from ' + self.sitemap_file + ' and ' + input_file + ".")

        # self.log.info('Working directory: ' + self.location_dir)

        # Clone repos/files for marked-it conref reuse

        if os.path.isfile(self.location_dir + input_file):
            self.log.debug(self.location_dir + input_file + ' exists.')
            contentReuseList = []
            if ((details["username"] is not None) and
                    (details["token"] is not None) and
                    (self.location_github_branch is not None) and
                    (self.location_github_domain is not None)):

                self.log.debug('Parsing ' + input_file)
                cloudDocsOrg = 'cloud-docs'
                # if cloudDocsOrg == 'Run this now':
                with open(self.location_dir + input_file, "r+", encoding="utf8", errors="ignore") as file_open:
                    file_read = file_open.readlines()
                    for line in file_read:
                        line = re.sub('<!--(.*?)-->', '', line, flags=re.DOTALL)
                        tocFilenameNoSpaces = line.replace('-', '', 1).replace(' ', '').replace('\n', '')
                        if '/toc' in line:
                            contentReuseList.append(tocFilenameNoSpaces)
                            tocFilenameNoStartingSlash = tocFilenameNoSpaces[1:]
                            repoName = tocFilenameNoStartingSlash.split('/', 1)[0]
                            if not os.path.isdir(self.location_dir + '/sitemap-temp/' + repoName):
                                self.log.info('Cloning ' + repoName + ' to resolve sitemap content.')
                                subprocess.call('git clone --depth 1 -b ' + self.location_github_branch + ' https://' +
                                                details["username"] + ':' + details["token"] + '@' +
                                                self.location_github_domain + '/' + cloudDocsOrg + '/' + repoName + ' ' +
                                                self.location_dir + '/sitemap-temp/' + repoName + ' --quiet', shell=True)
                            if not os.path.isfile(self.location_dir + '/sitemap-temp/' + repoName + input_file):
                                addToWarnings('The sitemap might be incomplete. This TOC does not exist yet: ' +
                                              repoName + input_file, location_sitemap_file, '', details, self.log,
                                              self.location_name, '', '')
                        elif 'include: ' in line:
                            # - include: ../va/va_index.md
                            reuseTopic = line.split('include: ')[1]
                            getReuseFile(reuseTopic)

                        elif tocFilenameNoSpaces.startswith('/'):
                            contentReuseList.append(tocFilenameNoSpaces)
                            tocFilenameNoStartingSlash = tocFilenameNoSpaces[1:]
                            repoName = tocFilenameNoStartingSlash.split('/', 1)[0]
                            if not os.path.isdir(self.location_dir + '/sitemap-temp/' + repoName):
                                self.log.info('Cloning ' + repoName + ' to resolve sitemap content.')
                                subprocess.call('git clone --depth 1 -b ' + self.location_github_branch + ' https://' +
                                                details["username"] + ':' + details["token"] + '@' +
                                                self.location_github_domain + '/' + cloudDocsOrg + '/' + repoName + ' ' +
                                                self.location_dir + '/sitemap-temp/' + repoName + ' --quiet', shell=True)

            try:
                with open(self.location_dir + input_file, "r+", encoding="utf8", errors="ignore") as file_open_test:
                    yaml.safe_load(file_open_test)
            except Exception as e:
                # Try to get the line number from the yaml that could not be validated.
                eString = str(e)
                self.log.error(eString)
                lineNumberLine = eString.rsplit('\n', 1)[1]
                lineNumber = lineNumberLine.split('line ')[1]
                addToErrors('The ' + input_file + ' could not be loaded to build the sitemap because ' +
                            'of a problem with output line ' + lineNumber + '.', location_sitemap_file, '',
                            details, self.log, self.location_name, '', '')
            else:
                self.log.debug('Loading: ' + self.location_dir + input_file)
                relativeLinks = ['/apidocs', '/catalog', '/docs/faqs', '/observe', '/status', '/unifiedsupport']

                def appendToFile(content, sitemapList):
                    # self.log.debug(content)
                    sitemapAnchorTest = '\n'.join(sitemapList)
                    if '{: #sitemap_' in sitemapAnchorTest:
                        # self.log.info('Evaluating sitemap anchor')
                        number = 0
                        anchorList = re.findall('{: #sitemap_(.*?)}', content, flags=re.DOTALL)
                        # self.log.info(anchorList)
                        for anchor in anchorList:
                            revisedAnchor = '{: #sitemap_' + anchor + '}'
                            if revisedAnchor in sitemapAnchorTest:
                                while revisedAnchor in sitemapAnchorTest:
                                    number = number + 1
                                    revisedAnchor = revisedAnchor.replace('}', str(number) + '}')
                                content = content.replace('{: #sitemap_' + anchor + '}', revisedAnchor)
                                # self.log.info('Revised anchor: ' + content)
                    sitemapList.append(content)
                    return (sitemapList)
                    # self.log.debug('Appending to file: ' + content)

                def titleAnchorCreation(type, title, sitemapAnchorList):
                    if type == 'anchor':
                        titleNoSpaces = title.replace(' ', '_')
                    elif type == 'link':
                        titleNoSpaces = title.replace(' ', '-')
                    else:
                        addToErrors('Type not set.', location_sitemap_file, '', details, self.log, self.location_name, '', '')
                        titleNoSpaces = title

                    titleNoSpaces = titleNoSpaces.replace(':', '').replace('#', '').replace('(', '')
                    titleNoSpaces = titleNoSpaces.replace(')', '').replace('.', '').replace('/', '').replace('\\', '')
                    titleNoSpaces = titleNoSpaces.replace('--', '-').replace('`', '').replace('--', '-')
                    titleNoSpaces = titleNoSpaces.lower()
                    while '{{' in titleNoSpaces:
                        firstpart, ignore = titleNoSpaces.split('{{', 1)
                        secondpart = ignore.split('}}', 1)[1]
                        titleNoSpaces = firstpart + secondpart
                        if '{{' not in titleNoSpaces:
                            break
                    while ('{: #sitemap_' + titleNoSpaces + '}') in sitemapAnchorList:
                        titleNoSpaces = titleNoSpaces + '_'
                    return (titleNoSpaces)

                def getLink(linkIntro, topicOrGroup, topicGroup, sitemapList):
                    try:
                        topicLabel = topicOrGroup['link']['label']
                    except Exception:
                        topicLabel = topicOrGroup['label']

                    # self.log.debug(topicOrGroup)
                    try:
                        topicLink = topicOrGroup['link']['href']
                    except Exception:
                        try:
                            topicLink = topicOrGroup['href']
                        except Exception:
                            self.log.debug('Could not get href for: ' + str(topicOrGroup))
                    try:
                        # self.log.info('In link try')
                        # self.log.info('topicLink: ' + topicLink)
                        # self.log.info('topicGroup: ' + str(topicGroup))
                        if topicLink.startswith('http'):
                            external = '{: external}'
                        else:
                            external = ''
                        if topicLink.startswith('/'):
                            if (not topicLink.startswith(tuple(relativeLinks))) and (not topicLink.startswith('/docs/')):
                                repo, topicID = topicLink.rsplit('/', 1)
                                topicLinkRevised = '/docs' + repo + '?topic=' + topicID
                                sitemapList = appendToFile('\n[' + topicLabel + '](' + topicLinkRevised + ')' + external, sitemapList)
                            else:
                                sitemapList = appendToFile('\n[' + topicLabel + '](' + topicLink + ')' + external, sitemapList)
                        else:
                            if topicGroup == 1:
                                titleNoSpaces = titleAnchorCreation('link', topicLabel, sitemapAnchorList)
                                # self.log.info('H2 in topicGroup: ' + topicLabel)
                                sitemapList = appendToFile('\n\n## ' + topicLabel + '\n{: #sitemap_' + titleNoSpaces + '}\n\n[' +
                                                           topicLabel + '](' + topicLink + ')' + external, sitemapList)
                                # self.log.info('155: ' + topicLabel)
                                # self.log.debug('Appending to file: ' + '## ' + topicLabel + '\n{: #sitemap_' +
                                # titleNoSpaces + '}\n\n[' + topicLabel + '](' + topicLink + ')' + external)
                            elif topicGroup == 2:
                                sitemapList = appendToFile('\n[' + topicLabel + '](' + topicLink + ')' + external, sitemapList)
                                # self.log.debug('Appending to file: ' + '[' + topicLabel + '](' + topicLink + ')' + external)
                            elif topicGroup == 3:
                                sitemapList = appendToFile('\n* [' + topicLabel + '](' + topicLink + ')' + external, sitemapList)
                                # self.log.debug('Appending to file: ' + '* [' + topicLabel + '](' + topicLink + ')' + external)
                    except Exception:
                        self.log.debug('In link except')
                        try:
                            topicLink = topicOrGroup['topicgroup']['topic']
                        except Exception:
                            self.log.debug('No topics in topicgroup')
                        else:
                            if not topicLink.startswith(tuple(relativeLinks)):
                                with open(self.location_dir + '/' + topicLink, "r+", encoding="utf8", errors="ignore") as file_open_topic:
                                    topicContent = file_open_topic.read()
                                    topicContent = checkForReusedSections(topicContent, topicLink)
                                    idList = re.findall('{: #(.*?)}', topicContent, flags=re.DOTALL)

                                if not idList == []:
                                    topicID = idList[0]
                                    topicLinkRevised = linkIntro + topicID

                                    sitemapList = appendToFile('\n*[' + topicLabel + '](' + topicLinkRevised + ')', sitemapList)
                                    self.log.debug('Appending to file: ' + '*[' + topicLabel + '](' + topicLinkRevised + ')', sitemapList)
                            else:
                                addToErrors('Not handling tuple', location_sitemap_file, '', details, self.log, self.location_name, '', '')
                    return (sitemapList)

                def fileEvaluation(topicInfo, navtitle, topicGroup, nestedTOC, predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList):
                    # self.log.debug('Evaluating: ')
                    # self.log.debug(topicInfo)
                    try:
                        if str(topicInfo).startswith('{\'link\':'):
                            sitemapList = getLink(linkIntro, topicInfo, topicGroup, sitemapList)
                        elif str(topicInfo).endswith('toc'):
                            repoName = topicInfo.split('/')[1]
                            # self.log.debug('repoName: ' + repoName)
                            if os.path.isfile(self.location_dir + '/sitemap-temp/' + repoName + input_file):
                                f2 = open(self.location_dir + '/sitemap-temp/' + repoName + input_file)
                                tocContent2 = yaml.safe_load(f2)
                                f2.close()
                                path2 = tocContent2['toc']['properties']['path']
                                subcollection2 = tocContent2['toc']['properties']['subcollection']
                                linkIntro2 = '/docs/' + path2 + '?topic=' + subcollection2 + '-'
                                entries2 = tocContent2['toc']['entries']
                                self.log.debug(entries2)
                                sitemapList = entriesLoop(entries2, linkIntro2, self.location_dir + '/sitemap-temp/' + repoName,
                                                          True, True, topicGroup, sitemapAnchorList, sitemapList)
                                nestedTOC = False
                            # else:
                                # self.log.debug('TOC does not exist: ' + self.location_dir + '/sitemap-temp/' + repoName + input_file)
                        elif str(topicInfo).startswith('/') or str(topicInfo).startswith('../'):
                            # self.log.info('Checking: ' + topicInfo)
                            if str(topicInfo).startswith('/'):
                                topicPath, subcollectionAndID = str(topicInfo).rsplit('/', 1)
                                repoName = topicPath.split('/')[1]
                                fileName = (subcollectionAndID.split(repoName + '-', 1)[1]) + '.md'
                            elif str(topicInfo).startswith('../'):
                                while str(topicInfo).startswith('../'):
                                    topicInfo = str(topicInfo).replace('../', '')
                                # self.log.info(topicInfo)
                                topicPath, fileName = str(topicInfo).rsplit('/', 1)
                                if '/' in topicPath:
                                    repoName = topicPath.split('/')[1]
                                else:
                                    repoName = topicPath
                                # self.log.info(topicPath)
                                # self.log.info(repoName)
                                # self.log.info(fileName)
                            if not topicPath.startswith('/'):
                                topicPath = '/' + topicPath
                            # self.log.info('Looking for ' + self.location_dir + '/sitemap-temp' + topicPath + '/' + fileName)
                            if os.path.isfile(self.location_dir + '/sitemap-temp' + topicPath + '/' + fileName):
                                # self.log.info('Found: ' + self.location_dir + '/sitemap-temp' + topicPath + '/' + fileName)
                                sitemapList = getFileContents(self.location_dir + '/sitemap-temp' + topicPath + '/' + fileName,
                                                              navtitle, topicGroup, nestedTOC, self.location_dir + '/sitemap-temp/' +
                                                              topicPath, sitemapAnchorList, sitemapList)
                            else:
                                # self.log.info('Looping for ' + topicPath)
                                for (path, dirs, files) in os.walk(self.location_dir + '/sitemap-temp' + topicPath + '/'):
                                    if '.git' not in path:
                                        for tempFile in files:
                                            tempFile = path + '/' + tempFile
                                            with open(tempFile, "r+", encoding="utf8", errors="ignore") as file_open_tempfile:
                                                topicContent = file_open_tempfile.read()
                                                topicContent = checkForReusedSections(topicContent, tempFile)
                                                idList = re.findall('{: #(.*?)}', topicContent, flags=re.DOTALL)
                                                if not idList == []:
                                                    fileTopicID = idList[0]
                                                    if fileTopicID == fileName[:-3]:
                                                        # self.log.info('Anchor matches')
                                                        if os.path.isfile(tempFile):
                                                            # self.log.info('Tmp File Exists: ' + tempFile)
                                                            sitemapList = getFileContents(tempFile, navtitle, topicGroup,
                                                                                          nestedTOC, path, sitemapAnchorList, sitemapList)
                                                            break

                        elif str(topicInfo).endswith('.md'):
                            # self.log.info('Working on')
                            # getFileContents(file,navtitle,topicGroup,nestedTOC,predictedFilePath)
                            sitemapList = getFileContents(topicInfo, navtitle, topicGroup, nestedTOC, predictedFilePath, sitemapAnchorList, sitemapList)
                        elif topicInfo['topic']:
                            file_name = topicInfo['topic']
                            try:
                                navtitle = topicInfo['navtitle']
                            except Exception:
                                navtitle = False
                            if relativeTOC is False:
                                file_name = self.location_dir + '/' + file_name
                            else:
                                file_name = predictedFilePath + '/' + file_name

                            if os.path.isfile(file_name):
                                # getFileContents(file,navtitle,topicGroup,nestedTOC,predictedFilePath)
                                sitemapList = getFileContents(file_name, navtitle, topicGroup, nestedTOC, predictedFilePath, sitemapAnchorList, sitemapList)
                            else:
                                addToErrors('Does not exist: ' + file_name, location_sitemap_file, '', details, self.log, self.location_name, '', '')
                        elif topicInfo['href']:
                            self.log.debug('Handling links!')
                            sitemapList = getLink(linkIntro, topicInfo, topicGroup, sitemapList)
                        else:
                            addToErrors('Not sure how to handle:\n' + topicInfo, location_sitemap_file, '', details, self.log, self.location_name, '', '')
                    except Exception as e:
                        if str(topicInfo).startswith('{\'topicgroup\''):
                            addToWarnings('marked-it does not support topicgroups this deep. ' +
                                          'Section not included in the sitemap: ' + str(topicInfo), location_sitemap_file, '',
                                          details, self.log, self.location_name, '', '')
                        else:
                            addToErrors('Cannot evaluate: ' + str(topicInfo), location_sitemap_file, '', details, self.log, self.location_name, '', '')
                            self.log.info(e)
                    return (sitemapList)

                def getFileContents(file, navtitle, topicGroup, nestedTOC, predictedFilePath, sitemapAnchorList, sitemapList):
                    # self.log.info('getFileContents')
                    # self.log.info('file: ' + file)
                    # self.log.info('navtitle: ' + str(navtitle))
                    # self.log.info('topicGroup: ' + str(topicGroup))
                    # self.log.info('nestedTOC: ' + str(nestedTOC))
                    # self.log.info('predictedFilePath: ' + predictedFilePath)
                    if '/sitemap-temp/' not in file:
                        if self.location_dir not in file:
                            filePath = self.location_dir + '/' + file
                        else:
                            filePath = file
                        subcollectionTemp = tocContent['toc']['properties']['subcollection']
                        linkIntro = '/docs/' + path + '?topic=' + subcollectionTemp + '-'
                    if '/sitemap-temp/' in file:
                        filePath = file
                        # If new whole file content reuse is used in the toc, then use the same subcollection as the repo
                        linkIntro = '/docs/' + path + '?topic=' + path + '-'

                    if ((os.path.isfile(filePath)) and (location_sitemap_file_name not in filePath)):
                        with open(filePath, "r+", encoding="utf8", errors="ignore") as file_open_filepath:
                            topicContent = file_open_filepath.read()
                            topicContent = re.sub('<!--(.*?)-->', '', topicContent, flags=re.DOTALL)
                            idList = re.findall('{: #(.*?)}', topicContent, flags=re.DOTALL)

                            if idList == []:
                                contentExists = False
                            else:
                                contentExists = True
                                fileTopicID = idList[0]
                                # self.log.info('fileTopicID: ' + fileTopicID)

                            if contentExists is True:
                                if '<!--' in topicContent:
                                    commentList = re.findall('<!--(.*?)-->', topicContent, flags=re.DOTALL)
                                else:
                                    commentList = []
                                if '```' in topicContent:
                                    codeblockList = re.findall('```(.*?)```', topicContent, flags=re.DOTALL)
                                else:
                                    codeblockList = []
                        # self.log.info(codeblockList)
                        if contentExists is True:

                            # self.log.info('Content exists')

                            with open(filePath, "r+", encoding="utf8", errors="ignore") as file_open_file_path:
                                # self.log.info('Opening filePath 2: ' + filePath)
                                topicContent = file_open_file_path.read()
                                topicContent = checkForReusedSections(topicContent, filePath)
                                topicContent = re.sub('<!--(.*?)-->', '', topicContent, flags=re.DOTALL)
                                topicContentLines = topicContent.split('\n')
                                anchor = ''
                                findAnchor = False
                                # self.log.info('Reading file')
                                checkForRelNotesDefLists = False
                                releaseNotesFile = False
                                for line in topicContentLines:
                                    lineNoNewlines = line.replace('\n', '')
                                    if (((not str(lineNoNewlines) in str(commentList)) and
                                            (not str(lineNoNewlines) in str(codeblockList))) or
                                            (findAnchor is True)):
                                        # self.log.info('Starting new line')
                                        # if line.startswith('#'):
                                        # self.log.debug('\n\n\n\n' + line)
                                        # self.log.debug(topicGroup)

                                        if 'content-type: release-note' in line:
                                            releaseNotesFile = True

                                        if ((line.startswith("#### ")) and (H4_ENABLED is True)):
                                            title = line.replace("#### ", "")
                                            title = title.rstrip()
                                            if (topicGroup == 4) and (nestedTOC is False):
                                                indent = '        * '
                                            elif nestedTOC is True:
                                                self.log.debug('Got in for H4')
                                                indent = '        * '
                                            else:
                                                indent = '        * '
                                            findAnchor = True
                                            checkForRelNotesDefLists = False

                                        elif ((line.startswith("### ")) and (H3_ENABLED is True)):
                                            title = line.replace("### ", "")
                                            title = title.rstrip()
                                            if (topicGroup == 4) and (nestedTOC is False):
                                                indent = '    * '
                                            # elif topicGroup == 1 and nestedTOC == False:
                                            # indent = '* '
                                            elif nestedTOC is True:
                                                # self.log.debug('Got in for H3')
                                                indent = '    * '
                                            else:
                                                indent = '    * '
                                            findAnchor = True
                                            if releaseNotesFile is True:
                                                checkForRelNotesDefLists = True

                                        elif ((line.startswith("## ")) and (H2_ENABLED is True)):
                                            title = line.replace("## ", "")
                                            title = title.rstrip()

                                            if (topicGroup == 1) and (nestedTOC is False):
                                                # self.log.info('Setting 1 indent to *')
                                                indent = '* '
                                            elif (topicGroup == 2) and (nestedTOC is False):
                                                # self.log.info('Setting 2 indent to *')
                                                indent = '* '
                                            elif (topicGroup == 3) and (nestedTOC is False):
                                                # self.log.info('Setting 3 indent to *')
                                                indent = '* '
                                            elif nestedTOC is True:
                                                # self.log.info('Got in for H2 nested toc  True')
                                                indent = '* '
                                            else:
                                                # self.log.info('Got in for H2 else')
                                                indent = '* '
                                            findAnchor = True
                                            checkForRelNotesDefLists = False
                                            if releaseNotesFile is True:
                                                checkForRelNotesDefLists = True

                                        elif line.startswith('# '):
                                            # self.log.info('H1:')
                                            # self.log.info(topicGroup)
                                            # self.log.info(nestedTOC)
                                            # self.log.info('Found H1')
                                            checkForRelNotesDefLists = False
                                            if (navtitle is False) and (nestedTOC is False):
                                                # self.log.info('navtitle and nestedtoc are false')
                                                count = 0
                                                line.count('#')
                                                count = count + 1
                                                # self.log.info('count: ' + str(count))
                                                if count > 1:
                                                    break
                                                # Makes sure to only include H1s and no possible comments in codeblocks
                                                elif count == 1:
                                                    title = line.replace('# ', '')
                                                    title = title.rstrip()
                                                    # self.log.info(title)
                                                    # if topicGroup == True:
                                                    # self.log.info('topicGroup: ' + str(topicGroup))
                                                    # Topic group heading
                                                    titleNoSpaces = titleAnchorCreation('anchor', title, sitemapAnchorList)
                                                    # self.log.info('H2 in H1 section: ' + title)
                                                    if topicGroup == 1:
                                                        # self.log.info('393: ' + title)
                                                        sitemapList = appendToFile('\n\n## ' + title + '\n{: #sitemap_' + titleNoSpaces + '}\n', sitemapList)
                                                    elif topicGroup == 2:
                                                        # self.log.info('393: ' + title)
                                                        sitemapList = appendToFile('\n\n## ' + title + '\n{: #sitemap_' + titleNoSpaces + '}\n', sitemapList)
                                                    # elif topicGroup == 3:
                                                        # self.log.info('396: ' + title)
                                                        # appendToFile('\n\n### ' + title + '\n{: #sitemap_'+ titleNoSpaces + '}\n')
                                                    indent = ''
                                                findAnchor = True
                                            elif ((navtitle is False) and (nestedTOC is True)):
                                                if topicGroup == 1:
                                                    indent = ''
                                                elif topicGroup == 2:
                                                    # VA lands here
                                                    indent = ''
                                                else:
                                                    # 'Registry public images land here
                                                    indent = ''
                                                findAnchor = True
                                                title = line.replace('# ', '')
                                                title = title.rstrip()
                                                # self.log.info(title)
                                                self.log.debug('title: ' + str(title))
                                                titleNoSpaces = titleAnchorCreation('anchor', title, sitemapAnchorList)
                                                if topicGroup == 1 or topicGroup == 2:
                                                    # self.log.info('346: ' + title)
                                                    sitemapList = appendToFile('\n\n## ' + title + '\n{: #sitemap_' + titleNoSpaces + '}\n', sitemapList)
                                                # if topicGroup == 3 or topicGroup == 4:
                                                    # 'Registry public images land here
                                                    # self.log.info('453: ' + title)
                                                    # appendToFile('\n\n### ' + title + '\n{: #sitemap_'+ titleNoSpaces + '}\n')
                                            else:
                                                indent = ''
                                                findAnchor = True
                                                title = navtitle
                                                # self.log.info(title)
                                                titleNoSpaces = titleAnchorCreation('anchor', navtitle, sitemapAnchorList)
                                                # self.log.info('H2 in H1 else: ' + navtitle)
                                                if topicGroup == 1:
                                                    sitemapList = appendToFile('\n\n## ' + navtitle + '\n{: #sitemap_' + titleNoSpaces + '}\n', sitemapList)
                                                # elif topicGroup == 2:
                                                    # appendToFile('\n\n### ' + navtitle + '\n{: #sitemap_'+ titleNoSpaces + '}\n')
                                                # elif topicGroup == 3:
                                                    # appendToFile('\n\n### ' + navtitle + '\n{: #sitemap_'+ titleNoSpaces + '}\n')

                                        elif findAnchor is True:
                                            # self.log.info('Finding anchor')
                                            # self.log.info('line: ' + line)
                                            if "{: #" in line:
                                                anchor = line.replace('{: #', '')
                                                anchor = anchor.replace('}', '')
                                                anchor = anchor.rstrip()
                                                # self.log.info('407')
                                                # self.log.info('Appending to file: ' + indent + '[' + title + '](' +
                                                # linkIntro + fileTopicID + '#' + anchor + ')')
                                                # appendToFile('\n' + indent + '[' + title + '](' + linkIntro + fileTopicID +
                                                # '#' + anchor + ')')

                                            elif line.startswith('{: notoc}'):
                                                self.log.debug('This section is set to notoc. Not including in the sitemap.')
                                                findAnchor = False
                                                anchor = ''

                                            else:
                                                # self.log.info('Creating anchor from title')

                                                if anchor == '':
                                                    anchor = titleAnchorCreation('link', title, sitemapAnchorList)
                                                    # self.log.info('413')
                                                    # self.log.info(indent + '[' + title + '](' + linkIntro + fileTopicID + '#' + titleNoSpaces + ')')

                                                if ' ' in anchor:
                                                    filePathShort = filePath.split(self.location_dir)[1]
                                                    addToWarnings('The anchor "' + anchor + '" in ' + filePathShort +
                                                                  ' contains a space and will affect the sitemap link.',
                                                                  location_sitemap_file, '',
                                                                  details, self.log,
                                                                  self.location_name, '', '')
                                                    anchor = anchor.split(' ', 1)[0]

                                                sitemapList = appendToFile('\n' + indent + '[' + title + '](' +
                                                                           linkIntro + fileTopicID + '#' + anchor + ')', sitemapList)
                                                # self.log.info('Appending: ' + indent + '[' + title + '](' + linkIntro + fileTopicID + '#' + anchor + ')')
                                                findAnchor = False
                                                anchor = ''
                                        elif checkForRelNotesDefLists is True:
                                            if ((not line.startswith('\n')) and
                                                    (not line.startswith(':')) and
                                                    (not line.startswith('{:')) and
                                                    (not line.startswith('#')) and
                                                    (not line.startswith(' '))):
                                                lineFormatted = line.replace('\n', '')
                                                if ' {: #' in lineFormatted:
                                                    lineFormatted, anchor = lineFormatted.split(' {: #', 1)
                                                    anchor = anchor[:-1]
                                                    sitemapList = appendToFile('\n    ' + indent + '[' + lineFormatted + '](' +
                                                                               linkIntro + fileTopicID + '#' + anchor + ')', sitemapList)
                                                else:
                                                    sitemapList = appendToFile('\n    ' + indent + lineFormatted, sitemapList)
                    return (sitemapList)

                def entriesLoop(entries, linkIntro, predictedFilePath, nestedTOC, relativeTOC, levelsToAdd, sitemapAnchorList, sitemapList):
                    try:
                        section = ''
                        for navgroup in entries:
                            section = navgroup
                            try:
                                mainTopicsSection = navgroup['navgroup']['topics']
                            except Exception:
                                try:
                                    mainTopicsSection = navgroup['topics']
                                except Exception:
                                    mainTopicsSection = navgroup['navgroup']['links']
                            for topicOrGroup in mainTopicsSection:
                                if str(topicOrGroup).startswith('{\'link\''):
                                    sitemapList = getLink(linkIntro, topicOrGroup, 1, sitemapList)
                                elif str(topicOrGroup).startswith('{\'include\''):
                                    sitemapList = fileEvaluation(topicOrGroup['include'], False, (1 + levelsToAdd), nestedTOC,
                                                                 predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)
                                elif str(topicOrGroup).startswith('{\'topicgroup\''):
                                    try:
                                        section = topicOrGroup
                                        topicLabel = topicOrGroup['topicgroup']['label']
                                    except Exception:
                                        topicLabel = topicOrGroup['label']
                                    titleNoSpaces = titleAnchorCreation('anchor', topicLabel, sitemapAnchorList)
                                    sitemapList = appendToFile('\n\n## ' + topicLabel + '\n{: #sitemap_' + titleNoSpaces + '}\n', sitemapList)

                                    try:
                                        topicOrGroup1 = topicOrGroup['topicgroup']['topics']
                                    except Exception:
                                        try:
                                            topicOrGroup1 = topicOrGroup['topics']
                                        except Exception:
                                            topicOrGroup1 = topicOrGroup['topicgroup']['links']
                                    # self.log.info('\n')
                                    # self.log.info(topicOrGroup1)
                                    if topicOrGroup1 is None:
                                        addToErrors('A topic group is defined but has no topics within it. The sitemap cannot continue to be built past: ' +
                                                    str(topicOrGroup), location_sitemap_file, '', details, self.log, self.location_name, '', '')
                                        break
                                    if str(topicOrGroup1).startswith('{\'link\''):
                                        sitemapList = getLink(linkIntro, topicOrGroup1, 1, sitemapList)
                                    elif str(topicOrGroup1).startswith('{\'include\''):
                                        sitemapList = fileEvaluation(topicOrGroup1['include'], False, (3 + levelsToAdd), nestedTOC,
                                                                     predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)

                                    elif str(topicOrGroup1).startswith('{\'topicgroup\''):
                                        section = topicOrGroup1
                                        try:
                                            topicLabel = topicOrGroup1['topicgroup']['label']
                                        except Exception:
                                            topicLabel = topicOrGroup1['label']

                                        try:
                                            topicOrGroup2 = topicOrGroup1['topicgroup']['topics']
                                        except Exception:
                                            topicOrGroup2 = topicOrGroup1['topics']
                                        # self.log.info('Topic group 2: ' + topicLabel)
                                        # self.log.info('\n')
                                        # self.log.info('topicOrGroup2 1:')
                                        # self.log.info(topicOrGroup2)
                                        for topicOrGroup3 in topicOrGroup2:
                                            section = topicOrGroup3
                                            if str(topicOrGroup3).startswith('{\'link\''):
                                                sitemapList = getLink(linkIntro, topicOrGroup3, 2, sitemapList)
                                            elif str(topicOrGroup3).startswith('{\'include\''):
                                                sitemapList = fileEvaluation(topicOrGroup3['include'], False, (4 + levelsToAdd), nestedTOC,
                                                                             predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)
                                            elif str(topicOrGroup3).startswith('{\'topicgroup\''):
                                                try:
                                                    topicLabel = topicOrGroup3['topicgroup']['label']
                                                except Exception:
                                                    topicLabel = topicOrGroup3['label']
                                                try:
                                                    topicOrGroup4 = topicOrGroup3['topicgroup']['topics']
                                                except Exception:
                                                    topicOrGroup4 = topicOrGroup3['topics']
                                                # self.log.info('Topic group 3: ' + topicLabel)
                                                # self.log.info('\n')
                                                # self.log.info(topicOrGroup3)
                                                for topicOrGroup5 in topicOrGroup4:
                                                    section = topicOrGroup5
                                                    if str(topicOrGroup5).startswith('{\'topicgroup\''):
                                                        try:
                                                            topicLabel = topicOrGroup5['topicgroup']['label']
                                                        except Exception:
                                                            topicLabel = topicOrGroup5['label']
                                                        # self.log.info('Topic group 4: ' + topicLabel)
                                                        try:
                                                            topicOrGroup6 = topicOrGroup5['topicgroup']['topics']
                                                        except Exception:
                                                            topicOrGroup6 = topicOrGroup5['topics']
                                                        addToErrors('Needs another topicgroup', location_sitemap_file, '', details,
                                                                    self.log, self.location_name, '', '')
                                                        # self.log.info('\n')
                                                        # self.log.info(topicOrGroup3)
                                                        for topicOrGroup7 in topicOrGroup6:
                                                            sitemapList = fileEvaluation(topicOrGroup7, False, (4 + levelsToAdd), nestedTOC,
                                                                                         predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)
                                                    elif str(topicOrGroup5).startswith('{\'include\''):
                                                        sitemapList = fileEvaluation(topicOrGroup5['include'], False, (5 + levelsToAdd), nestedTOC,
                                                                                     predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)
                                                    elif str(topicOrGroup5).startswith('{\'link\''):
                                                        sitemapList = getLink(linkIntro, topicOrGroup5, 3, sitemapList)
                                                    else:
                                                        for topicOrGroup6 in topicOrGroup5:
                                                            if str(topicOrGroup6).startswith('{\'link\''):
                                                                sitemapList = getLink(linkIntro, topicOrGroup6, 4, sitemapList)
                                                            elif str(topicOrGroup6).startswith('{\'include\''):
                                                                sitemapList = fileEvaluation(topicOrGroup6['include'], False, (6 + levelsToAdd), nestedTOC,
                                                                                             predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)
                                                            else:
                                                                sitemapList = fileEvaluation(topicOrGroup6, False, (4 + levelsToAdd),
                                                                                             nestedTOC, predictedFilePath, relativeTOC,
                                                                                             sitemapAnchorList, sitemapList)
                                            else:
                                                for topicOrGroup4 in topicOrGroup3:
                                                    if str(topicOrGroup4).startswith('{\'link\''):
                                                        sitemapList = getLink(linkIntro, topicOrGroup4, 3, sitemapList)
                                                    elif str(topicOrGroup4).startswith('{\'include\''):
                                                        sitemapList = fileEvaluation(topicOrGroup4['include'], False, (5 + levelsToAdd), nestedTOC,
                                                                                     predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)
                                                    elif str(topicOrGroup4).startswith('{\'topicgroup\''):
                                                        try:
                                                            section = topicOrGroup4
                                                            topicLabel = topicOrGroup4['topicgroup']['label']
                                                        except Exception:
                                                            topicLabel = topicOrGroup4['label']
                                                        try:
                                                            topicOrGroup5 = topicOrGroup4['topicgroup']['topics']
                                                        except Exception:
                                                            topicOrGroup5 = topicOrGroup4['topics']
                                                        for topicOrGroup6 in topicOrGroup5:
                                                            sitemapList = fileEvaluation(topicOrGroup6, False, (5 + levelsToAdd), nestedTOC,
                                                                                         predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)
                                                    else:
                                                        sitemapList = fileEvaluation(topicOrGroup4, False, (3 + levelsToAdd), nestedTOC,
                                                                                     predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)
                                    else:
                                        for topicOrGroup2 in topicOrGroup1:
                                            # self.log.info('\ntopicOrGroup2 2:')
                                            # self.log.info(topicOrGroup2)
                                            if str(topicOrGroup2).startswith('{\'link\''):
                                                sitemapList = getLink(linkIntro, topicOrGroup2, 2, sitemapList)
                                            elif str(topicOrGroup2).startswith('{\'include\''):
                                                sitemapList = fileEvaluation(topicOrGroup2['include'], False, (4 + levelsToAdd), nestedTOC,
                                                                             predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)
                                            elif str(topicOrGroup2).startswith('{\'topicgroup\''):
                                                try:
                                                    section = topicOrGroup2
                                                    topicLabel = topicOrGroup2['topicgroup']['label']
                                                except Exception:
                                                    topicLabel = topicOrGroup2['label']

                                                # self.log.info('topicLabel: ' + topicLabel)

                                                titleNoSpaces = titleAnchorCreation('anchor', topicLabel, sitemapAnchorList)
                                                sitemapList = appendToFile('\n\n### ' + topicLabel + '\n{: #sitemap_' + titleNoSpaces + '}\n', sitemapList)

                                                try:
                                                    topicOrGroup3 = topicOrGroup2['topicgroup']['topics']
                                                except Exception:
                                                    try:
                                                        topicOrGroup3 = topicOrGroup2['topics']
                                                    except Exception:
                                                        if str(topicOrGroup2).startswith('{\'topicgroup\''):
                                                            try:
                                                                topicLabel = topicOrGroup2['topicgroup']['label']
                                                            except Exception:
                                                                topicLabel = topicOrGroup2['label']
                                                            try:
                                                                topicOrGroup3 = topicOrGroup2['topicgroup']['topics']
                                                            except Exception:
                                                                try:
                                                                    topicOrGroup3 = topicOrGroup2['topics']
                                                                except Exception:
                                                                    topicOrGroup3 = topicOrGroup2['topicgroup']['links']
                                                else:
                                                    for topicOrGroup4 in topicOrGroup3:
                                                        if str(topicOrGroup4).startswith('{\'include\''):
                                                            sitemapList = fileEvaluation(topicOrGroup4['include'], False, (4 + levelsToAdd), nestedTOC,
                                                                                         predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)
                                                        else:
                                                            sitemapList = fileEvaluation(topicOrGroup4, False, (4 + levelsToAdd), nestedTOC,
                                                                                         predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)
                                            else:
                                                # self.log.info('Evaluating')
                                                # self.log.info(topicOrGroup2)
                                                sitemapList = fileEvaluation(topicOrGroup2, False, (3 + levelsToAdd), nestedTOC,
                                                                             predictedFilePath, relativeTOC, sitemapAnchorList, sitemapList)

                                else:
                                    sitemapList = fileEvaluation(topicOrGroup, False, (1 + levelsToAdd), nestedTOC, predictedFilePath,
                                                                 relativeTOC, sitemapAnchorList, sitemapList)

                    except Exception as e:
                        addToErrors('The sitemap could not be generated because of an error in the toc: ' +
                                    str(e) + '\n' + str(section), location_sitemap_file, '', details, self.log,
                                    self.location_name, '', '')
                    return (sitemapList)

                with open(self.location_dir + input_file, "r", encoding="utf8", errors="ignore") as file_open_input_path:
                    tocContent = yaml.safe_load(file_open_input_path)
                path = str(tocContent['toc']['properties']['path'])
                subcollection = tocContent['toc']['properties']['subcollection']
                linkIntro = '/docs/' + path + '?topic=' + subcollection + '-'
                entries = tocContent['toc']['entries']

                with open(self.location_dir + location_sitemap_file, "r", encoding="utf8", errors="ignore") as h:
                    sitemapList = [h.read()]

                # self.log.info(entries)

                sitemapList = entriesLoop(entries, linkIntro, self.location_dir, False, False, 0, sitemapAnchorList, sitemapList)

                sitemapList.append('\n')

                completeSitemap = "\n".join(sitemapList)
                writeResult(self, details, location_sitemap_file_name, self.sitemap_file, location_sitemap_folderPath, completeSitemap)

                self.log.info('Sitemap complete.')

        else:
            addToErrors('The ' + input_file + ' could not be found at this location to build the sitemap from: ' +
                        self.location_dir + input_file, location_sitemap_file, '', details, self.log, self.location_name, '', '')

    except Exception as e:
        addToErrors('The sitemap could not be generated: ' + str(e), location_sitemap_file, '', details, self.log, self.location_name, '', '')

    if os.path.isdir(self.location_dir + '/sitemap-temp'):
        shutil.rmtree(self.location_dir + '/sitemap-temp')
