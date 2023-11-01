<!--
# Copyright 2022, 2023 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2023-11-01
-->
# Notices

When running the Markdown Enricher in Travis or Jenkins, the author of the commit is collected (`commit` > `author` > `name`) from the Github Enterprise API. This name is used to help teams of writers know who is responsible for which warnings and errors.

This personal information can be included in:
* Log files: The log files are stored in the `<source-branch>-logs` branch of the upstream Github repository.
* Optional: Slack posts: If a webhook is defined, the Github user name is included.
* Optional: Downstream commit summaries: You can define what information is included in the commit summary of files to a downstream repository. The upstream commit author is optional.

Only users with access to the Slack channels or read access to the upstream repository can view the user names.

## Removing author names from Slack posts or commit summaries

To remove author names from Slack posts, include the `--slack_show_author False` flag with your `start` command.


## Removing author names from Slack posts or commit summaries

To remove author names from commit summaries, set the [`location_commit_summary_style`](setup.md) value for each location in the locations file.
