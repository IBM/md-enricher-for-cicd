<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-06-07
-->

# Environment variables reference


|Environment variable|Description|
|----------|-----------|
|`GH_USERNAME`|<br><br>A Github user with proper authorizations for the upstream and downstream locations. Required when using the Markdown Enricher to clone or push output to a Github repository. Important: When choosing which user to use, keep in mind that if you want to have pull requests created to merge content downstream, that user will not be able to merge unless another person approves. To avoid this problem, use a functional ID rather than a contributor's ID. <ul><li>Upstream repos: This user must be given `write` access upstream to create a log branch in the upstream repo. </li><li>Downstream repos: This user must be given `write` access in each downstream location to push changed files. If branch protection is enabled and you want commits automatically merged into that repo, this user must be given `maintainer` or `admin` permission.</li></ul> |
|`GH_TOKEN`|<br><br>The personal access token for the `GH_USERNAME`. Required when using the Markdown Enricher to clone or push output to a Github repository. To create a token, log in to Github and click your user icon > **Settings** > **Developer settings** > **Personal access tokens** > **Tokens** > **Generate new token**. Select the `repo` scope.|
|`SLACK_BOT_TOKEN`|<br><br>Optional. Include to post error and warning messages to Slack via a Slack bot have failures to non-source branch be ephemeral and only visible to the user who made the commit. If you set this variable, you must also set the `SLACK_CHANNEL` variable and create a mapping of the Github to Slack IDs.|
|`SLACK_CHANNEL`|<br><br>Required with `SLACK_BOT_TOKEN`. The ID for the channel in Slack.|
|`SLACK_WEBHOOK`|Optional. Include to post error and warning messages to Slack via incoming webhook.|


