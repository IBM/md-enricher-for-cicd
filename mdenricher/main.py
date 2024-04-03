#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

""" Markdown enricher. """

import os
import queue
import shutil
import subprocess
import sys
import threading
from subprocess import PIPE, STDOUT

from mdenricher.cleanupEachFile.cleanupEachFile import cleanupEachFile
# from mdenricher.cleanupEachFile.dates import dates
from mdenricher.errorHandling.errorHandling import addToWarnings
from mdenricher.errorHandling.errorHandling import addToErrors
from mdenricher.errorHandling.flagCheck import flagCheck
from mdenricher.errorHandling.jsonCheck import jsonCheck
from mdenricher.errorHandling.loggingConfig import loggingConfig
from mdenricher.errorHandling.phraseCheck import phraseCheck
from mdenricher.errorHandling.snippetCheck import snippetCheck
from mdenricher.errorHandling.validateArguments import validateArguments
from mdenricher.errorHandling.parseSubprocessOutput import parseSubprocessOutput
from mdenricher.repos.clone import clone
from mdenricher.repos.previousCommitInfo import previousCommitInfo
from mdenricher.repos.pushUpdatedFiles import pushUpdatedFiles
from mdenricher.setup.config import config
from mdenricher.setup.exitBuild import exitBuild
from mdenricher.setup.locations import locations
from mdenricher.sitemap.sitemapOLD import sitemapOLD
from mdenricher.sitemap.sitemapYML import sitemapYML
from mdenricher.sitemap.sitemapSUMMARY import sitemapSUMMARY
from mdenricher.sourceFileList.allFilesGet import allFilesGet
from mdenricher.sourceFileList.locationContentList import locationContentList
from mdenricher.sourceFileList.sourceFilesForThisBranch import sourceFilesForThisBranch
from mdenricher.sourceFileList.runThisBuild import runThisBuild
from mdenricher.tags.tagListCompile import tagListCompile


