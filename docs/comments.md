<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-07-23
-->

# Comments

You can use HTML style comments (<code>&lt;!-- ... --&gt;</code>) in your markdown files. You can choose whether to include the comments in the output when you configure the [locations file](setup.md). 


In cases where there are specific comments you do not want removed, even when `location_comments` remain `off`, you can add `ME_ignore` to a comment to keep it in the output.

Example source:

<pre>&#60;!--ME_ignore This is a comment I want to keep.--&#62;</pre>


Example output:

<pre>&#60;!--This is a comment I want to keep.--&#62;</pre>

