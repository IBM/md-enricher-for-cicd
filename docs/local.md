<!--
# Copyright 2022, 2023 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2023-08-31
-->

# Running locally
To test your content changes locally before committing them to the source repo or to test changes to the code base, you can run the Markdown Enricher on your local content.

1. Install [Python](https://www.python.org/downloads/).
1. Clone your source repo locally and edit the content.
1. Clone the [Markdown Enricher](https://github.com/IBM/md-enricher-for-cicd) repository.
1. Create a [`locations.json`](setup.md) file. 
1. Open a command line terminal.
1. Run the [start command](setup.md). Example: 
   ```
python <PATH>/md-enricher-for-cicd/mdEnricherForCICD/start.py --source_dir <PATH_TO_UPSTREAM_LOCAL_CLONE> --output_dir <OUTPUT_DIRECTORY> --locations_file <PATH_TO>/locations.json 
```
1. Review the transformed files in the output location.
