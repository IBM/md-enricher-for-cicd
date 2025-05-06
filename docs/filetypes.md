<!--
# Copyright 2022, 2025 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2025-05-06
-->

# Supported file types

By default, these are the supported file types the Markdown Enricher can handle.
```
.html, .json, .md, .nojekyll, .yml, .yaml, .txt, toc
```


Supported image output file types:
```
.gif, .GIF, .jpg, .JPG, .jpeg, .JPEG, .mp4, .MP4, .png, .PNG, .svg, .SVG
```

Supported image source file types:
```
.ai, .AI, .drawio, .psd, .PSD, .sketch, .svg, .SVG
```




## Defining your own file types

You can choose which file types are defined by adding them to the locations file in the `config` section. The list you define supercedes what is set by default, so if there are any file types from the original list that you'd like to include, include them in your list as well.
```
{
    "markdown-enricher": 
    {   
        "config": 
            {
                "source_github_branch": "main",
                "filetypes": ".html, .json, .md, .xml",
                "img_output_filetypes": ".png, .PNG",
                "img_src_filetypes": ".ai, .AI",
                "last_commit_id_file": "main_commit.txt",
                "log_branch": "main-logs",
                "log_file_name": ".md-enricher-for-cicd.log"
            },
        "locations":
        ...
```
