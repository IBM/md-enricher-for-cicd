<!--
# Copyright 2022, 2023 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2023-11-01
-->

# Reuse
Sometimes it's handy to be able to reuse pieces of information in multiple places while only updating it one time. For example, you might want to include the same table in a task topic and in a reference topic. You can choose to use the reuse capabilities that are available by default in the Markdown Enricher or you can use another reuse tool.

## Reuse options available in the Markdown Enricher
Similar to DITA conrefs, you can reuse words, phrases, sections, or whole files in content files. 

> **Before you begin**: You must create a `reuse-snippets` directory in the root of the upstream repo/branch and store these files in that folder. If you create subfolders, you must include the path when using that reference.

|Convention|Description|
|----------|-----------|
|`{[ID]}`|A one-line phrase, sentence, or paragraph that can be stored in the `reuse-snippets/phrases.json` file and re-used in topics by referencing the ID. When something is changed in `reuse-snippets/phrases.json`, every file is checked to see if the change needs to be made in that file too. You can use these references in other references specified in the `reuse-snippets/phrases.json`. **Important**: Review the requirements for the [JSON linter](linters.md) if you get errors.|
|`{[ID.md]}`<br />`{[subfolder/ID.md]}`|Multi-line content that can be stored in the `reuse-snippets/<ID>.md` file and re-used in topics by referencing the topic name. You can use other phrases and files from the `reuse-snippets` directory in these files. When something is changed in one of the `reuse-snippets/<ID>.md` files, every file is checked to see if the change needs to be made in that file too.<p>**Tip:** To indent properly, put the indentation in the snippet file.  In the markdown that references that snippet with an ID, do not put any indentation.</p>|

### Optional: Adding comments to the `phrases.json` file
To insert comments into the `phrases.json` file, you can enter them as their own key, value pair with a unique name.
```
{
"{[common-word]}":"my-tool-name",
"_comment_1":"This is a comment",
"_comment_2":"This is another comment",
"{[tool-version]}":"2.1.2"
}
```


