## Contributing In General
Our project welcomes external contributions.

To contribute code or documentation, submit a [pull request](https://github.com/IBM/md-enricher-for-cicd/pulls).

A good way to familiarize yourself with the codebase and contribution process is
to look for and tackle low-hanging fruit in the [issue tracker](https://github.com/IBM/md-enricher-for-cicd/issues).
Before embarking on a more ambitious contribution, get in touch with us.

**Note: We appreciate your effort, and want to avoid a situation where a contribution
requires extensive rework (by you or by us), sits in backlog for a long time, or
cannot be accepted at all.**

### Proposing new features

If you would like to implement a new feature, [raise an issue](https://github.com/IBM/md-enricher-for-cicd/issues)
before sending a pull request so the feature can be discussed. This is to avoid
you wasting your time working on a feature that the project developers
are not interested in accepting into the code base.

### Fixing bugs

If you would like to fix a bug, [raise an issue](https://github.com/IBM/md-enricher-for-cicd/issues) before sending a
pull request so it can be tracked.

### Merge approval

The project maintainers use LGTM (Looks Good To Me) in comments on the code
review to indicate acceptance.

For a list of the maintainers, see the [MAINTAINERS.md](MAINTAINERS.md) page.

## Legal

Each source file must include a license header for the Apache
Software License 2.0. Using the SPDX format is the simplest approach.
e.g.

```
#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#
```

We have tried to make it as easy as possible to make contributions. This
applies to how we handle the legal aspects of contribution. We use the
same approach - the [Developer's Certificate of Origin 1.1 (DCO)](https://github.com/hyperledger/fabric/blob/master/docs/source/DCO1.1.txt) - that the Linux® Kernel [community](https://elinux.org/Developer_Certificate_Of_Origin)
uses to manage code contributions.

We simply ask that when submitting a patch for review, the developer
must include a sign-off statement in the commit message.

Here is an example Signed-off-by line, which indicates that the
submitter accepts the DCO:

```
Signed-off-by: John Doe <john.doe@example.com>
```

You can include this automatically when you commit a change to your
local git repository using the following command:

```
git commit -s
```

## Setup
- Install Python.
- Install the Python requirements.
- Set environment variables, if necessary.


## Testing
[Run the Markdown Enricher locally](https://pages.github.com/IBM/md-enricher-for-cicd-docs/#/local) to test your code changes.

## Coding style guidelines
flake8 and mypy are used to enforce coding styles.
