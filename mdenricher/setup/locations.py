#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def locations(details, location, log):

    # Parse the locations section of the locations file

    # from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.errorHandling.errorHandling import addToErrors
    from mdenricher.setup.exitBuild import exitBuild

    try:
        location_name = location["location"]
    except KeyError:
        addToErrors('No value for location was specified in the locations file. This field is required.',
                    'locations.json', '', details, log, 'pre-build', '', '')
        exitBuild(details, log)
    else:
        log.debug('Parsing location information for: ' + location_name)

    try:
        location_build = location["location_build"]
    except KeyError:
        location_build = 'on'

    # If not specified, the output action is local only
    try:
        location_output_action = location["location_output_action"]
    except KeyError:
        location_output_action = 'none'
    else:
        if details['builder'] == 'local':
            location_output_action = 'none'

    try:
        location_github_url = location["location_github_url"]
        if location_github_url.endswith('.git'):
            location_github_url = location_github_url.split('.git')[0]
    except KeyError:
        if location_output_action == 'none':
            location_github_url = None
        else:
            addToErrors('No value for location_github_url was specified in the locations file. This field is required.',
                        'locations.json', '', details, log, 'pre-build', '', '')
            exitBuild(details, log)

    try:
        location_github_branch = location["location_github_branch"]
    except KeyError:
        if location_output_action == 'none':
            location_github_branch = None
        else:
            addToErrors('No value for location_github_branch was specified in the locations file. This field is required.',
                        'locations.json', '', details, log, 'pre-build', '', '')
            exitBuild(details, log)

    if location_output_action == 'create-pr':
        try:
            location_github_branch_pr = location["location_github_branch_pr"]
        except KeyError:
            location_github_branch_pr = location_github_branch + '-next'

    elif location_output_action == 'none':
        location_github_branch_pr = None
    else:
        location_github_branch_pr = None

    location_contents_folders = []
    location_contents_files = []
    try:
        location_contents = location["location_contents"]
    except KeyError:
        location_contents = ['all']
        remove_all_other_files_folders = False
    else:
        try:
            remove_all_other_files_folders = location["location_contents"]["remove_all_other_files_folders"]
        except KeyError:
            remove_all_other_files_folders = False
        try:
            location_contents_folders = location["location_contents"]["folders"]
        except KeyError:
            location_contents_folders = []

        try:
            location_contents_files = location["location_contents"]["files"]
        except KeyError:
            location_contents_files = []

    try:
        location_commit_summary_style = location["location_commit_summary_style"]
    except KeyError:
        location_commit_summary_style = 'AuthorAndSummary'

    try:
        location_comments = location["location_comments"]
    except KeyError:
        location_comments = 'on'
    else:
        if ((not location_comments == 'on') and (not location_comments == 'off')):
            addToErrors('The value for ' + location_comments + ' is not valid. The value must be on or off.',
                        'locations.json', '', details, log, 'pre-build', '', '')
            exitBuild(details, log)

    try:
        location_internal_framework = location["location_internal_framework"]
    except KeyError:
        location_internal_framework = None

    try:
        location_downstream_build_url = location["location_downstream_build_url"]
    except KeyError:
        location_downstream_build_url = None

    return (location_build, location_comments,
            location_commit_summary_style, location_contents, location_contents_files,
            location_contents_folders, location_downstream_build_url, location_github_branch, location_github_branch_pr, location_github_url,
            location_internal_framework, location_output_action, remove_all_other_files_folders)
