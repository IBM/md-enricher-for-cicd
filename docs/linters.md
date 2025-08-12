<!--
# Copyright 2022, 2025 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2025-07-17
-->

# Checks

The Markdown Enricher includes several checks for helping you identify and correct setup and content errors.

## Errors

Errors must be resolved before content is pushed downstream.

### Initial setup checks

These intitial setup checks cause build errors:
- Source directory specified could not created.
- The source repo or branch does not exist.
- Locations file:
    - Duplicate location names exist in the locations file.
    - The upstream and downstream locations are the same.
    - The locations file does not exist where specified.
    - `location_github_url` or `location_github_branch` is not included in a location where the `location_output_action` is not `none`.
    - The branch specified with `location_github_branch` does not exist.
    - Invalid values for any key.

### YAML linting

YAML content files, such as the `toc.yaml`, are checked for proper YAML formatting.

> Note: Newlines are automatically stripped out.

### JSON linting

JSON content and Markdown Enricher files, such as the `locations.json`, `phrases.json`, and `feature-flags.json` files, are checked for proper JSON formatting. 

- If there is nested content (applies to `feature-flags.json`), start and end the file with `[ ]`
- Non-nested content (applies to `phrases.json`) or sections of nested content must start and end with `{ }`
- No comma after last entry.
- If a `phrases.json` value must include quotation marks, you must escape the quotation marks with a backslash. Example: `"{[logo]}":"<img src=\"images/logo.svg\" width=\"32\" alt=\"Logo\" style=\"width:32px;\" />",`

> Note: Newlines are automatically stripped out.


### Tag check

Tags identified by location names or by the feature flag file are validated. 

- Mismatches between opening and closing tags.

    Example for a valid `<staging>` location:
    ```
    This sentence has a starting tag <staging>here but no closing tag.
    ```

- Tag was removed from the feature flag file, but is still used in content files.
- A tag is duplicated in the feature flag file.
- A tag includes a space in the feature flag file.
- A tag does not include a location in the feature flag file.
- A tag includes an invalid location that is not specified in the locations file.


### Git issues

These issues with Git cause errors. For local builds, this list does not apply.
- Clone issues:
    - A Github username was not specified.
    - A Github token was not specified.
    - The downstream branch could not be cloned or checked out.
    - The downstream Github URL was not valid.
    - A list of branches could not be retrieved for the downstream repo.
- Commit retrieval issues:
    - The last 2 commits could not be retrieved.
    - Branch status could not be retrieved.
    - A diff could not be retrieved between the two commits.
    - Git did not provide a JSON response.
- Push issues:
    - A new branch could not be pushed.
    - Permission denied.
    - Branch protection is enabled and `location_output_action` is set to `merge-automatically`.
    - Push failure for any other reason.
    - A pull request could not be created.
- Logs branch could not be checked out.






## Warnings

Content is still pushed downstream when warnings exist.

### File handling

- If a file is renamed and the old version of the file name does not exist downstream already.
- If a file is renamed and the previous file name could not be retrieved.
- If a file is specified with --rebuild_files, but it does not exist.
- Git commit contains 300 or more changed files.
- Log files could not be pushed to the logs branch.


### Tag check

- A tag exists in the feature flag file but is not used in any content file.
- If tags are used in JSON and were not handled properly so that the JSON is not valid.
- All HTML styling is validated in the output files. If there is a non-standard HTML tag that is leftover after all of the replacements are done (because of a tagging error or a flag that was not included in the `feature-flag.json` file), a warning is issued.

Example:

```
This sentence has a <new-tag-name>tag</new-tag-name> that needs to be added to the feature flag file.
```



### Images

- An image is referenced in a content file but does not exist.
- An image exists in the upstream source but is not referenced in any downstream content file.



### Code blocks

- Empty codeblocks.
- Matching code block and code phrase formatting.
- Variables in HTML code blocks are validated as part of the HTML tag validation. If they do not have the proper `&lt;` and `&gt;` coding, a warning is issued. This validation is done because if `<>` are used instead, the variables disappear from the framework display.

Example:
```
<codeblock>
ls <directory_name>
</codeblock>
```

Corrected:
```
<codeblock>
ls &lt;directory_name&gt;
</codeblock>
```

### Snippets

- Snippet is not formatted properly.
- Whole topic snippet is used, but does not include a `.md` extension.
- Whole topic snippet is used, but does not exist.
- Inline snippet is used, but does not exist in `phrases.json`.
- With the phrase check enabled, an inline snippet exists, but is not used anywhere.
- With the snippet check enabled, a whole topic snippet exists, but is not used anywhere.
