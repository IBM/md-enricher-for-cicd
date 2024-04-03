<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-04-03
-->


# Common errors
Some errors can be fixed in your content and some errors come from the continuous delivery tools.

Common content errors:
- Mismatched tags
- Nested tags that aren't being removed properly
- Missing snippets in `.md` files or the `phrases.json` file




## Travis console log is incomplete

Refresh the page.


## Travis builds are running, but commits aren't getting picked up

Github might be down.Check the [Github status page](https://www.githubstatus.com/).


## Travis `git checkout` error

You see the following error in the Travis console log: 
```
The command "git checkout -qf <commit_ID>" failed and exited with 128 during ...
```

The branch was deleted before the Travis build had a chance to checkout the commit. Usually when this happens, the next build is from the merge of the PR. As long as the commit from the merge doesn't error, the error from the branch can be ignored.


## Travis error generating the build script

You see the following error in the Travis console log: 
```
An error occurred while generating the build script.
```

Restart the build or make another change to kick off another build.


## Travis isn't running on a fork of an enabled repo
You must enable Travis and go through the setup steps to run Travis builds on a fork. Learn more in the [Travis documentation](https://travis-ci.community/t/pull-requests-from-forks-does-not-trigger-travis-ci/8393).

