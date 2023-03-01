<!--
# Copyright 2022, 2023 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2023-02-23
-->

# Running in Travis


1. Configure [Travis](https://docs.travis-ci.com/user/tutorial/#to-get-started-with-travis-ci-using-github) for your Github repository.
1. Configure the settings for Travis.
    a. Click **More options** > **Settings**. If the Settings option does not display, wait a minute and refresh the page. If the problem persists, verify you are an admin of the upstream repo, then in Travis, click your username > **Profile** > **Sync Account** to refresh your Github permissions in Travis.
    
    a. Turn **Build only if .travis.yml is present** on. 

    a. Turn **Limit concurrent jobs** on and enter 1.

    a. Disable the job from running on **Pull requests**.

    a. Add the [environment variables](setup.md#Environment-variables).
1. Create a [locations file](setup.md#Locations-file). 
1. Create a `.travis.yml` file. Example:
    ```
    matrix:
    include:
    - language: python
        python: 3.10.0
        env:
        - name="Markdown Enricher for Continuous Integration and Continuous Deployment"
        script:
        - echo "Getting the version number of the latest Markdown Enricher release..."
        - export version=$(echo $(curl -u ${GH_TOKEN}:x-oauth-basic -s https://api.github.com/repos/IBM/md-enricher-for-cicd/releases/latest | jq -r '.tag_name'))
        - echo ${version}
        - echo "Downloading the latest Markdown Enricher release..."
        - bash <(curl -O -u ${GH_TOKEN}:x-oauth-basic -sL https://github.com/IBM/md-enricher-for-cicd/archive/${version}.zip)
        - echo "Extracting the latest Markdown Enricher release:"
        - |
            if unzip -q -o ${version}.zip; then
                echo "Cloned repo unzipped."
            else
                echo $? 
                printf "ERROR: The Markdown Enricher repo could not be cloned. The GH_TOKEN might be expired."
                travis_terminate 1
            fi
        - echo "Starting the Markdown Enricher script..."
        - python -m pip install -r ${TRAVIS_BUILD_DIR}/*md-enricher-for-cicd-*/requirements.txt
        - python ${TRAVIS_BUILD_DIR}/*md-enricher-for-cicd-*/md-enricher-for-cicd/mdEnricherForCICD/start.py --source_dir ${TRAVIS_BUILD_DIR} --locations_file ${TRAVIS_BUILD_DIR}/*md-enricher-for-cicd-*/md-enricher-for-cicd/locations.json --slack_webhook ${SLACK_WEBHOOK} | tee -a ${TRAVIS_BUILD_DIR}/.md-enricher-for-cicd.log ; travis_terminate ${PIPESTATUS[0]}
    ```
1. Mark up your content with tags. These tags can be the names of the locations or the flags in the `feature-flags.json` file. When you commit the change, a Travis build is kicked off.




