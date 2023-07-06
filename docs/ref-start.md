<!--
# Copyright 2022, 2023 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2023-07-06
-->

# Start command options reference

|Option|Description|
|----------|-----------|
|`--builder`| Optional. Include `--builder local` to force builds running in Travis or Jenkins to behave like a `local` build. Ensures that source Git repository information retrieval or output handling do not affect the outcome of the build. |
|`--cleanup_flags_and_content <tag1,tag2,tag3>`| Optional. Include locally with `--source_dir` to remove an outdated feature flag and all of the content within it from all files in the directory. For example, you might have set outdated content within a specific flag to hidden, now that flag and the content within it can be removed. Separate more than one tag with a comma. Do not include spaces.|
|`--cleanup_flags_not_content <tag1,tag2,tag3>`| Optional. Include locally with `--source_dir` to remove an outdated feature flag from all files in the directory, but not the content within it. For example, you might have set new content within a specific flag to `all` or all of the locations it needs to be in, so now that flag can be removed, but the content within the tags must remain. Separate more than one tag with a comma. Do not include spaces.|
|`--locations_file <path_to_locations_file>`|Required. The path to the JSON file of locations to create content for.|
|`--output_dir <path_to_output_directory>`|Optional. The path to the output location.|
|`--rebuild_files <file1,file2,file3>`|Optional. Force a rebuild of specific files no matter what changes kicked off the build. For multiple files, include them as a comma-separated list. This flag is helpful for something like a landing page, so that the date updates even though the content itself does not change often. Example: `--rebuild_files landing.json,folder/file.md`|
|`--rebuild_all_files`|Optional. Force a rebuild of all files no matter what changes kicked off the build. This option is helpful when you're running the Markdown Enricher for the first time on new downstream branches.|
|`--slack_bot_token ${SLACK_BOT_TOKEN}`|Optional. The token for the Slack bot. This value can be an environment variable.|
|`--slack_channel ${SLACK_CHANNEL}`|Required with the `--slack_bot_token` flag. The ID for the Slack channel. This value can be an environment variable.|
|`--slack_post_success`|Optional. When also using the `--slack_webhook` or `--slack_bot_token` options, you can post success messages to Slack in addition to errors and warnings.|
|`--slack_show_author <True_or_False>`|Optional. When also using the `--slack_webhook` option, you can include (True) or exclude (False) the commit author's Github ID in the Slack post.|
|`--slack_user_mapping <path_to_mapping_file>`|Optional to include with the --slack_bot_token flag. A JSON file that maps a Github ID to a Slack ID.|
|`--slack_webhook ${SLACK_WEBHOOK}`|Optional. The webhook for a Slack channel to post error messages to. This value can be an environment variable.|
|`--source_dir <path_to_source_directory>`|Required. The path to a content directory or a cloned Github repo.|
|`--test_only`|Optional. Performs a check without pushing the results anywhere.|

## Example

```
python <PATH>/md-enricher-for-cicd/mdEnricherForCICD/start.py --source_dir <PATH_TO_UPSTREAM_LOCAL_CLONE> --output_dir <OUTPUT_DIRECTORY> --locations_file <PATH_TO>/locations.json 
```