def main(
         builder,
         ibm_cloud_docs,
         ibm_cloud_docs_keyref_check,
         ibm_cloud_docs_sitemap_depth,
         ibm_cloud_docs_sitemap_rebuild_always,
         ibm_docs,
         locations_file,
         output_dir,
         rebuild_all_files,
         rebuild_files,
         slack_bot_token,
         slack_channel,
         slack_post_success,
         slack_show_author,
         slack_user_mapping,
         slack_webhook,
         source_dir,
         test_only,
         validation):

    """ Markdown enricher. """

    def change_dir(details, source_dir):

        """ Change directory. """

        try:
            os.chdir(source_dir)
        except FileNotFoundError:
            addToErrors('The directory specified for the source_dir could not be found. ' +
                        'Verify the path specified: --source_dir=' + source_dir, 'start.py-command', '', details,
                        log, 'pre-build', '', '')
            exitBuild(details, log)

    def process_data(q):
        while not exitFlag:
            queueLock.acquire()
            if not workQueue.empty():
                q.get()
            queueLock.release()

    ###############################
    # Loop details for running over each repo and branch
    ###############################

    class locationByThread(threading.Thread):

        def __init__(self,
                     threadID,
                     all_tags,
                     location,
                     location_name,
                     source_files_original_list,
                     q):

            threading.Thread.__init__(self)
            self.threadID = threadID
            self.all_tags = all_tags
            self.location = location
            self.location_name = location_name
            self.source_files_original_list = source_files_original_list
            self.q = q

        def run(self):

            process_data(self.q)

            log = loggingConfig(details, details["tool_name"] + '_' + self.location_name)
            self.log = log

            self.log.info('Started: ' + self.location_name)

            subprocessOutput = subprocess.Popen('echo Test', shell=True, stdout=PIPE, stderr=STDOUT)
            exitCode = parseSubprocessOutput(subprocessOutput, log)

            self.log.debug('\n\n\n')
            self.log.debug('---------------------------------------------------------')
            self.log.debug('%s', self.location_name.upper())
            self.log.debug('---------------------------------------------------------\n\n')

            (location_build, location_comments, location_commit_summary_style,
             location_contents, location_contents_files, location_contents_folders,
             location_downstream_build_url, location_github_branch,
             location_github_branch_pr, location_github_url, location_internal_framework, location_output_action,
             remove_all_other_files_folders) = locations(details, self.location, log)

            self.location_build = location_build
            self.location_comments = location_comments
            self.location_commit_summary_style = location_commit_summary_style
            self.location_contents = location_contents
            self.location_contents_files = location_contents_files
            self.location_contents_folders = location_contents_folders
            self.location_dir = details["output_dir"] + '/' + self.location_name
            self.location_downstream_build_url = location_downstream_build_url
            self.location_github_branch = location_github_branch
            self.location_github_branch_pr = location_github_branch_pr
            self.location_internal_framework = location_internal_framework
            if str(location_github_url).endswith('/'):
                location_github_url = location_github_url[:-1]
            self.location_github_url = location_github_url
            # location_name set in init
            self.location_output_action = location_output_action
            self.remove_all_other_files_folders = remove_all_other_files_folders

            conref_files_list = []  # type: ignore
            filesForOtherLocations = []  # type: ignore

            if self.location_build == 'off':
                self.log.info('Skipping: ' + self.location_name + '.')
                self.log.debug('location_build is set to off in the locations file.')
                self.conref_files_list = conref_files_list
                self.filesForOtherLocations = filesForOtherLocations
            else:

                (location_contents_files_keep, location_contents_files_remove,
                 location_contents_folders, location_contents_folders_keep, location_contents_folders_remove,
                 location_contents_folders_remove_and_files) = locationContentList(self)

                self.location_contents_files_keep = location_contents_files_keep
                self.location_contents_files_remove = location_contents_files_remove
                self.location_contents_folders_keep = location_contents_folders_keep
                self.location_contents_folders_remove = location_contents_folders_remove
                self.location_contents_folders_remove_and_files = location_contents_folders_remove_and_files

                # Get a list of all of the files that the scripts work with
                all_files_get_result = allFilesGet(details, self.location_contents_files, self.location_contents_files_keep,
                                                   self.location_contents_files_remove, self.location_contents_folders,
                                                   self.location_contents_folders_keep, self.location_contents_folders_remove,
                                                   self.location_contents_folders_remove_and_files, self.log,
                                                   self.remove_all_other_files_folders, self.source_files_original_list)
                all_files_dict = all_files_get_result[0]
                conref_files_list = all_files_get_result[1]
                image_files_list = all_files_get_result[2]
                sitemap_file = all_files_get_result[3]
                filesForOtherLocations = all_files_get_result[4]
                allSourceFiles.update(all_files_dict)

                self.all_files_dict = all_files_dict
                self.conref_files_list = conref_files_list
                self.filesForOtherLocations = filesForOtherLocations
                self.image_files_list = image_files_list
                self.sitemap_file = sitemap_file

                # Use the name of the properties file to identify this location in the build

                if self.location_github_url is None:
                    location_github_domain = None
                    location_github_org = None
                    location_github_repo = None
                    location_github_api_prefix = None
                    location_github_api_repos = None
                    location_github_branch_pr = None
                # If not a local build, set these values to something based on the UPSTREAM_URL
                else:
                    location_github_list = self.location_github_url.split('/')
                    location_github_domain = location_github_list[2]
                    location_github_org = location_github_list[3]
                    location_github_repo = location_github_list[4]
                    if 'github.com' in self.location_github_url:
                        location_github_api_prefix = 'https://api.' + location_github_domain
                        location_github_api_repos = location_github_api_prefix + '/repos/' + location_github_org + '/' + location_github_repo
                    else:
                        location_github_api_prefix = 'https://' + location_github_domain + '/api/v3'
                        location_github_api_repos = location_github_api_prefix + '/repos/' + location_github_org + '/' + location_github_repo

                self.location_github_api_prefix = location_github_api_prefix
                self.location_github_api_repos = location_github_api_repos
                self.location_github_domain = location_github_domain
                self.location_github_org = location_github_org
                self.location_github_repo = location_github_repo

                if self.source_files_original_list == {}:
                    source_files_location_list = self.all_files_dict
                else:
                    # Rebuild the list with the status, patch, and previous name from git, but use the downstream folder and file name from the all files list
                    source_files_location_list = {}
                    # self.log.debug('source_files_original_list:')
                    for source_files_original in self.source_files_original_list:
                        try:
                            folderPath = self.all_files_dict[source_files_original]["folderPath"]
                            file_name = self.all_files_dict[source_files_original]["file_name"]
                        except Exception:
                            try:
                                folderPath = self.source_files_original_list[source_files_original]["folderPath"]
                                file_name = self.source_files_original_list[source_files_original]["file_name"]
                            except Exception as e:
                                self.log.debug('Not handling: ' + source_files_original)
                                self.log.debug(e)
                                try:
                                    self.log.debug(folderPath)
                                except Exception:
                                    self.log.debug('No folderPath.')
                                try:
                                    self.log.debug(file_name)
                                except Exception:
                                    self.log.debug('No file_name.')
                        try:
                            fileStatus = self.source_files_original_list[source_files_original]["fileStatus"]
                            filePatch = self.source_files_original_list[source_files_original]["filePatch"]
                            fileNamePrevious = self.source_files_original_list[source_files_original]["fileNamePrevious"]
                        except Exception as e:
                            # We don't want things like .travis.yml added to the location list
                            self.log.debug('Not handling: ' + source_files_original)
                            self.log.debug(e)
                            try:
                                self.log.debug(fileStatus)
                            except Exception:
                                self.log.debug('No fileStatus.')
                            try:
                                self.log.debug(filePatch)
                            except Exception:
                                self.log.debug('No filePatch.')
                            try:
                                self.log.debug(fileNamePrevious)
                            except Exception:
                                self.log.debug('No fileNamePrevious.')
                        else:
                            try:
                                source_files_location_list[source_files_original] = {}
                                source_files_location_list[source_files_original]['folderAndFile'] = source_files_original
                                source_files_location_list[source_files_original]['file_name'] = file_name
                                source_files_location_list[source_files_original]['folderPath'] = folderPath
                                source_files_location_list[source_files_original]['fileStatus'] = fileStatus
                                source_files_location_list[source_files_original]['filePatch'] = filePatch
                                source_files_location_list[source_files_original]['fileNamePrevious'] = fileNamePrevious
                            except Exception as e:
                                self.log.debug('Could not add details to location list: ' + source_files_original)
                                self.log.debug(e)

                self.source_files_location_list = source_files_location_list

                self.log.debug('Location details:')
                self.log.debug('location_dir: %s', str(self.location_dir))
                self.log.debug('location_contents: ' + str(self.location_contents))
                self.log.debug('location_github_api_prefix: %s', str(self.location_github_api_prefix))
                self.log.debug('location_github_api_repos: %s', str(self.location_github_api_repos))
                self.log.debug('location_github_branch: %s', str(self.location_github_branch))
                self.log.debug('location_github_branch_pr: %s', str(self.location_github_branch_pr))
                self.log.debug('location_github_domain: %s', str(self.location_github_domain))
                self.log.debug('location_github_org: %s', str(self.location_github_org))
                self.log.debug('location_github_repo: %s', str(self.location_github_repo))
                self.log.debug('location_github_url: %s', str(self.location_github_url))
                self.log.debug('location_name: %s', str(self.location_name))
                self.log.debug('location_output_action: %s', str(self.location_output_action))
                self.log.debug('sitemap_file: %s', str(self.sitemap_file))
                self.log.debug('remove_all_other_files_folders: ' + str(self.remove_all_other_files_folders))

                self.log.debug('File list for this location:')
                for source_file in self.source_files_location_list:
                    self.log.debug(self.source_files_location_list[source_file]['folderAndFile'])

                # See if this is a location that should be iterated over
                # or skipped based on which files kicked off the build
                runThisLocation = runThisBuild(self, details)

                if runThisLocation is False:
                    self.log.info('Not running on %s.', self.location_name)
                else:

                    try:
                        self.location_github_branch_push = clone(self, details)
                    except Exception as e:
                        self.log.debug(e)

                    # For local builds, copy over everything to the working directory
                    if not os.path.isdir(self.location_dir):
                        os.mkdir(self.location_dir)

                    # If there is a cloned repo, do stuff with it.
                    # There might not be for the CLI and SUB_REPO.
                    if os.path.isdir(self.location_dir):

                        os.chdir(self.location_dir)

                        # Create a list of tags with show/hide values for this branch
                        tags_hide, tags_show = tagListCompile(self, details)

                        self.tags_hide = tags_hide
                        self.tags_show = tags_show

                        # Revise the source list based on the branch.
                        # For example, the original commit might only contain a conref file.
                        # We need to get a list of all of the files that use that conref to work with.
                        self.source_files = sourceFilesForThisBranch(self, details)

                        if self.source_files == {}:
                            self.log.debug('No changes to process for this location.')
                        else:
                            self.log.debug('\n')
                            self.log.debug('Handling files for ' + self.location_name + '.')

                            if ((self.sitemap_file in self.source_files) and
                                    (not details["ibm_cloud_docs_sitemap_depth"] == 'off')):
                                with open(self.location_dir + '/sitemap.md', 'r', encoding="utf8", errors="ignore") as fileName_read:
                                    topicContentsDownstream = fileName_read.read()
                                self.source_files[self.sitemap_file]['downstream_sitemap_contents'] = topicContentsDownstream

                            # Actually do the conref and tag replacements in the new source file list
                            cleanupEachFile(self, details, False)

                            # After all of the content files are updated, update the images
                            cleanupEachFile(self, details, True)

                            # If images are not all stored in the /images directory, issue a warning
                            if ((not os.path.isdir(details["source_dir"] + '/images')) and
                                    (not self.image_files_list == []) and details["ibm_cloud_docs"] is True):
                                addToWarnings('Images were found in the repo, but they were not stored in a single ' +
                                              '/images/ directory in the root of the repo.', '/images/', '', details, self.log,
                                              self.location_name, '', '')

                            # Check for these directories and delete them to avoid accidental pushes
                            directories_to_delete = ['/' + details["reuse_snippets_folder"], '/source']
                            for folder in self.location_contents_folders_remove:
                                directories_to_delete.append(folder)

                            # Should these be within the location_dir or the output_dir
                            for directory_to_delete in directories_to_delete:
                                if not directory_to_delete.startswith('/') and not directory_to_delete.startswith('includes'):
                                    directory_to_delete = '/' + directory_to_delete
                                if os.path.isdir(self.location_dir + directory_to_delete):
                                    self.log.debug('Deleted: ' + self.location_dir + directory_to_delete)
                                    shutil.rmtree(self.location_dir + directory_to_delete)

                            # Don't remove the .travis.yml in case there's another one not created by us in the repo
                            if os.path.isfile(self.location_dir + details["featureFlagFile"]):
                                os.remove(self.location_dir + details["featureFlagFile"])
                                self.log.debug('Removing: ' + self.location_dir + details["featureFlagFile"])

                            locations_file_name = details["locations_file"].rsplit('/', 1)[1]
                            if os.path.isfile(self.location_dir + '/' + locations_file_name):
                                os.remove(self.location_dir + '/' + locations_file_name)
                                self.log.debug('Removing: ' + self.location_dir + '/' + locations_file_name)

                            if os.path.isdir(self.location_dir + '/doctopus-common'):
                                shutil.rmtree(self.location_dir + '/doctopus-common')
                                self.log.debug('Removing: ' + self.location_dir + '/doctopus-common')

                            # If there is a sitemap.md, populate it with links
                            # This needs to happen after comments are handled
                            if ((self.sitemap_file in self.source_files) and
                                    (not details["ibm_cloud_docs_sitemap_depth"] == 'off')):
                                if 'toc.yaml' in str(self.all_files_dict) and details["ibm_cloud_docs"] is True:
                                    sitemapYML(self, details)

                                elif 'SUMMARY.md' in str(self.all_files_dict) and details["ibm_docs"] is True:
                                    sitemapSUMMARY(self, details)

                                elif (('toc' in str(self.all_files_dict)) and ('toc.yaml' not in str(self.all_files_dict))):
                                    sitemapOLD(self, details)

                                else:
                                    addToWarnings('A toc.yaml file does not exist, so the sitemap could not be built.',
                                                  'toc.yaml', '', details, log, 'pre-build', '', '')

                            # Don't actually push the updated files if any of these ifs are met
                            # self.log.info(json.dumps(self.source_files, indent=2))
                            if (((details['builder'] == 'local') and (self.location_output_action == 'none')) or
                                    (self.location_output_action == 'none') or
                                    (details["test_only"] is True)):
                                if os.path.isdir(self.location_dir + '/.git'):
                                    try:
                                        subprocessOutput = subprocess.Popen('git add -n --all', shell=True, stdout=PIPE, stderr=STDOUT)
                                        exitCode = parseSubprocessOutput(subprocessOutput, self.log)
                                    except Exception:
                                        self.log.debug('Not printing changed files list.')
                                    else:
                                        if exitCode > 0:
                                            self.log.debug('Not printing changed files list.')
                                        else:
                                            status_bytes = subprocess.check_output('git status --short', shell=True)
                                            status = status_bytes.decode("utf-8")
                                            self.log.debug('\n')
                                            if ('nothing to commit' in status.lower()) or (status == '\n') or (status == ''):
                                                self.log.debug('No changes to commit.')
                                            else:
                                                self.log.debug('These files are changed, but are not being committed at this time:')
                                                self.log.debug(status)

                            else:
                                # Push the updated files to the downstream branches
                                pushUpdatedFiles(self, details, pushQueue)

            self.log.info('Finished: ' + self.location_name)
            return

    # Start

    try:

        exitFlag = 0
        pushQueue = []

        details = {}
        details.update({"ibm_cloud_docs": ibm_cloud_docs})
        details.update({"ibm_cloud_docs_sitemap_depth": ibm_cloud_docs_sitemap_depth})
        details.update({"ibm_cloud_docs_sitemap_rebuild_always": ibm_cloud_docs_sitemap_rebuild_always})
        details.update({"ibm_docs": ibm_docs})
        details.update({"rebuild_all_files": rebuild_all_files})
        details.update({"slack_bot_token": slack_bot_token})
        details.update({"slack_channel": slack_channel})
        details.update({"slack_post_success": slack_post_success})
        details.update({"slack_show_author": slack_show_author})
        details.update({"slack_user_mapping": slack_user_mapping})
        details.update({"slack_webhook": slack_webhook})
        details.update({"tool_name": 'md-enricher-for-cicd'})
        details.update({"validation": validation})

        if output_dir is None:
            output_dir = source_dir + '/output'
        details.update({"output_dir": output_dir})

        if locations_file is None:
            if os.path.isfile(source_dir + '/locations.json'):
                locations_file = source_dir + '/locations.json'
        details.update({"locations_file": locations_file})

        # Need to remove the old output directory and create a new one before the log file starts
        if os.path.isdir(details["output_dir"]):
            shutil.rmtree(details["output_dir"])
        os.makedirs(details["output_dir"])

        # Remove old check files
        phraseUsageFile = details["output_dir"] + '/phraseUsageFile.txt'
        details.update({"phraseUsageFile": phraseUsageFile})
        if os.path.isfile(phraseUsageFile):
            os.remove(phraseUsageFile)

        snippetUsageFile = details["output_dir"] + '/snippetUsageFile.txt'
        details.update({"snippetUsageFile": snippetUsageFile})
        if os.path.isfile(snippetUsageFile):
            os.remove(snippetUsageFile)

        # Import the logging config
        log = loggingConfig(details, details["tool_name"])

        error_file = details["output_dir"] + '/errors.txt'
        warning_file = details["output_dir"] + '/warnings.txt'

        details.update({"error_file": error_file})
        details.update({"warning_file": warning_file})

        log.info("\n\n\n-------------------------------------------------------------------------\n\n\n" +
                 "MARKDOWN ENRICHER FOR CONTINUOUS INTEGRATION AND CONTINUOUS DELIVERY" +
                 "\n\n\n-------------------------------------------------------------------------\n\n\n")

        # These imports need to be after the pip install
        from datetime import datetime
        import json
        from pytz import timezone
        import time
        import urllib.parse
        import yaml

        log.info("-------------------------------------------------------------")
        log.info("COLLECTING BUILDER INFORMATION")
        log.info("-------------------------------------------------------------")
        log.info("")

        # To identify a length of time that it took to run, establish a start time
        time_start = time.time()
        details.update({"time_start": time_start})

        time_zone = timezone('US/Eastern')
        details.update({"time_zone": time_zone})
        log.debug('Build began: %s', str(datetime.now(details["time_zone"])))

        # Github credentials
        token = str(os.environ.get('GH_TOKEN'))
        username = os.environ.get('GH_USERNAME')
        details.update({"token": token})
        details.update({"username": username})

        travis_build_dir = str(os.environ.get('TRAVIS_BUILD_DIR'))
        workspace = str(os.environ.get('WORKSPACE'))
        if travis_build_dir != 'None':

            # Getting the SHAs here, but had problems with the environment variables before.
            # Will get them for real in previousCommitInfo.
            # For here, they're just gotten for the purposes of including with failed build slack posts.
            workspace = travis_build_dir
            build_id = os.environ.get('TRAVIS_BUILD_ID')
            build_number = os.environ.get('TRAVIS_BUILD_NUMBER')
            if builder is None:
                builder = 'travis'

        # Anticipating that other builders could use the workspace variable
        elif 'jenkins' in workspace:
            build_id = os.environ.get('build_id')
            build_number = os.environ.get('build_number')
            if builder is None:
                builder = 'jenkins'

        # Toolchain
        elif workspace.startswith('/workspace/'):
            build_id = os.environ.get('BUILD_ID')
            build_number = os.environ.get('BUILD_NUMBER')
            if builder is None:
                builder = 'toolchain'
        else:
            if builder is None:
                builder = 'local'
            build_id = None
            build_number = 'Local'
            workspace = source_dir

        details.update({"builder": builder})
        details.update({"build_id": build_id})
        details.update({"build_number": build_number})
        details.update({"workspace": workspace})

        # Create a list out of the rebuild_files values and make sure each entry starts with a slash
        if rebuild_files is None:
            rebuild_files_list: list[str] = []  # type: ignore[misc]
        elif ',' in rebuild_files:
            rebuild_files_list = []
            rebuild_files_list_original = rebuild_files.split(',')
            for rebuild_files_list_item in rebuild_files_list_original:
                if not rebuild_files_list_item.startswith('/'):
                    rebuild_files_list_item = '/' + rebuild_files_list_item
                rebuild_files_list.append(rebuild_files_list_item)
        else:
            if not rebuild_files.startswith('/'):
                rebuild_files = '/' + rebuild_files
            rebuild_files_list = [rebuild_files]
        details.update({"rebuild_files_list": rebuild_files_list})

        if not os.path.exists(source_dir):
            os.makedirs(source_dir)
        change_dir(details, workspace)

        details.update({"source_dir": source_dir})

        if os.path.isdir(source_dir + '/.git'):
            try:
                source_github_url_bytes = subprocess.check_output(["git", "config", "--get", "remote.origin.url"])
                source_github_url = source_github_url_bytes.decode("utf-8")
                log.debug('Source directory is a Git clone.')
            except Exception:
                addToErrors('The directory specified for the source_dir is not a clone of a Git repository. ' +
                            'This directory must be a Git clone.', 'start.py-command', '', details, log, 'pre-build', '', '')
                # Too many variables haven't been established yet to use the errorHandling exit build.
                exitBuild(details, log)
        else:
            source_github_url = None
            log.debug('Source directory is not a Git clone.')

        try:
            if details["builder"] == 'travis':
                current_github_branch = str(os.environ.get('TRAVIS_BRANCH'))
                current_github_branch = urllib.parse.quote(current_github_branch, encoding="utf-8")
            elif details["builder"] == 'local':
                current_github_branch = 'local'
            else:
                current_github_branch_bytes = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
                current_github_branch = current_github_branch_bytes.decode("utf-8")
                current_github_branch = current_github_branch.replace('\n', '')
            # Jenkins pipeline
            # if 'HEAD' == current_github_branch:
            # current_github_branch_bytes = subprocess.check_output(["git", "branch", "--show-current"])
            # current_github_branch = current_github_branch_bytes.decode("utf-8")
            # current_github_branch = current_github_branch.replace('\n', '')
            if 'origin/' in current_github_branch:
                current_github_branch = current_github_branch.split('origin/')[1]
            details.update({"current_github_branch": current_github_branch})
            # log.debug('current_github_branch: ' + current_github_branch)
        except Exception as e:
            addToErrors('The current branch name could not be found.', 'start.py-command', '', details, log, 'pre-build', '', '')
            log.debug(str(e))
        validateArguments(details, log)

        # Get the contents of the feature flags file
        if os.path.isfile((details["source_dir"]) + '/feature-flags.json'):
            details.update({"featureFlagFile": '/feature-flags.json'})
            with open(details["source_dir"] + details["featureFlagFile"], 'r', encoding="utf8", errors="ignore") as featureFlagJson:
                try:
                    featureFlags = json.load(featureFlagJson)
                except Exception as e:
                    addToErrors('Information might not be formatted properly in feature flags file.' + str(e),
                                details["featureFlagFile"], '', details, log, 'pre-build', '', '')
                else:
                    details.update({"featureFlags": featureFlags})
        else:
            details.update({"featureFlagFile": 'None'})
            details.update({"featureFlags": 'None'})

        # This has to come before the allfilesget
        log.debug('Getting values from: %s', details["locations_file"])

        with open(details["locations_file"], 'r', encoding="utf8", errors="ignore") as locations_file_open:
            try:
                locations_wholeFile = json.load(locations_file_open)
                locations_json = locations_wholeFile["markdown-enricher"]
            except Exception as e:
                addToErrors('The locations file could not be parsed. ' + str(e), 'start.py-command', '', details, log, 'pre-build', '', '')
                # Too many variables haven't been established yet to use the errorHandling exit build.
                exitBuild(details, log)

            try:
                locations_json_list = locations_json["locations"]
            except Exception as e:
                addToErrors('The locations file could not be parsed. ' + str(e), 'start.py-command', '', details, log, 'pre-build', '', '')
                # Too many variables haven't been established yet to use the errorHandling exit build.
                exitBuild(details, log)

            try:
                locations_config = locations_json["config"]
            except Exception:
                locations_config = {}
                log.debug('No config section was included in the locations file. The default values will be used.')
                # Need to know the branch at the very least
            finally:
                (details) = config(log, details, locations_config)

        # If the branch is not the source branch, don't push anything anywhere
        if ((not details["source_github_branch"] == details["current_github_branch"]) and
                (not details["log_branch"] == details["current_github_branch"]) and
                (not details["builder"] == 'local')):
            log.info('Running as a test without pushing the final results downstream because the %s ' +
                     'branch is not the %s branch.', details["current_github_branch"], details["source_github_branch"])
            test_only = True

        details.update({"test_only": test_only})

        # If the branch is the log branch, just exit
        if details["log_branch"] == details["current_github_branch"]:
            log.info('Exiting. Not running on the %s.', details["current_github_branch"])
            sys.exit(0)

        # Delete the .git directory from the tool clone so those files get detected by the push later
        # This has to go after the remote origin URL get
        # if not details["builder"] == 'local':
            # if os.path.isdir(workspace + '/.git'):
            # log.debug('Deleted: %s/.git', workspace)
            # shutil.rmtree(workspace + '/.git')

        # EX: https://DOMAIN/ORG/REPO.git
        if str(source_github_url).startswith('https'):
            source_github_url = str(source_github_url).split('.git', maxsplit=1)[0]
            source_github_list = source_github_url.split('/')
            source_github_domain = source_github_list[2]
            source_github_org = source_github_list[3]
            source_github_repo = source_github_list[4]
            if '@' in source_github_domain:
                source_github_domain = source_github_domain.split('@')[1]
                source_github_url = 'https://' + source_github_domain + '/' + source_github_org + '/' + source_github_repo
        # EX: git@DOMAIN:ORG/REPO.git
        elif str(source_github_url).startswith('git@'):
            source_github_domain, source_github_url = str(source_github_url).split(':')
            source_github_domain = source_github_domain.split('@')[1]
            source_github_url = source_github_url.split('.git')[0]
            source_github_org, source_github_repo = source_github_url.split('/')
            source_github_url = 'https://' + source_github_domain + '/' + source_github_url
        # For local builds, set these remote values to None
        else:
            source_github_url = 'None'
            source_github_domain = None
            source_github_org = None
            source_github_repo = None

        if '\n' in str(source_github_repo):
            source_github_repo = str(source_github_repo).replace('\n', '')

        details.update({"source_github_domain": source_github_domain})
        details.update({"source_github_org": source_github_org})
        details.update({"source_github_repo": source_github_repo})
        details.update({"source_github_url": source_github_url})

        if details["builder"] == 'travis':
            build_url = str(os.environ.get('TRAVIS_BUILD_WEB_URL'))
        elif details["builder"] == 'jenkins':
            build_url = str(os.environ.get('build_url'))
        else:
            build_url = 'None'

        details.update({"build_url": build_url})

        # Set the GITHUB API variables
        if (('github.com' in details["source_github_url"]) and (not details["builder"] == 'local')):
            source_github_api_prefix = 'https://api.' + details["source_github_domain"]
            source_github_api_repos = source_github_api_prefix + '/repos/' + details["source_github_org"] + '/' + details["source_github_repo"]
        elif (('github.com' not in details["source_github_url"]) and ('None' not in str(details["source_github_url"])) and (not details["builder"] == 'local')):
            source_github_api_prefix = 'https://' + details["source_github_domain"] + '/api/v3'
            source_github_api_repos = source_github_api_prefix + '/repos/' + details["source_github_org"] + '/' + details["source_github_repo"]
        else:
            source_github_api_prefix = None
            source_github_api_repos = None

        details.update({"source_github_api_repos": source_github_api_repos})
        details.update({"source_github_api_prefix": source_github_api_prefix})

        # Combine image lists
        img_filetypes = details["img_output_filetypes"] + details["img_src_filetypes"]
        details.update({"img_filetypes": img_filetypes})

        # Get the IBM Cloud product name file to verify the product name conrefs that are used in each file
        ibm_cloud_docs_product_names = []
        if ibm_cloud_docs_keyref_check is True:
            if os.path.isfile(details['workspace'] + '/cloudoekeyrefs.yml'):
                log.debug('IBM Cloud cloudoekeyrefs.yml exists. Product name checks enabled.')
                with open(details['workspace'] + '/cloudoekeyrefs.yml', "r", encoding="utf8", errors="ignore") as stream:
                    try:
                        ibm_cloud_docs_product_namesAll = yaml.safe_load(stream)
                        ibm_cloud_docs_product_names = ibm_cloud_docs_product_namesAll['keyword']
                    except yaml.YAMLError as exc:
                        log.warning(exc)

            if not os.path.isfile(details['workspace'] + '/cloudoekeyrefs.yml') and not os.path.isfile(details["source_dir"] + '/keyref.yaml'):
                ibm_cloud_docs_keyref_check = False

        details.update({"ibm_cloud_docs_product_names": ibm_cloud_docs_product_names})
        details.update({"ibm_cloud_docs_keyref_check": ibm_cloud_docs_keyref_check})

        # Make a list of enricher required JSON files for pre-build check
        enricher_json_files = ['/' + details["reuse_snippets_folder"] + '/' + details["reuse_phrases_file"],
                               details["featureFlagFile"], details["slack_user_mapping"]]
        jsonCheck(details, log, 'False', enricher_json_files, 'None')

        all_tags = []
        all_locations: list[str] = []  # type: ignore[misc]
        allSourceFiles = {}  # type: ignore[var-annotated]

        # Collect tags, location folders, but also verify that the locations are unique
        log.debug('Verifying that each location is unique.')

        for location in locations_json_list:
            location_name = location["location"]

            all_tags.append(location_name)

            # Verify that the combination of the URL, branch, and PR branch are unique to avoid
            # accidentally overwriting content by pushing to the same location multiple times
            try:
                location_github_url = location["location_github_url"]
            except Exception:
                log.debug('%s is a local location.', location_name)
            else:

                def checkLocation(all_locations, location_info):
                    # Catch duplicates in the locations file
                    if location_info in all_locations:
                        addToErrors('The ' + location_name + ' might be a duplicate of another. ' +
                                    'Check that the combination of the URL, Branch and PR branch are unique for ' +
                                    location_info + '.', 'locations.json', '',
                                    details, log, 'pre-build', location_name, locations_wholeFile)
                        exitBuild(details, log)
                    # Check if the current branch is listed in one of the locations and don't run on that
                    elif (location_info ==
                          details["source_github_url"] + ',' + details["current_github_branch"]):
                        addToErrors('The downstream location cannot be the same as the upstream location where this build is initiated: ' +
                                    location_info +
                                    ' branch. Not running on this content. Exiting the build.',
                                    'locations.json', '', details, log, 'pre-build', '', '')
                        exitBuild(details, log)
                    else:
                        all_locations.append(location_info)
                        log.debug('Verified location is unique: ' + location_info)
                    return (all_locations)

                try:
                    location_info = location_github_url + ',' + location["location_github_branch_pr"]
                except Exception:
                    pass
                else:
                    all_locations = checkLocation(all_locations, location_info)

                try:
                    location_info = location_github_url + ',' + location["location_github_branch"]
                except Exception:
                    addToErrors('No branch is specified in the locations file for ' + location_name + '.',
                                'locations.json', '', details, log, 'pre-build', location_name, locations_wholeFile)
                    exitBuild(details, log)
                else:
                    all_locations = checkLocation(all_locations, location_info)

        join_comma = ', '
        log.info('Locations can be used as tags: %s', join_comma.join(all_tags))
        details.update({"location_tags": all_tags})

        if (source_github_url + ',' + current_github_branch) in all_locations:
            addToWarnings('The ' + current_github_branch + ' branch in ' + source_github_url +
                          ' cannot be both the upstream source and in the list of downstream output locations. ' +
                          'Exiting the build.',
                          'locations.json', '', details, log, 'pre-build', '', '')
            exitBuild(details, log)

        # Get info from the commit that triggered this build, including a list of all files
        if (details["builder"] == 'local') or (details["source_github_branch"] == 'None'):
            try:
                current_commit_author = os.getlogin()
            except Exception:
                current_commit_author = 'None'
            current_commit_email = 'None'
            try:
                current_commit_id_bytes = subprocess.check_output(["git", "log", "-1", "--format=%H"])
                current_commit_id = current_commit_id_bytes.decode("utf-8")
                if '\n' in current_commit_id:
                    current_commit_id = current_commit_id.split('\n', 1)[0]
            except Exception:
                current_commit_id = 'None'
            current_commit_summary = 'Local transform'
            previous_commit_id = 'None'
            source_files_original_list = {}
        else:
            # For remote current_github_branch that is not source_github_branch
            previous_commit_result = previousCommitInfo(details, log)

            current_commit_author = previous_commit_result[0]
            current_commit_email = previous_commit_result[1]
            current_commit_id = previous_commit_result[2]
            current_commit_summary = previous_commit_result[3]
            previous_commit_id = previous_commit_result[4]
            source_files_original_list = previous_commit_result[5]

        details.update({"current_commit_author": current_commit_author})
        details.update({"current_commit_email": current_commit_email})
        details.update({"current_commit_id": current_commit_id})
        details.update({"current_commit_summary": current_commit_summary})
        details.update({"previous_commit_id": previous_commit_id})

        log.info('')
        log.info('Build details:')
        for detail in sorted(details):
            if (details["ibm_cloud_docs"] is False) and ('ibm' in detail):
                if 'ibm_cloud_docs_product_names' not in detail:
                    log.debug('%s: %s', detail, str(details[detail]))
            else:
                if (('token' not in detail) and ('webhook' not in detail) and ('username' not in detail) and ('ibm_cloud_docs_product_names' not in detail)):
                    if len(str(details[detail])) > 500:
                        detailsString = str(details[detail])[0:500] + '...'
                    else:
                        detailsString = str(details[detail])
                    log.info('%s: %s', detail, detailsString)
        # log.info(details["username"])

        queueLock = threading.Lock()
        workQueue = queue.Queue(maxsize=2)  # type: ignore[var-annotated]
        threads = []
        threadID = 1

        log.info("\n\n\n")
        log.info("-------------------------------------------------------------")
        log.info("GENERATING CONTENT")
        log.info("-------------------------------------------------------------")
        log.info("")

        # Create new threads
        for location in locations_json_list:

            thread = locationByThread(threadID,
                                      all_tags,
                                      location,
                                      location['location'],
                                      source_files_original_list,
                                      workQueue)

            thread.start()
            threads.append(thread)
            threadID += 1

        # Fill the queue
        for location in locations_json_list:
            log.debug('Started: ' + location['location'])
            workQueue.put(location['location'])
            log.debug('Finished: ' + location['location'])

        # Wait for queue to empty
        while not workQueue.empty():
            pass

        # Notify threads it's time to exit
        exitFlag = 1

        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            filesForOtherLocations = thread.filesForOtherLocations
            conref_files_list = thread.conref_files_list

        if details["validation"] == 'on':
            log.debug('Validating output.')
            if not filesForOtherLocations == []:
                phraseCheck(details, log, allSourceFiles, filesForOtherLocations)
                if not conref_files_list == []:
                    snippetCheck(details, log, allSourceFiles, conref_files_list, filesForOtherLocations)
                flagCheck(details, log, allSourceFiles, filesForOtherLocations)

        exitBuild(details, log)

    except Exception as e:
        print(e)
        sys.exit(1)
