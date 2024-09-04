<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-09-04
-->

# Images
As with all markdown content, adding images to your content is a two-step process:
1. Upload an image and, if needed, its source file to the `images` directory in the source repo.
1. Add the image name to the markdown file. You can specify images using markdown or HTML styling. Include the path as it will be in the output, not in the source. If the image path is part of a reuse snippet in files that will output to different directory levels, the Markdown Enricher attempts to adjust the filepath appropriately based on where they are located.
  * `![Image](images/logo.svg)`
  * `<img src="images/logo.svg" alt="Image" width="50%" height="50%">`

The Markdown Enricher handles image delivery based on the following circumstances:
* If the image is referenced in a markdown file in a downstream location, then that image is pushed to the downstream location.
* By default, these image output files are handled: `.gif, .jpg, .jpeg, .mp4, .png, .svg`.
* By default, image source files with the extensions `.ai`, `.drawio`, `.psd`, or `.sketch` are not pushed downstream. If they do exist already downstream, they are removed automatically.

> **Note**: With the default values for `img_output_filetypes` and `img_src_filetypes`, SVG files are considered image output files, even though they can be edited and exported as other file types.
