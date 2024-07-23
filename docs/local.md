<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-07-18
-->

# Running locally
To test your content changes locally before committing them to the source repo or to test changes to the code base, you can run the Markdown Enricher on your local content.

1. Clone your source repo locally and edit the content.
1. Install [Python 3.8 or later](https://www.python.org/downloads/).

1. Install the Markdown Enricher. This example uses the version from the `main` branch, but you can use the name of any branch or a specific release version. Including `--upgrade` ensures that any out of date packages that are required by the Markdown Enricher are updated.
    ```
    python3.12 -m pip install git+https://github.com/IBM/md-enricher-for-cicd.git@main --upgrade
    ```

1. Verify the installation by checking the version number.
    ```
    mdenricher --version
    ```
1. Create a [`locations.json`](setup.md) file. 
1. Open a command line terminal.
1. Run the [mdenricher command](setup.md). Example: 
   ```
mdenricher --source_dir <PATH_TO_UPSTREAM_LOCAL_CLONE> --output_dir <OUTPUT_DIRECTORY> --locations_file <PATH_TO>/locations.json 
```
1. Review the transformed files in the output location.
