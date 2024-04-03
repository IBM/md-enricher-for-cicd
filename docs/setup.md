<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-04-03
-->


# Setting up the Markdown Enricher


## Terminology
* **upstream**: The single repository, branch, or source where you manage what content is meant to go where.
* **downstream**: One or more output repository, branch, or content locations. Do not make changes to content in this location.


## Prerequisites
- You can run the Markdown Enricher on any content if it's on the same local system as the Markdown Enricher, but to take advantage of the content delivery features of the Markdown Enricher, you must use Github Enterprise or [Github Public repositories](https://github.com/).
- If your upstream content is stored in a Github repository, there might be some setup tasks that require you to be an administrator to complete.


## Create the repositories
If you are storing the source or the output in Github repositories, create those repos first. The repos can be public, private, in an Enterprise domain, or wherever the username and token that you use has access to.
- Create an upstream repo or branch, if it's not already created. This source branch must exist before continuing.
- Create downstream repos as necessary. The downstream branches do not need to exist yet.

Note for Github users: Because the same Github username and token is used for upstream and downstream tasks, the upstream and downstream locations must be in the same domain (such as `github.com`), however, they can be in different organizations and repos. You are not required to use Github for storing the upstream or downstream files.


## Locations file
The downstream repositories and branches are defined in a Locations file (`locations.json`). The location names and branches also supply some auto-generated tags that can be used in the content. For every upstream repo, there must be a locations file.

Note: 
- If you are using Github, the upstream and downstream locations must be in the same Github domain (such as `github.com`), however, they can be in different organizations and repos. 
- The `locations.json` file must be local. Remote locations files are not supported.
- The repositories listed in the locations files must exist already, but the branches do not need to exist on first run.
- The locations are built in the order they are listed in the locations file.


### `config` section

`source_github_branch` is the only required key when running on each commit in Travis or Jenkins to differentiate the main branch that other development branches are made from. For the other keys, if unspecified, the default values are used.

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

### `locations` section

The `location` name is the only required key. For the other keys, if unspecified, the default values are used.

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


### Example

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



### Minimal locations file example for local builds
To get started with a local build, all you need is a name for each of the downstream locations, such as `staging` and `prod`. Example: 
   ```
   "markdown-enricher": {
        "locations": [
            {
                "location": "staging",
            },{
                "location": "prod",
            }
         ]
   }
   ```

## Environment variables
For security, there are values that must be set in the environment variables.


|Environment variable|Description|
|----------|-----------|
|`GH_USERNAME`|<br><br>A Github user with proper authorizations for the upstream and downstream locations. Required when using the Markdown Enricher to clone or push output to a Github repository. Important: When choosing which user to use, keep in mind that if you want to have pull requests created to merge content downstream, that user will not be able to merge unless another person approves. To avoid this problem, use a functional ID rather than a contributor's ID. <ul><li>Upstream repos: This user must be given `write` access upstream to create a log branch in the upstream repo. </li><li>Downstream repos: This user must be given `write` access in each downstream location to push changed files. If branch protection is enabled and you want commits automatically merged into that repo, this user must be given `maintainer` or `admin` permission.</li></ul> |
|`GH_TOKEN`|<br><br>The personal access token for the `GH_USERNAME`. Required when using the Markdown Enricher to clone or push output to a Github repository. To create a token, log in to Github and click your user icon > **Settings** > **Developer settings** > **Personal access tokens** > **Tokens** > **Generate new token**. Select the `repo` scope.|
|`SLACK_BOT_TOKEN`|<br><br>Optional. Include to post error and warning messages to Slack via a Slack bot have failures to non-source branch be ephemeral and only visible to the user who made the commit. If you set this variable, you must also set the `SLACK_CHANNEL` variable and create a mapping of the Github to Slack IDs.|
|`SLACK_CHANNEL`|<br><br>Required with `SLACK_BOT_TOKEN`. The ID for the channel in Slack.|
|`SLACK_WEBHOOK`|Optional. Include to post error and warning messages to Slack via incoming webhook.|





## `mdenricher` command options
The `mdenricher` command kicks things off. These are the available options to set with the command.  

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
|`--version`|View the installed version of the Markdown Enricher.|


CLI help:
```
mdenricher --help
```



## Optional Slack configuration

There are two options for Slack configuration. If you choose to have the Markdown Enricher issue Slack posts, the user names as displayed in Github Enterprise are included in the post to help identify which errors or warnings were included in whose content.

### Slack webhooks
Create a Slack channel and webhook so errors can be posted for you. 
1. Create a Slack channel. 
1. Create an incoming webhook in the Slack app. 
1. In the environment variables, add the `SLACK_WEBHOOK` environment variable.
1. In the `mdenricher` command, add `--slack_webhook ${SLACK_WEBHOOK}`.

### Slack bot posts with optional ephemeral messages
You can use a Slack bot and the Slack Python SDK to issue posts. You can choose to set up ephemeral messages by including a mapping of Github user information to Slack IDs. If a change is made in a branch that is not the main source branch, the Slack posts are only visible to the committer of the change and not to everyone else in the channel. Recommended for larger teams to eliminate unnecessary noise in the channel. Ephemeral messages disappear after about 24 hours and are not stored in the Slack history.
1. Create a Slack channel. 
1. For ephemeral messages, create or update a JSON user mapping of Github users to Slack IDs. Example: 
    ```
    {
    "user_mapping": [
            {
                "name": "lloyd",
                "github_id": "Lloyd.V.Christmas",
                "github_name": "Lloyd Christmas",
                "slack_id": "U1A2B3C4D5"
            },
            {
                "name": "harry",
                "github_id": "harry.dunne",
                "github_name": "Harry Dunne",
                "slack_id": "W1A2B3C4D5"
            }
    ]}
    ```
1. Install the Slack app into the Slack channel.
1. In the environment variables, add `SLACK_BOT_TOKEN` and `SLACK_CHANNEL`.
1. In the `mdenricher` command, add `--slack_bot_token ${SLACK_BOT_TOKEN} --slack_channel ${SLACK_CHANNEL} --slack_user_mapping <path_to_mapping_file>`.
