<!--
# Copyright 2022, 2025 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2025-05-06
-->

# Comments

You can use HTML style comments (<code>&lt;!-- ... --&gt;</code>) in your markdown files. You can choose whether to include the comments in the output when you configure the [locations file](setup.md). 


In cases where there are specific comments you do not want removed, even when `location_comments` remain `off`, you can add `ME_ignore` to a comment to keep it in the output.

![example in a comment](images/me-ignore-comment.png)
