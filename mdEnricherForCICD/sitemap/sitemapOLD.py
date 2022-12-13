#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def sitemapOLD(self, details):

    # !/usr/bin/env python
    import os
    import traceback
    import re
    import shutil
    import subprocess
    import requests
    import base64

    self.log.info("\n")
    self.log.info("Creating the sitemap from the toc file.")
    if details["builder"] == 'local':
        self.log.info('Locally, the sitemap might be incomplete. ' +
                      'Credentials are not configured locally to go to Github and retrieve the ' +
                      'content defined in the TOC that is reused from other services.')

    self.log.debug("\n\n")
    self.log.debug("-------------------------------------------------------------")
    self.log.debug("UPDATE SITEMAP")
    self.log.debug("-------------------------------------------------------------\n")

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

    self.log.info('ibm_cloud_docs_sitemap_depth: ' + details["ibm_cloud_docs_sitemap_depth"])
    self.log.info('H1_ENABLED: True')
    self.log.info('H2_ENABLED: ' + str(H2_ENABLED))
    self.log.info('H3_ENABLED: ' + str(H3_ENABLED))

    workingDir = self.location_dir
    self.log.debug('Working directory: ' + workingDir)

    # if sitemapGithubRepo == None:
    sitemapGithubRepo = self.location_github_repo

    cloudDocsOrg = 'cloud-docs'

    os.chdir(workingDir)
    self.log.debug('Current directory: ' + os.getcwd())

    self.log.debug('Repo: ' + sitemapGithubRepo)
    contentReuseList = []
    indentations = ['/', '    /', '        /']

    if not os.path.isfile(workingDir + '/toc'):
        self.log.warning('No toc file to work with. Not creating a sitemap.')
    else:
        # Go through the toc and figure out what kind each entry is
        with open(workingDir + '/toc', "r+", encoding="utf8", errors="ignore") as file_open:
            file_read = file_open.readlines()
            for line in file_read:
                # Get the subcollection name
                if 'subcollection' in line:
                    subcollectionList = re.findall(r'subcollection\=\".*?\"', line)
                    subcollection = subcollectionList[0]
                    subcollection = subcollection.split('"')[1]
                    self.log.debug('Subcollection: ' + subcollection)

                # If it's pulling in a whole toc, then clone that repo
                elif (('toc' in line) and (not details["builder"] == 'local')):

                    tocFilenameNoSpaces = line.replace(' ', '').replace('\n', '')
                    contentReuseList.append(tocFilenameNoSpaces)
                    tocFilenameNoStartingSlash = tocFilenameNoSpaces[1:]
                    repoName, backhalf = tocFilenameNoStartingSlash.split('/', 1)

                    subprocess.call('git clone --depth 1 -b ' + self.location_github_branch + ' https://' +
                                    details["username"] + ':' + details["token"] + '@' + self.location_github_domain + '/' +
                                    cloudDocsOrg + '/' + repoName + ' ' + workingDir + '/sitemap-temp/' + repoName + ' --quiet',
                                    shell=True)
                    if not os.path.isdir(workingDir + '/sitemap-temp/' + repoName):
                        subprocess.call('git clone --depth 1 -b ' + self.location_github_branch + ' https://' +
                                        self.username + ':' + details["token"] + '@' + self.location_github_domain + '/' +
                                        cloudDocsOrg + '/' + repoName + ' ' + workingDir + '/sitemap-temp/' + repoName + ' --quiet',
                                        shell=True)

                # If it's a relative link to a file in another repo, clone that repo
                elif ((line.startswith('/') or
                       line.startswith('    /') or
                       line.startswith('        /') or
                       line.startswith('            /')) and
                      (not details["builder"] == 'local')):

                    tocFilenameNoSpaces = line.replace(' ', '').replace('\n', '')
                    contentReuseList.append(tocFilenameNoSpaces)
                    tocFilenameNoStartingSlash = tocFilenameNoSpaces[1:]
                    repoName, backhalf = tocFilenameNoStartingSlash.split('/', 1)

                    topicID = backhalf.split(repoName + '-', 1)[1]

                    if not os.path.isfile(workingDir + '/' + topicID + '.md'):
                        try:
                            fileSourceGet = requests.get(self.location_github_branch + '/' + repoName + '/contents/' +
                                                         topicID + '.md?ref=' + self.location_github_branch,
                                                         auth=(details["username"], details["token"]))
                            if not fileSourceGet.status_code == 200:
                                fileSourceGet = requests.get(self.location_github_branch + '/' + repoName + '/contents/' +
                                                             topicID + '.md?ref=' + self.location_github_branch,
                                                             auth=(details["username"], details["token"]))
                            if not fileSourceGet.status_code == 200:
                                subprocess.call('git clone --depth 1 -b ' + self.location_github_branch +
                                                ' https://' + details["username"] + ':' + details["token"] + '@' +
                                                self.location_github_domain + '/' + self.location_github_org + '/' +
                                                repoName + ' ' + workingDir + '/sitemap-temp/' + repoName + ' --quiet', shell=True)
                            if fileSourceGet.status_code == 200:
                                fileSourceJSON = fileSourceGet.json()
                                fileSourceEncoded = fileSourceJSON['content']
                                fileSourceDecoded = base64.b64decode(fileSourceEncoded)
                                fileSourceDecodedUTF = fileSourceDecoded.decode("utf-8")
                                if not os.path.isdir(workingDir + '/sitemap-temp/'):
                                    os.mkdir(workingDir + '/sitemap-temp/')
                                if not os.path.isdir(workingDir + '/sitemap-temp/' + repoName):
                                    os.mkdir(workingDir + '/sitemap-temp/' + repoName)
                                with open(workingDir + '/sitemap-temp/' + repoName + '/' + topicID + '.md',
                                          'w+', encoding="utf8", errors="ignore") as file_open:
                                    file_open.write(fileSourceDecodedUTF)

                        except Exception as e:
                            self.log.debug('Could not get: ' + topicID)
                            self.log.debug(e)

        file2 = workingDir + '/sitemap.md'
        self.log.debug('Sitemap location: ' + workingDir + '/sitemap.md')

        source: dict[dict[str, str], dict[str, str]] = {}  # type: ignore[misc]
        fileList: list[str] = []  # type: ignore[misc]
        h1 = ""
        sitemapAnchorList: list[str] = []  # type: ignore[misc]

        # Go through every file and get a list of files that will be included in the sitemap
        for root, dirs, files in os.walk(workingDir):

            for file in files:
                if ((not file == file2) and
                    (file.endswith('.md') and
                                  ('reuse-pages' not in root) and
                                  (details["reuse_snippets_folder"] not in root) and
                                  ('.git' not in root) and
                                  ('sitemap' not in file) and
                                  ('images' not in root) and
                                  ('README.md' not in file))):
                    fileList.append(root + '/' + file)

        self.log.debug('baseURL: ' + sitemapGithubRepo + '?topic=' + subcollection + '-')
        for file in sorted(fileList):

            # Start creating the link that will get used in the sitemap later
            baseURL = '/docs/' + sitemapGithubRepo + '?topic=' + subcollection + '-'
            originalBaseURL = baseURL
            originalBaseRepo = subcollection

            # Get the content from each file
            with open(file, "r+", encoding="utf8", errors="ignore") as f:
                topicContent = f.read()

                # Check to see if there is an anchor in the topic.
                # If there isn't, don't include it in the dictionary at all.
                # Helps eliminate some files that might be in progress or a readme or something that might have snuck through
                idList = re.findall('{: #(.*?)}', topicContent, flags=re.DOTALL)

                if idList == []:
                    contentExists = False
                else:
                    contentExists = True
                    fileTopicID = idList[0]

                if contentExists is True:
                    # Create a dictionary with an entry for that file name
                    source[file] = {}

                    h2 = ''
                    h3 = ''
                    baseRepo = originalBaseRepo

                    # Might need to reset the link details if it's a topic being pulled into this toc from another repo.
                    # It needs to have the name of this repo but the subcollection for that other repo
                    for contentReuse in contentReuseList:
                        baseURL = originalBaseURL
                        baseRepo = originalBaseRepo

                        tocFilenameNoStartingSlash = contentReuse[1:]
                        repoName, backhalf = tocFilenameNoStartingSlash.split('/', 1)
                        reuseTopicID = contentReuse.replace('/' + repoName + '/' + repoName + '-', '')
                        # Ignore the .md to generate a link in context of this repo

                        if ((fileTopicID == reuseTopicID) or (('/' + repoName + '/') in (file + '/'))):
                            baseURL = '/docs/' + self.location_github_repo + '?topic=' + repoName + '-'
                            self.log.debug('Revised baseURL: ' + '/docs/' + sitemapGithubRepo + '?topic=' + repoName + '-')
                            baseRepo = repoName
                            break

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
                        source[file]['baseRepo'] = baseRepo
                        for line in lines:
                            linecount = linecount + 1
                            anchorline = linecount
                            lineNumberLength = len(str(anchorline))
                            if lineNumberLength == 5:
                                anchorlineStr = '0' + str(anchorline)
                            elif lineNumberLength == 4:
                                anchorlineStr = '00' + str(anchorline)
                            elif lineNumberLength == 3:
                                anchorlineStr = '000' + str(anchorline)
                            elif lineNumberLength == 2:
                                anchorlineStr = '0000' + str(anchorline)
                            elif lineNumberLength == 1:
                                anchorlineStr = '00000' + str(anchorline)
                            lineNoNewlines = line.replace('\n', '')

                            if ((not str(lineNoNewlines) in str(commentList)) and (not str(lineNoNewlines) in str(codeblockList))):

                                if ((line.startswith("### ")) and (H3_ENABLED is True)):
                                    line1 = line.replace("### ", "")
                                    # self.log.debug('line 1 = ' + line1)
                                    line2 = line1.rstrip()
                                    # self.log.debug('line2 = ' + line2)
                                    title = line2+']'.rstrip()
                                    h3 = h3 + ';' + str(anchorlineStr) + '$[' + title + '(' + str(baseURL)
                                    source[file]['h3'] = h3

                                elif ((line.startswith("## ")) and (H2_ENABLED is True)):
                                    line1 = line.replace("## ", "")
                                    # self.log.debug('line 1 = ' + line1)
                                    line2 = line1.rstrip()
                                    # self.log.debug('line2 = ' + line2)
                                    title = line2+']'.rstrip()
                                    h2 = h2 + ';' + str(anchorlineStr) + '$[' + title + '(' + str(baseURL)
                                    source[file]['h2'] = h2

                                elif line.startswith('# '):
                                    count = 0
                                    line.count('#')
                                    count = count + 1
                                    if count > 1:
                                        break
                                    elif count == 1:
                                        line1 = line.replace('# ', '')
                                        line2 = line1.rstrip()
                                        title = line2 + ']'.rstrip()
                                        h1 = '[' + str(anchorlineStr) + '$[' + str(title) + '(' + str(baseURL)
                                        try:
                                            source[file]['draft-h1']
                                        except Exception:
                                            source[file]['draft-h1'] = str(h1)

        # get h1s and append anchor
        self.log.info('Including H1 headers.')
        for filename in source:
            # self.log.debug('Getting values for: ' + filename)
            try:
                h1all = source[filename]['draft-h1']
            except Exception as e:
                self.log.warning('There is an issue processing the conrefs. ' +
                                 'There might be a file that is entirely removed by staging tags, though the ' +
                                 'file is referenced in the prod TOC. Check to see if there are staging tags that ' +
                                 'need to be removed from conref files or if a staging-only topic needs tags ' +
                                 'around it in the TOC.')
                self.log.warning(filename)
                self.log.warning(source[filename])
                self.log.warning(e)
            else:
                # self.log.debug(title2)
                linenumber, goodlink = h1all.rsplit('$', 1)
                linenumber = linenumber.replace('[', '')
                # self.log.debug(linenumber)
                if os.path.isfile(str(filename)):
                    with open(str(filename), "r+", encoding="utf8", errors="ignore") as file_openh1:
                        file_readh1 = file_openh1.readlines()
                        for i, anchor in enumerate(file_readh1):
                            if int(i) == int(linenumber):
                                if 'notoc' not in anchor:
                                    if "{: #" in anchor:
                                        anchor = anchor.replace('{: #', '')
                                        anchor = anchor.replace('}', ')')
                                        goodh1 = goodlink + anchor
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
                        with open(str(filename), "r+", encoding="utf8", errors="ignore") as file_open_h2:
                            file_read_h2 = file_open_h2.readlines()
                        # self.log.debug(h2list)
                        for h2 in h2list:
                            noTocFound = False
                            # self.log.debug(h2list)
                            countColons = h2.count('$')
                            if countColons == 1:
                                linenumber, goodlink = h2.split('$')
                                linenumber = linenumber.replace('[', '')
                                anchorFound = False
                                for i, anchor in enumerate(file_read_h2):
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
                                    goodAnchor = goodtitle.replace(' ', '-').replace(':', '').replace('#', '')
                                    goodAnchor = goodAnchor.lower()
                                    goodAnchor = '#' + goodAnchor + ')'
                                    anchorFound = True
                                if ((noTocFound is False) and (anchorFound is True)):
                                    goodh2 = goodh2 + ';' + linenumber + '$' + goodlink + topicID + goodAnchor
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
                        with open(str(filename), "r+", encoding="utf8", errors="ignore") as file_open_h3:
                            file_read_h3 = file_open_h3.readlines()
                        for h3 in h3list:
                            noTocFound = False
                            # self.log.debug(h2list)
                            countColons = h3.count('$')
                            if countColons == 1:
                                linenumber, goodlink = h3.split('$')
                                linenumber = linenumber.replace('[', '')

                                anchorFound = False
                                for i, anchor in enumerate(file_read_h3):
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
                                    goodAnchor = goodtitle.replace(' ', '-').replace(':', '').replace('#', '')
                                    goodAnchor = goodAnchor.lower()
                                    goodAnchor = '#' + goodAnchor + ')'
                                    anchorFound = True
                                if ((noTocFound is False) and (anchorFound is True)):
                                    goodh3 = goodh3 + ';' + linenumber + '$' + goodlink + topicID + goodAnchor

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

            def reuseLoop(tocFilename, topicGroup):
                tocFilenameNoSpaces = tocFilename.replace(' ', '').replace('\n', '')
                tocFilenameNoStartingSlash = tocFilenameNoSpaces[1:]
                # self.log.info(tocFilenameNoStartingSlash)
                repoName, backhalf = tocFilenameNoStartingSlash.split('/', 1)
                topicID = backhalf.split(repoName + '-', 1)[1]
                # self.log.info('topicID: ' + topicID)
                loop(topicID, topicGroup)

            def tocLoop(tocFilename, topicGroup):
                self.log.debug('Still need to handle nested toc files.')
                # This goes and gets the toc, but if there's content reuse in there, it's not handled yet
                repoName = tocFilename.split('/')[1]
                # self.log.info('sitemap-temp dir:')
                # self.log.info(os.listdir(workingDir + '/sitemap-temp/'))
                # self.log.info('sitemap-temp repo dir:')
                # self.log.info(os.listdir(workingDir + '/sitemap-temp/' + repoName))
                with open(workingDir + '/sitemap-temp/' + repoName + '/toc', 'r', encoding="utf8", errors="ignore") as file_open:
                    reusedTOC = file_open.readlines()
                    for line in reusedTOC:
                        if (('[' in line) or ('.md' in line)):
                            tocFilename = line.replace(' ', '')
                            # self.log.info('Handling from toc: ' + tocFilename)
                            loop(tocFilename, topicGroup)
                        elif (line.startswith('/') or
                              line.startswith('    /') or
                              line.startswith('        /') or
                              line.startswith('            /') and
                              (not details["builder"] == 'local')):
                            tocFilenameNoSpaces = line.replace(' ', '').replace('\n', '')
                            tocFilenameNoStartingSlash = tocFilenameNoSpaces[1:]
                            repoName, backhalf = tocFilenameNoStartingSlash.split('/', 1)
                            topicID = backhalf.split(repoName + '-', 1)[1]
                            # self.log.info('Handling from toc: ' + topicID + '.md')
                            loop(topicID + '.md', topicGroup)

            def loop(tocFilename, topicGroup):
                # In case the link in the toc just uses the topic id without the .md file name,
                # go get the file name from the dictionary first
                if ('.md' not in tocFilename) and ('{' in tocFilename) and (not tocFilename == ''):
                    for filename, info in list(source.items()):
                        # self.log.info(info)
                        if ('\'topicID\': \'' + tocFilename) in str(info):
                            filenameShort = str(filename).rsplit('/', 1)[1]
                            tocFilename = filenameShort
                            break
                if (('.md' in tocFilename) and (not tocFilename.endswith('sitemap.md'))):

                    # Compare the repo name and file name from the toc file with the repo name and file name
                    # that's stored in the source list to make sure you're getting the right one.
                    # There might be similarly named files in different folders or repos.

                    # Start with getting the repo and the file name of what's in the toc
                    tempTocFilename = tocFilename.replace(' ', '').replace('	', '').replace('	', '').replace('  ', ' ').replace('\t', '').replace('\n', '')
                    try:
                        tocFileNameBaseRepo = source[workingDir + '/' + tempTocFilename]['baseRepo']
                    except Exception:
                        # self.log.info('\n\ntocFilename:' + tocFilename)
                        self.log.debug('1. File listed in the toc does not exist in this location: ' + workingDir + '/' + tempTocFilename)
                        tocFileNameBaseRepo = 'nomatch1'
                        # Check the temp directory for the other cloned repos for content reuse
                        try:
                            if '/' in tempTocFilename:
                                tocFileNameBaseRepo = tempTocFilename.rsplit('/', 1)[0]
                            tocFileNameBaseRepo = source[workingDir + '/sitemap-temp/' + tocFileNameBaseRepo + '/' + tempTocFilename]['baseRepo']
                            # self.log.info('1. Found! tocFileNameBaseRepo: ' + tocFileNameBaseRepo)
                        except Exception:
                            self.log.debug('2. File listed in the toc does not exist in this location: ' +
                                           workingDir + '/sitemap-temp/' + tocFileNameBaseRepo + '/' + tempTocFilename)
                            matchFound = True
                            for root, dirs, files in os.walk(workingDir + '/sitemap-temp/'):
                                for directory in dirs:
                                    if '.git' not in root:
                                        try:
                                            tocFileNameBaseRepo = source[workingDir + '/sitemap-temp/' + directory + '/' + tempTocFilename]['baseRepo']
                                            # self.log.info('2. Found! tocFileNameBaseRepo: ' + tocFileNameBaseRepo)
                                            # print('baseRepo: ' + tocFileNameBaseRepo)
                                            matchFound = True
                                            break
                                        except Exception:
                                            self.log.debug('3. File listed in the toc does not exist in this location: ' +
                                                           workingDir + '/sitemap-temp/' + directory + '/' + tempTocFilename)
                                if matchFound is True:
                                    break
                    if '/' in tempTocFilename:
                        tempTocFilename = tempTocFilename.rsplit('/', 1)[1]

                    # Next get the repo name and the file name of what's stored in the source list
                    for filename, info in list(source.items()):
                        sourceFileNameBaseRepo = source[filename]['baseRepo']
                        filenameShort = str(filename).rsplit('/', 1)[1]
                        filenameShort = filenameShort.replace(' ', '').replace('	', '').replace('	', '').replace('  ', ' ').replace('\t', '').replace('\n', '')

                        # Now compare the repo names and file names of the two and if they match, then continue
                        if ((sourceFileNameBaseRepo + '/' + str(filenameShort)) == (tocFileNameBaseRepo + '/' + str(tempTocFilename))):
                            # self.log.info(filenameShort + ' is in ' + tocFilename)
                            self.log.debug('\n')
                            debugFilename = str(source[filename])
                            self.log.debug('Working with: ' + str(debugFilename.encode('utf-8', errors='ignore')))
                            try:
                                self.log.debug('H1: ' + str(source[filename]['h1']) + ', topicGroup value: ' + str(topicGroup))
                            except Exception:
                                self.log.error('Check for missing anchors.')
                            if topicGroup is True:
                                g.write('\n\n' + source[filename]['h1'])
                            else:
                                topicTitle = source[filename]['h1']
                                topicTitle = topicTitle.split(']')[0]
                                topicTitle = topicTitle.split('[')[1]
                                # Write once without a link
                                g.write('\n\n\n## ' + topicTitle)
                                topicTitleNoSpaces = topicTitle.lower()
                                # Not sure why blockchain has these extra tabs in their headings - must be how the toc is configured with tabs?
                                topicTitleNoSpaces = topicTitleNoSpaces.replace(' ', '_').replace('	', '').replace('	', '').replace('  ', ' ').replace('\t', '')
                                if '{{' in topicTitleNoSpaces:
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
                                h2ListLOCATION_NAMEed = []
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
                                        h2LOCATION_NAMEed = h2.replace('$', '$H2$')
                                        h2ListLOCATION_NAMEed.append(h2LOCATION_NAMEed)

                                    self.log.debug('h2ListLOCATION_NAMEed:' + str(str(h2ListLOCATION_NAMEed).encode('utf-8', errors='ignore')))

                            if H3_ENABLED is True:
                                h3ListLOCATION_NAMEed = []
                                try:
                                    h3s = source[filename]['goodh3']
                                except Exception:
                                    self.log.debug('        No h3s in this MD topic.')
                                else:
                                    h3List = h3s.split(';')
                                    self.log.debug('h3List:' + str(str(h3List).encode('utf-8', errors='ignore')))
                                    for h3 in h3List:
                                        h3LOCATION_NAMEed = h3.replace('$', '$H3$')
                                        h3ListLOCATION_NAMEed.append(h3LOCATION_NAMEed)
                                    self.log.debug('h3ListLOCATION_NAMEed:' + str(str(h3ListLOCATION_NAMEed).encode('utf-8', errors='ignore')))

                            combinedListLOCATION_NAMEed: list[str] = []  # type: ignore[misc]
                            if H2_ENABLED is True:
                                combinedListLOCATION_NAMEed = combinedListLOCATION_NAMEed + h2ListLOCATION_NAMEed
                            if H3_ENABLED is True:
                                combinedListLOCATION_NAMEed = combinedListLOCATION_NAMEed + h3ListLOCATION_NAMEed

                            sortedListLOCATION_NAMEed = sorted(combinedListLOCATION_NAMEed)

                            sortedListLOCATION_NAMEedEncoded = str(sortedListLOCATION_NAMEed).encode('utf-8', errors='ignore')
                            self.log.debug('sortedListLOCATION_NAMEed: ' + str(sortedListLOCATION_NAMEedEncoded))

                            for listItem in sortedListLOCATION_NAMEed:
                                dollarCount = listItem.count('$')
                                if dollarCount == 2:

                                    location_name = listItem.split('$')[1]
                                    link = listItem.split('$')[2]
                                    # self.log.debug('lineNumber: ' + lineNumber)
                                    # self.log.debug('location_name: ' + location_name)
                                    # self.log.debug('link: ' + link)
                                    if location_name == 'H2':
                                        if not link == '':
                                            linkEncoded = str(link.rstrip()).encode('utf-8', errors='ignore')
                                            self.log.debug('    H2: ' + str(linkEncoded))

                                            if topicGroup is True:
                                                g.write('\n* ' + link.rstrip())
                                                # self.log.debug('Writing H2: ' + str(linkEncoded))
                                            else:
                                                g.write('\n\n* ' + link.rstrip())
                                                # self.log.debug('Writing H2: ' + str(linkEncoded))
                                    elif location_name == 'H3':
                                        if not link == '':
                                            linkEncoded = str(link.rstrip()).encode('utf-8', errors='ignore')
                                            self.log.debug('        H3: ' + str(linkEncoded))
                                            if topicGroup is True:
                                                g.write('\n    * ' + link.rstrip())
                                                # self.log.debug('Writing H3: ' + str(linkEncoded))
                                            else:
                                                g.write('\n    * ' + link.rstrip())
                                                # self.log.debug('Writing H3: ' + str(linkEncoded))
                                # else:
                                    # self.log.debug('Not enough dollar signs to split: ' + listItem)
                            break
                        # elif str(filenameShort) in str(tempTocFilename):
                        # self.log.info('Did not find: ' + filenameShort + ' in ' + tempTocFilename)
                        # self.log.info('"' + filenameShort + '"')
                        # self.log.info('"' + tempTocFilename + '"')

                elif '[' in tocFilename:
                    # self.log.info('working with []: '+ tocFilename)

                    if (('                ' in tocFilename) and (topicGroup is True)):
                        tocFilename = tocFilename.replace('    ', '')
                        self.log.debug('            H4 True: ' + tocFilename)
                        g.write('\n * ' + tocFilename + '{: external}')

                    elif (('            ' in tocFilename) and (topicGroup is True)):
                        tocFilename = tocFilename.replace('    ', '')
                        self.log.debug('        H3 True: ' + tocFilename)
                        g.write('\n* ' + tocFilename + '{: external}')

                    elif (('        ' in tocFilename) and (topicGroup is True)):
                        tocFilename = tocFilename.replace('    ', '')
                        self.log.debug('    H2 True: ' + tocFilename)
                        g.write('\n\n' + tocFilename + '{: external}')

                    elif (('        ' in tocFilename) and (topicGroup is False)):
                        tocFilename = tocFilename.replace('    ', '')
                        self.log.debug('    H2 False: ' + tocFilename)
                        g.write('\n' + tocFilename + '{: external}')

                    elif (('    ' in tocFilename) and (topicGroup is True)):
                        tocFilename = tocFilename.replace('    ', '')
                        self.log.debug('    H1 True: ' + tocFilename)
                        g.write('\n' + tocFilename + '{: external}')

                    elif (('    ' in tocFilename) and (topicGroup is False)):
                        tocFilename = tocFilename.replace('    ', '')
                        self.log.debug('H1 False: ' + tocFilename)
                        if '[' in tocFilename:
                            firstHalf = tocFilename.split('[')[1]
                            titleH2 = firstHalf.split(']')[0]
                        else:
                            titleH2 = tocFilename
                        g.write('\n\n\n## ' + titleH2)
                        if '[' in tocFilename:
                            g.write('\n\n' + tocFilename + '{: external}')
                        else:
                            topicTitleNoSpaces = tocFilename.replace(' ', '')
                            topicTitleNoSpaces = topicTitleNoSpaces.lower()
                            g.write('\n{: #sitemap_' + topicTitleNoSpaces + '}\n')
                    else:
                        self.log.debug('Didn\'t know what to do with: ' + tocFilename)

            with open(workingDir + '/toc', "r+", encoding="utf8", errors="ignore") as file_open_toc:
                file_read_toc = file_open_toc.read()
                # subcollectionList = re.findall(r'subcollection\=\".*?\"',f)

                file_read_toc_nonewlines = file_read_toc.replace('\n    \n', '\n\n')

                navgroupList = re.findall(r"\{\: \.navgroup(.*?)\{\: \.navgroup\-end", file_read_toc_nonewlines, re.DOTALL)
                # navgroupList = re.findall(r"\.*?\}",fString, re.DOTALL)

                checkForUnclosedNavGroups = file_read_toc_nonewlines
                for navgroup in navgroupList:
                    checkForUnclosedNavGroups = checkForUnclosedNavGroups.replace(navgroup, '')
                if '{: .navgroup ' in checkForUnclosedNavGroups:
                    self.log.warning('Warning: Unclosed navgroup in this toc')

                for navgroup in navgroupList:
                    navgroup = navgroup.split('}', 1)[1]
                    navgroup = navgroup.split('{: .navgroup-end', 1)[0]
                    self.log.debug('navgroup: ' + str(str(navgroup).encode('utf-8', errors='ignore')))
                    topicGroup = False
                    if '{: .topicgroup' in navgroup:

                        if '\n\n' in navgroup:
                            listDividedByTopicGroups = navgroup.split('\n\n')
                        else:
                            listDividedByTopicGroups = [navgroup]

                        self.log.debug('listDividedByTopicGroups: ')
                        for group in listDividedByTopicGroups:
                            self.log.debug(str(group.encode('utf-8', errors='ignore')))
                        # listDividedByTopicGroups = list(dict.fromkeys(listDividedByTopicGroups))
                        for listDividedByTopicGroup in listDividedByTopicGroups:
                            # if '\t' in listDividedByTopicGroup:
                            # listDividedByTopicGroup = listDividedByTopicGroup.replace('\t', '    ')
                            if '\n    \n' in listDividedByTopicGroup:
                                try:
                                    goodstuff = listDividedByTopicGroup.split('\n    \n')[1]
                                    if isinstance(goodstuff, list):
                                        self.log.debug('goodstuff is a list 1!')
                                    if goodstuff not in listDividedByTopicGroups:
                                        # self.log.info('Appending 1: ' + goodstuff)
                                        listDividedByTopicGroups.append(goodstuff)
                                except Exception:
                                    goodstuff = listDividedByTopicGroup.split('\n    \n')
                                    self.log.debug(goodstuff)
                                    listDividedByTopicGroups.remove(listDividedByTopicGroup)
                                    for section in goodstuff:
                                        if section not in listDividedByTopicGroups:
                                            listDividedByTopicGroups.append(section)
                                            # self.log.info('Appending 2: ' + section)
                            else:
                                if listDividedByTopicGroup not in listDividedByTopicGroups:
                                    listDividedByTopicGroups.append(listDividedByTopicGroup)
                                    # self.log.info('Appending 3: ' + listDividedByTopicGroup)

                        # self.log.info('\nlistDividedByTopicGroups: ' + str(listDividedByTopicGroups))
                        # listDividedByTopicGroups = list(dict.fromkeys(listDividedByTopicGroups))
                        for listDividedByTopicGroup in listDividedByTopicGroups:
                            # self.log.debug('\n\nlistDividedByTopicGroup 2: ' + str(listDividedByTopicGroup))
                            if '{: .topicgroup' in listDividedByTopicGroup:
                                topicGroup = True
                                if '\t' in listDividedByTopicGroup:
                                    listDividedByTopicGroup = listDividedByTopicGroup.replace('\t', '    ')
                                listDividedSingleTopics = listDividedByTopicGroup.split('\n')
                                # listDividedSingleTopics = list(dict.fromkeys(listDividedSingleTopics))
                                for listDividedSingleTopic in listDividedSingleTopics:
                                    if '' == listDividedSingleTopic:
                                        listDividedSingleTopics.remove(listDividedSingleTopic)
                                    elif '{: .topicgroup}' in str(listDividedSingleTopic):
                                        listDividedSingleTopics.remove(listDividedSingleTopic)

                                self.log.debug('listDividedSingleTopics: ' + str(listDividedSingleTopics))
                                topicGroupTitle = listDividedSingleTopics[0]
                                if (('topicgroup' in topicGroupTitle) or ('.md' in topicGroupTitle)):
                                    topicGroupTitle = listDividedSingleTopics[1]
                                if (('topicgroup' in topicGroupTitle) or ('.md' in topicGroupTitle)):
                                    topicGroupTitle = listDividedSingleTopics[2]
                                topicGroupTitle = topicGroupTitle.replace('    ', '')
                                self.log.debug('H1: ' + str(topicGroupTitle.encode('utf-8', errors='ignore')))
                                g.write('\n\n\n## ' + topicGroupTitle)
                                topicGroupTitleNoSpaces = topicGroupTitle.lower()
                                topicGroupTitleNoSpaces = topicGroupTitleNoSpaces.replace(' ', '_').replace('	', '')
                                topicGroupTitleNoSpaces = topicGroupTitleNoSpaces.replace('	', '').replace('  ', ' ')
                                topicGroupTitleNoSpaces = topicGroupTitleNoSpaces.replace('\t', '')
                                while '{: #sitemap_' + topicGroupTitleNoSpaces + '}' in sitemapAnchorList:
                                    topicGroupTitleNoSpaces = topicGroupTitleNoSpaces + '_'
                                sitemapAnchorList.append('{: #sitemap_' + topicGroupTitleNoSpaces + '}')
                                g.write('\n{: #sitemap_' + topicGroupTitleNoSpaces + '}\n')
                                for tocFilename in listDividedSingleTopics:
                                    if (('[' in tocFilename) or ('.md' in tocFilename)):
                                        loop(tocFilename, topicGroup)
                                    elif 'toc' in tocFilename and not details["builder"] == 'local':
                                        tocLoop(tocFilename, topicGroup)
                                    elif tocFilename.startswith(tuple(indentations)) and not details["builder"] == 'local':
                                        reuseLoop(tocFilename, topicGroup)
                                    else:
                                        self.log.debug('Not handled: ' + str(tocFilename.encode('utf-8', errors='ignore')))

                            else:
                                if not isinstance(listDividedByTopicGroup, list):
                                    listDividedSingleTopics = listDividedByTopicGroup.split('\n')
                                topicGroup = False
                                for tocFilename in listDividedSingleTopics:
                                    if '\t' in tocFilename:
                                        tocFilename = tocFilename.replace('\t', '    ')
                                    if ('toc' in tocFilename) and (not details["builder"] == 'local'):
                                        tocLoop(tocFilename, topicGroup)
                                    elif tocFilename.startswith(tuple(indentations)) and not details["builder"] == 'local':
                                        # self.log.info('reuseloop for: ' + tocFilename)
                                        reuseLoop(tocFilename, topicGroup)
                                    else:
                                        loop(tocFilename, topicGroup)

                    else:
                        navGroupSplit = navgroup.split('\n')
                        topicGroup = False
                        for tocFilename in navGroupSplit:
                            if 'toc' in tocFilename and not details["builder"] == 'local':
                                tocLoop(tocFilename, topicGroup)
                            elif tocFilename.startswith(tuple(indentations)) and not details["builder"] == 'local':
                                reuseLoop(tocFilename, topicGroup)
                            else:
                                loop(tocFilename, topicGroup)
        self.log.info('Success!')

    if os.path.isdir(workingDir + '/sitemap-temp/'):
        shutil.rmtree(workingDir + '/sitemap-temp/')
        self.log.debug('Removing: ' + '/sitemap-temp/')
