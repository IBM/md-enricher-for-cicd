<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-09-04
-->

# Feature flags

Rather than tag different collections of changes with location names, you can create your own custom tags. Define them in a `feature-flags.json` file. 

For example, to manage content related to a specific feature that is in development, create a feature flag named `myfeature`. Set the display value to a location name in `feature-flags.json`, say `staging`. When you're ready for that content to be in both the `staging` and `prod` content, change the `staging` feature flag to `all`. The Markdown Enricher scans every file in the supported file types list for this feature flag and handles the tag changes appropriately.

|Convention|Description|
|----------|-----------|
|<code>&#60;anyTagName&#62;Feature flag content only&#60;/anyTagName&#62;</code>|Add a tag that you want to use to <code>feature-flags.json</code> and indicate which locations the content should be displayed in. Do not include spaces in the name. When something is changed in `feature-flags.json`, every file is checked to see if the change needs to be made in that file too. </p>|

<br />

## Adding feature flags

To start using feature flags: 
1. Create a `feature-flags.json` file in the root of your repository. Example tags for `new-feature` and `old-feature` where the locations set in the locations file are `staging` and `prod`.
    ```
[{
    "name": "new-feature",
    "location": "staging"
},
{
    "name": "old-feature",
    "location": "prod"
},
{
    "name": "unchanged-feature",
    "location": "all"
},
{
    "name": "another-unchanged-feature",
    "location": "staging,prod"
}]
```
1. Enter a name for the feature flag. Do not include spaces in the name. Example: `"name": "my-feature",`
1. Enter a location value, `hidden`, `all`, or a comma-separated list of locations. For example, if your locations are `staging`, `prod`, `cli-staging`, and `cli-prod`, you could use a combination of those: `"location": "staging,cli-staging"`
1. Tag your content with the feature name. Example: `<my-feature>Feature specific content.</my-feature>`
1. When you are ready to change the display of that content, for example `staging` content is now ready to be included in the prod content, change the location value in the feature flag file. Remember, if you set the value to `prod`, the content would only display there and not in `staging`. To display the content in both locations, list them individually or use `all`. Every markdown file that has the feature flag in it will be updated. Example: `"location": "all"`

> **Important**: Review the requirements for the [JSON linter](linters.md) if you get errors.



## Optional: Adding comments to the `feature-flags.json` file
To insert comments into the `feature-flags.json` file, you can enter them as their own key, value pair  in each section. The key names do not need to be unique.
```
    {
        "name": "flag1",
        "location": "staging,cli-staging",
        "_comment": "These are comments"
    },
    {
        "name": "flag2",
        "location": "prod,cli-prod",
        "_comment": "These are more comments"
    }
```


## Cleaning up outdated feature flags

When a feature flag is no longer needed, you can run the Markdown Enricher locally on a clone of your source files to clean up those flags and, optionally, the content within them.

To decide whether the content within the tags must be removed in addition to the tags, look at what locations the tag is set to in the feature flags file. If the flag is set to hidden, the content is probably safe to remove as well. If the flag is set to `all` or the content exists in each location is meant to be in, the tags are probably safe to remove, but the content within them must be left behind.

1. Install [Python 3.8 or later](https://www.python.org/downloads/).

1. Install the Markdown Enricher. This example uses the version from the `main` branch, but you can use the name of any branch or a specific release version. Including `--upgrade` ensures that any out of date packages that are required by the Markdown Enricher are updated.
    ```
    python3.12 -m pip install git+https://github.com/IBM/md-enricher-for-cicd.git@main --upgrade
    ```

1. Verify the installation by checking the version number.
    ```
    mdenricher --version
    ```

1. Clone your upstream source repository so that you have the files locally.

1. Run the `mdenricher` command with the `--source_dir` option set to your local clone and with one or both of the cleanup flags.

    The examples below show the two flags separately, but you can use the flags together in the same command to handle tags in different ways within the same command.

    To remove the flags and the content within them:

    ```
    mdenricher --source_dir <PATH_TO_UPSTREAM_LOCAL_CLONE> --cleanup_flags_and_content <tag1,tag2,tag3>
    ```

    To remove the flags, but not the content within them:

    ```
    mdenricher --source_dir <PATH_TO_UPSTREAM_LOCAL_CLONE> --cleanup_flags_not_content <tag1,tag2,tag3>
    ```

1. Push the results to the upstream source repository.
