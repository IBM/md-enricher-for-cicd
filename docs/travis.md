<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-07-18
-->

# Running in Travis


1. Configure [Travis](https://docs.travis-ci.com/user/tutorial/#to-get-started-with-travis-ci-using-github) for your Github repository.
1. Configure the settings for Travis.
    a. Click **More options** > **Settings**. If the Settings option does not display, wait a minute and refresh the page. If the problem persists, verify you are an admin of the upstream repo, then in Travis, click your username > **Profile** > **Sync Account** to refresh your Github permissions in Travis.
    
    a. (Travis 2) Turn **Build only if .travis.yml is present** on. 

    a. Turn **Limit concurrent jobs** on and enter 1.

    a. Disable the job from running on **Pull requests**.

    a. Add the [environment variables](setup.md#environment-variables).
1. Create a [locations file](setup.md#locations-file). 
1. Create a `.travis.yml` file. Example:
    
    ```
    matrix:
    include:
    - language: python
        python: 3.12
        env:
        - name="Markdown Enricher for Continuous Integration and Continuous Deployment"
        script:
        - echo "Installing the Markdown Enricher..."
        - git+https://github.com/IBM/md-enricher-for-cicd.git@main --upgrade
        - echo "Running the Markdown Enricher..."
        - mdenricher --source_dir ${TRAVIS_BUILD_DIR} --locations_file ${TRAVIS_BUILD_DIR}/locations.json --slack_webhook ${SLACK_WEBHOOK} | tee -a ${TRAVIS_BUILD_DIR}/.md-enricher-for-cicd.log ; travis_terminate ${PIPESTATUS[0]}
    ```
1. Mark up your content with tags. These tags can be the names of the locations or the flags in the `feature-flags.json` file. When you commit the change, a Travis build is kicked off.




