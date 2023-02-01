<!--
# Copyright 2022, 2023 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2023-02-01
-->

# Feature flags

Rather than tag different collections of changes with location names, you can create your own custom tags. Define them in a `feature-flags.json` file. 

For example, to manage content related to a specific feature that is in development, create a feature flag named `myfeature`. Set the display value to a location name in `feature-flags.json`, say `staging`. When you're ready for that content to be in both the `staging` and `prod` content, change the `staging` feature flag to `all`. The Markdown Enricher scans every file in the supported file types list for this feature flag and handles the tag changes appropriately.

|Convention|Description|
|----------|-----------|
|<code>&#60;anyTagName&#62;Feature flag content only&#60;/anyTagName&#62;</code>|Add a tag that you want to use to <code>feature-flags.json</code> and indicate which locations the content should be displayed in. Do not include spaces in the name. When something is changed in `feature-flags.json`, every file is checked to see if the change needs to be made in that file too. </p>|



<br />

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



#### Optional: Adding comments to the `feature-flags.json` file
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

