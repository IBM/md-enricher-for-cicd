<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-06-21
-->


# Common errors
Some errors can be fixed in your content and some errors come from the continuous delivery tools.

Common content errors:
- Mismatched tags
- Nested tags that aren't being removed properly
- Missing snippets in `.md` files or the `phrases.json` file


## Old commits show in auto-generated PRs
When you merge the pull requests that are created automatically by the Markdown Enricher, you can choose how to merge it. Most likely, the previous PR was merged with the **Squash and merge** selection, where a new commit was created to merge each commit in the PR. That new commit is not known to the PR branch, so the changes continue to be included in the diffs with subsequent PRs.

Instead, in the PR you can select **Merge the pull request** when you merge it. Then the same changes are known to both branches and won't be showed as part of the diff in the next pull request. 

For more information about merging pull requests, see the [Git documentation](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges).

## Changes are included in the auto-generated PR that shouldn't be

While reviewing the auto-generated PR to merge it into the downstream branch, keep an eye out for content that shouldn't be going to that location. If you see this happen, here are some strategies for resolving the issue.

- Go back to the upstream source branch and add the necessary tags to have the content removed from that location. This strategy is the best long-term approach to any downstream content issues like this.
- You can make manual changes in the temporary branch that the PR is merging from. You might edit a line or, if it's a large change needed, copy the original file back from the downstream branch back to temporary branch. But, keep in mind that the contents of the source file upstream do not have these same changes in them and can be pushed downstream as they were again.
- You can close the PR, delete the temporary branch, then make a change in the upstream source branch to rebuild only the files you want updated (or use the `--rebuild_files` option for those select files). This strategy might help you in the moment, but remember, the next time the other files are built, unless there are tagging changes, the changes are added to the PR again.
