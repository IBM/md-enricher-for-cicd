<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-07-18
-->

# Running in Jenkins

1. Set up a webhook in the upstream repo to kick off the build on every commit.

1. Create a shell script to define the build.

1. Configure a [locations file](setup.md). 

1. Run the [mdenricher command](setup.md). Example: 
   ```
mdenricher --source_dir <PATH_TO_UPSTREAM_LOCAL_CLONE> --output_dir <OUTPUT_DIRECTORY> --locations_file <PATH_TO>/locations.json 
```

