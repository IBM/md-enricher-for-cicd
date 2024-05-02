<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-05-01
-->

# Images
As with all markdown content, adding images to your content is a two-step process:
1. Upload an image and, if needed, its source file to the `images` directory in the source repo.
1. Add the image name to the markdown file. You can specify images using markdown or HTML styling. Include the path as it will be in the output, not in the source. If the image path is part of a reuse snippet in files that will output to different directory levels, the Markdown Enricher attempts to adjust the filepath appropriately based on where they are located.
  * `![Image](images/logo.svg)`
  * `<img src="images/logo.svg" alt="Image" width="50%" height="50%">`

The Markdown Enricher handles image delivery based on the following circumstances:
* If the image is referenced in a markdown file in a downstream location, then that image is pushed to the downstream location. If the image is not referenced, then 
* Whatever happens to the image, whether it is pushed downstream or not, the same thing happens to its source file (AI, PSD, SVG, etc.) as long as the filenames match other than the extension.

> **Note**: With the default values for `img_output_filetypes` and `img_src_filetypes`, SVG files are considered both image source files and output files. Keep this in mind when customizing your own image lists.
