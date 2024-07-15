<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-07-13
-->

# Try it out!

Try out the Markdown Enricher with example markdown files.

1. Install [Python 3.8 or later](https://www.python.org/downloads/).

1. Install the Markdown Enricher. This example uses the version from the `main` branch, but you can use the name of any branch or a specific release version. Including `--upgrade` ensures that any out of date packages that are required by the Markdown Enricher are updated.
    ```
    python3.12 -m pip install git+https://github.com/IBM/md-enricher-for-cicd.git@main --upgrade
    ```

1. Verify the installation by checking the version number.
    ```
    mdenricher --version
    ```

1. In the cloned repository directory, review the contents of the `example` directory.
    - `locations.json`: The output locations (`staging` and `prod`) and the customizations for each one. Note that there isn't much required for pre-processing the files without delivering the output anywhere, just the names of the locations and that no action is required with the output. [Learn more](setup.md).
    - `feature-flags.json`: A configuration file that defines custom tags for marking up content to appear in the output for specific locations. [Learn more](feature-flags.md).
    - `reuse-snippets`: Files that can be referenced in content markdown files and reused as necessary. [Learn more](reuse.md).
    - Markdown files: Content files, which can be stored in subfolders.

1. Run the `mdenricher` command. [Learn more about mdenricher command options](setup.md).
    ```
    mdenricher --source_dir <SOURCE_FILES_DIRECTORY> --output_dir <OUTPUT_FILES_DIRECTORY> --locations_file <PATH>/locations.json
    ```

    Example:
    ```
    mdenricher --source_dir <PATH>/md-enricher-for-cicd/example --output_dir <PATH>/md-enricher-for-cicd/example-output --locations_file <PATH>/md-enricher-for-cicd/example/locations.json
    ```

1. Navigate to the output directory and review the output files. Notice how content that had location-specific tags around it only displays in the output for that location.




