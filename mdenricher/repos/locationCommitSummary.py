#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def locationCommitSummary(self, details):

    # Set the commit style for the location

    if self.location_commit_summary_style == 'Author':
        LOCATION_COMMIT_SUMMARY = details["current_commit_author"]

    elif self.location_commit_summary_style == 'AuthorAndSummary':
        # Workaround for alchemy-containers/documentation
        if (details["current_commit_author"] + ': ') in details["current_commit_summary"]:
            LOCATION_COMMIT_SUMMARY = details["current_commit_summary"]
        else:
            LOCATION_COMMIT_SUMMARY = details["current_commit_author"] + ': ' + details["current_commit_summary"]

    elif self.location_commit_summary_style == 'AuthorAndUpdate':
        LOCATION_COMMIT_SUMMARY = details["current_commit_author"] + ' update'
    elif self.location_commit_summary_style == 'BuildNumber':
        LOCATION_COMMIT_SUMMARY = 'Build ' + details["build_number"]
    elif self.location_commit_summary_style == 'BuildNumberAndSummary':
        LOCATION_COMMIT_SUMMARY = 'Build ' + details["build_number"] + ': ' + details["current_commit_summary"]

    elif self.location_commit_summary_style == 'CommitID':
        LOCATION_COMMIT_SUMMARY = details["current_commit_id"]
    elif self.location_commit_summary_style == 'CommitIDAndSummary':
        LOCATION_COMMIT_SUMMARY = details["current_commit_id"] + ': ' + details["current_commit_summary"]
    elif self.location_commit_summary_style == 'CommitIDAndAuthor':
        LOCATION_COMMIT_SUMMARY = details["current_commit_id"] + ': ' + details["current_commit_author"]

    elif self.location_commit_summary_style == 'Summary':
        LOCATION_COMMIT_SUMMARY = details["current_commit_summary"]

    else:
        LOCATION_COMMIT_SUMMARY = self.location_commit_summary_style

    return (LOCATION_COMMIT_SUMMARY)
