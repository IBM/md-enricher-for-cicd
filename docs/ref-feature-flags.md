<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-07-18
-->

# Feature flag file example


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

