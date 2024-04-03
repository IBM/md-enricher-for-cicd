<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-04-03
-->

# Locations file


## `config` section

|Name|Default values|Description|
|---|---|---|
|`source_github_branch`|String |Required when running on each commit in Travis or Jenkins to differentiate the main branch from other development branches that are made from it. For the value, enter the name of the upstream branch, such as `main`, `master` or `source`. Not required for local builds.|
|`filetypes`|`.html, .json, .md, .yml, .yaml, .txt, toc`|Optional. The types of files that are processed by the Markdown Enricher.|
|`img_output_filetypes`|`.gif, .GIF, .jpg, .JPG, .jpeg, .JPEG, .mp4, .MP4, .png, .PNG, .svg, .SVG`|Optional. Images that are referenced in content files and are stored in the `images` directory.|
|`img_src_filetypes`|`.ai, .AI, .psd, .PSD, .sketch, .svg, .SVG`|Optional. Image source files that might not be referenced in content files. These source files must have the same file name as their output counterparts and must be stored in the `images` directory.|
|`last_commit_id_file`|`<source_github_branch>_commit.txt`|Optional. The name of the file where the SHA is stored for the last commit that the Markdown Enricher processed. |
|`log_branch`|`<source_github_branch>-logs`|Optional. The name of the branch where logs are stored. This branch is automatically created in the upstream repo.|
|`log_file_name`|`.md-enricher-for-cicd.log`|Optional. The name of the log file. |
|`reuse_snippets_folder`|`reuse-snippets`|Optional. The name of the folder where snippets are stored as markdown files. This directory stores files are reused in other files and produce no output files themselves. This value must be folder or a path to a subfolder within the source directory. Example: `docs/reuse-snippets`.|
|`reuse_phrases_file`|`phrases.json`|Optional. A JSON file where snippet phrases or sentences are stored for reuse in other topics. This file must be stored in the `reuse_snippets_folder` and produces no output itself. |


## `locations` section

|Name|Value|Description|
|---|---|---|
|`location`|String| Required. The name of the location. This name can be used as tags in content.|
|`location_build`|<ul><li>`on` (default)</li><li>`off`</li></ul>|Optional. You can choose to generate output (`on`) or not generate output (`off`) for a location to speed up the overall build. Even when not generating output, the location name must still be included in the locations file so that the tags can be handled appropriately.|
|`location_output_action`|<ul><li>`none` (default)</li><li>`merge-automatically`</li><li>`create-pr`</li></ul>| Optional. Allowed values: <ul><li>`none`: Output is generated and not merged into any Github branch. Use `none` when you want to generate output locally or you want to push the output to a location outside of Github.</li><li>`merge-automatically`: Output is generated and merged into the downstream location, if specified specified. Helpful for staging content.</li><li>`create-pr`: Output is generated and a pull request is created for you to review and merge into the downstream location specified. Helpful for production content.</li></ul>|
|`location_github_url`|String|Required when `location_output_action` is set to something other than `none`. The URL for the downstream location. Example: `https://github.com/org/repo`|
|`location_github_branch`|String|Required when `location_output_action` is set to something other than `none`. The name of the branch to push output to in the downstream location. Example: `main`|
|`location_comments`|<ul><li>`on` (default)</li><li>`off`</li></ul>|Optional. HTML comments can be included (`on`) or excluded (`off`) in the output.|
|`location_commit_summary_style`|<ul><li>`Author`</li><li>`AuthorAndSummary` (default)</li><li>`BuildNumber`</li><li>`BuildNumberAndSummary`</li><li>`CommitID`</li><li>`CommitIDAndSummary`</li><li>`CommitIDAndAuthor`</li><li>`Summary`</li><li>Enter your own text.</li></ul>|Optional. The display of the Git commit summary when pushing output downstream. |
|`location_contents`|JSON|Optional. Special handling of individual files and folders for a downstream location.|


## Example

```
{
    "markdown-enricher": {
        "config": {
            "source_github_branch": "main",
            "last_commit_id_file": ".main_commit.txt",
            "log_branch": "main-logs"
        },
        "locations": [
            {
                "location": "staging",
                "location_github_url": "https://github.com/myOrg/myRepo",
                "location_github_branch": "staging",
                "location_output_action": "merge-automatically",
                "location_comments": "off",
                "location_commit_summary_style": "AuthorAndSummary"
            },
            {
                "location": "prod",
                "location_github_url": "https://github.com/myOrg/myRepo",
                "location_github_branch": "prod",
                "location_github_branch_pr": "next-prod-push",
                "location_output_action": "create-pr",
                "location_comments": "off",
                "location_commit_summary_style": "Summary"
            }
        ]
    }
}
```
