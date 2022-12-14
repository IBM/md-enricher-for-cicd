#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def locationCommitSummary(self, details):

    if self.location_commit_summary_style == 'AuthorAndSummary':
        LOCATION_COMMIT_SUMMARY = details["current_commit_author"] + ': ' + details["current_commit_summary"]
    elif self.location_commit_summary_style == 'AuthorOnly':
        LOCATION_COMMIT_SUMMARY = details["current_commit_author"]
    elif self.location_commit_summary_style == 'IDOnly':
        LOCATION_COMMIT_SUMMARY = details["current_commit_id"]
    elif self.location_commit_summary_style == 'IDAndSummary':
        LOCATION_COMMIT_SUMMARY = details["current_commit_id"] + ': ' + details["current_commit_summary"]
    elif self.location_commit_summary_style == 'IDAndAuthor':
        LOCATION_COMMIT_SUMMARY = details["current_commit_id"] + ': ' + details["current_commit_author"]
    elif self.location_commit_summary_style == 'SummaryOnly':
        LOCATION_COMMIT_SUMMARY = details["current_commit_summary"]
    else:
        LOCATION_COMMIT_SUMMARY = self.location_commit_summary_style

    return (LOCATION_COMMIT_SUMMARY)
