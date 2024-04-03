<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-04-03
-->

# Linters

The Markdown Enricher includes several linters for helping you identify and correct content errors.

## JSON linter

[https://www.npmjs.com/package/jsonlint](https://www.npmjs.com/package/jsonlint)

Runs on commits to the source branch and any working branch to check JSON files, such as the `phrases.json` and `feature-flags.json` files, for proper JSON formatting. Errors will fail the Markdown Enricher build.

What the linter looks for:

- If there is nested content (applies to `feature-flags.json`), start and end the file with `[ ]`
- Non-nested content (applies to `phrases.json`) or sections of nested content must start and end with `{ }`
- No comma after last entry
- If a `phrases.json` value must include quotation marks, you must escape the quotation marks with a backslash. Example: `"{[logo]}":"<img src=\"images/logo.svg\" width=\"32\" alt=\"Logo\" style=\"width:32px;\" />",`

> Note: Newlines are automatically stripped out to prevent JSON linter errors.


## Tag handling check

All HTML tags are validated in the output files. If there is a non-standard HTML tag that is leftover after all of the replacements are done (because of a tagging error or a flag that was not included in the `feature-flag.json` file), a warning is issued.


## Variable validation post-check

Variables in HTML code blocks are validated as part of the HTML tag validation. If they do not have the proper `&lt;` and `&gt;` coding, a warning is issued. This validation is done because if `<>` are used instead, the variables disappear from the framework display.


## Travis checks
If you are running the Markdown Enricher from Travis, any errors cause the build to fail and displays on pull requests as failed.



In the pull request itself, you can also see if the build was successful for not.

