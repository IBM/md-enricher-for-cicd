#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def writeResult(self,  details, file_name, folderAndFile, folderPath, location_github_branch_push, topicContents):

    # Write the revised contents with all of the tags removed and everything to a file

    import os  # for running OS commands like changing directories or listing files in directory

    # If the file doesn't have anything in it, don't write it or remove existing file unless it's a hidden file
    if ((topicContents == '') or (topicContents == '\n') or (topicContents == '\n\n')) and (not file_name.startswith('.')):
        if os.path.isfile(self.location_dir + folderPath + file_name):
            self.log.debug('- No content to write to file in ' + self.location_name + '. Removing.')
            try:
                os.remove(self.location_dir + folderPath + file_name)
            except Exception as e:
                self.log.error(e)
        else:
            self.log.debug('- No content to write to file in ' + self.location_name + '.')

    # Otherwise, write it
    else:
        if (folderAndFile in self.all_files_dict):
            # Open the file for writing
            with open(self.location_dir + folderPath + file_name, 'w+', encoding="utf8", errors="ignore") as fileName_write:
                fileName_write.write(topicContents)
                self.log.debug('Wrote: ' + self.location_dir + folderPath + file_name)
        # Double-check that nothing is getting written that shouldn't
        else:
            if os.path.isfile(self.location_dir + folderAndFile):
                os.remove(self.location_dir + folderAndFile)
                self.log.debug('Deleted: ' + self.location_dir + folderAndFile)
            if os.path.isfile(self.location_dir + folderPath + file_name):
                os.remove(self.location_dir + folderPath + file_name)
                self.log.debug('Deleted: ' + self.location_dir + folderPath + file_name)
