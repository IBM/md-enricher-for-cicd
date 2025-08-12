def featureFlagListCompile(log, details, all_tags):

    import json
    import os

    from mdenricher.errorHandling.errorHandling import addToErrors

    log.debug('Gathering feature flags.')

    # Get the contents of the feature flags file
    jsonStaging = {
        "name": "staging",
        "location": "draft,review"
        }
    jsonStagingAllowlist = {
        "name": "staging",
        "location": "draft"
        }
    jsonProd = {
        "name": "prod",
        "location": "publish"
        }
    jsonProdReady = {
        "name": "review-publish",
        "location": "review,publish"
        }

    def IBMCloudFFUpdate(featureFlags):
        if details['ibm_cloud_docs'] is True and 'cloud-api-docs' not in str(details['source_github_org']):
            if '\'staging\'' not in str(featureFlags) and 'cloud-docs-allowlist' in str(details['source_github_org']) and 'draft' in all_tags:
                featureFlags.append(jsonStagingAllowlist)
            elif '\'staging\'' not in str(featureFlags) and 'draft' in all_tags and 'review' in all_tags:
                featureFlags.append(jsonStaging)
            if '\'prod\'' not in str(featureFlags) and 'publish' in all_tags:
                featureFlags.append(jsonProd)
            if ('\'review-publish\'' not in str(featureFlags) and 'cloud-docs-allowlist' not in
                    str(details['source_github_org']) and 'review' in all_tags and 'publish' in all_tags):
                featureFlags.append(jsonProdReady)
        return (featureFlags)

    featureFlags = []
    if os.path.isfile((details["source_dir"]) + '/feature-flags.json'):
        details.update({"featureFlagFile": '/feature-flags.json'})
        with open(details["source_dir"] + details["featureFlagFile"], 'r', encoding="utf8", errors="ignore") as featureFlagJson:
            try:
                featureFlags = json.load(featureFlagJson)
            except Exception as e:
                addToErrors('JSON not formatted properly. ' + str(e),
                            details["featureFlagFile"], '', details, log, 'pre-build', '', '')
            else:
                featureFlags = IBMCloudFFUpdate(featureFlags)
                details.update({"featureFlags": featureFlags})
    elif details['ibm_cloud_docs'] is True:
        featureFlags = IBMCloudFFUpdate(featureFlags)
        details.update({"featureFlags": featureFlags})
        details.update({"featureFlagFile": 'None'})
    else:
        details.update({"featureFlagFile": 'None'})
        details.update({"featureFlags": 'None'})

    return (details)
