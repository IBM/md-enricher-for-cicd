<!--
# Copyright 2022, 2023 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2023-06-01
-->

# Default tags

In your source repository, you can use the names of the locations in your Locations file as tags. Surround the content with HTML-style opening and closing tags. For example, if your locations are `staging` and `prod`, you might tag a sentence like this so that it only displays in the `staging` version of the file.
```
<staging>This content I'm working on. </staging>This content is viewable in all versions. 
```



|Convention|Description|
|----------|-----------|
|No tags| Content without any tags is viewable in all locations.|
|<code>&#60;location1&#62;Location 1 only&#60;/location1&#62;</code>|For example, if you had a location named `location1` in the locations file, content within `location1` tags is viewable in `location1` output, but not `location2` output.|
|<code>&#60;location2&#62;Location 2 only&#60;/location2&#62;</code>|For example, if you had a location named `location2` in the locations file, content within `location2` tags is viewable in `location2` output, but not `location1` output.|
|<code>&#60;hidden&#62;Hidden content only&#60;/hidden&#62;</code>|Content within hidden tags is not viewable in any output.|
|<code>&#60;all&#62;Content displays in every location&#60;/all&#62;</code>|Content within all tags displays in the output for every location. More likely, you'd use `all` tags in the feature flag file rather than in content files. |


Remember:
- If a tag removes the entire content from a file, the file will not be written to the output. 
- Tags cannot have spaces in them.
- If your markdown processor is picky about line breaks, place your tags where line breaks are not going to be left behind.
- Nested tags might be impacted by the tags around them. For example, if you have a large section of content set to hidden but a nested sentence within it set to display, the nested sentence will also be hidden.


#### Adding tags to TOC files
If your markdown processor is picky about line breaks, you must begin and end tags in TOC files on existing lines so that when they are stripped away, line breaks are not left behind.

marked-it `toc.yaml` example:
```
- navgroup: 
    id: section
    topics:
    - topic1.md<staging>
    - topicgroup:
        label: Staging topics
        topics:
        - topic2.md
        - topic3.md</staging>
    - topic4.md
```

You must also add tags to the beginning and end of the markdown file as well to prevent that content file from outputting. Markdown processors are not generally as picky as TOC files so line breaks that are left usually do not affect the formatting of the transformed content. However, when surrounding a whole file with tags, make sure to start the tag on the same line as the first line of the metadata frontmatter.

Example metadata for marked-it:
```
<staging>---

copyright:
  years: 2014, [{CURRENT_YEAR}]
lastupdated: "[{LAST_UPDATED_DATE}]"

keywords: keyword1, keyword 2

subcollection: subcollection-name

---

# My markdown file

...

</staging>
```


