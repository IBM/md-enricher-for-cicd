#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def start():

    versionNumber = '1.2.5.5.20240724'

    # Process the command-line options

    import argparse
    import sys

    # Create the parser
    my_parser = argparse.ArgumentParser(description='Enrich your markdown content.')

    # Add the arguments
    my_parser.add_argument('--builder', action='store', type=str, help='Override the default builder',
                           choices=['local'])

    my_parser.add_argument('--cleanup_flags_and_content', action='store', type=str,
                           help='In a local clone of the source files, remove the feature flags and remove the content between them.' +
                           'List the comma-separated flags without spaces between them.')

    my_parser.add_argument('--cleanup_flags_not_content', action='store', type=str,
                           help='In a local clone of the source files, remove the feature flags, but leave the content between them.' +
                           'List the comma-separated flags without spaces between them.')

    my_parser.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)

    my_parser.add_argument('--feature_flag_migration', action='store_true', help=argparse.SUPPRESS)

    my_parser.add_argument('--gh_token', action='store', type=str,
                           help='The Github token to access the upstream and downstream repositories.')

    my_parser.add_argument('--gh_username', action='store', type=str,
                           help='The Github username to access the upstream and downstream repositories.')

    my_parser.add_argument('--ibm_cloud_docs', action='store_true', help='Identifies repos as IBM Cloud Docs repos.')

    my_parser.add_argument('--ibm_cloud_docs_keyref_check', action='store_true',
                           help='For IBM Cloud Docs repos, check keywords against the global and service keyref files.')

    my_parser.add_argument('--ibm_cloud_docs_locations', action='store_true', help='Generate a ' +
                           'locations file automatically based on IBM Cloud Docs locations and the current repo information.')

    my_parser.add_argument('--ibm_cloud_docs_prep', action='store_true', help='Generate a ' +
                           'locations file automatically based on IBM Cloud Docs locations and the ' +
                           'current repo information. Also download relevant conref files.')

    my_parser.add_argument('--ibm_cloud_docs_product_name_check', action='store_true',
                           help='For IBM Cloud Docs repos, check product name replacements against the YAML file.')

    my_parser.add_argument('--ibm_cloud_docs_sitemap_depth', action='store', type=str,
                           help='For IBM Cloud Docs repos, if a sitemap is created, the depth of the title headings to include.',
                           default='H3', choices=['H1', 'H2', 'H3', 'H4', 'off'])

    my_parser.add_argument('--ibm_cloud_docs_sitemap_rebuild_always', action='store_true',
                           help='Force the regeneration of the sitemap on every build. For services that reuse content in other repos.')

    my_parser.add_argument('--ibm_docs', action='store_true', help='Identifies repos as IBM Docs repos.')

    my_parser.add_argument('--locations_file', action='store', type=str,
                           help='The path to the JSON file of locations to create content for.')

    my_parser.add_argument('--output_dir', action='store', type=str, help='The path to the output location.')

    my_parser.add_argument('--rebuild_all_files', action='store_true',
                           help='Force a rebuild of all files no matter what changes kicked off the build.')

    my_parser.add_argument('--rebuild_files', action='store', type=str,
                           help='Force a rebuild of comma-separated list of files in addition to the changes that kicked off the build. ' +
                           'Helpful for landing page date updates where the date must change but the content itself does not change often.')

    my_parser.add_argument('--slack_bot_token', action='store',
                           help='The token for a Slack bot to post ephemeral and normal error messages to.')

    my_parser.add_argument('--slack_channel', action='store',
                           help='With the slack_bot_token, the Slack channel to post to.')

    my_parser.add_argument('--slack_post_success', action='store_true',
                           help='When True, posts errors, warnings, and successes to Slack. When False, posts errors and warnings to Slack.')

    my_parser.add_argument('--slack_post_start', action='store_true',
                           help='When True, posts a build start message to Slack.')

    my_parser.add_argument('--slack_show_author', choices=[True, False], default=True,
                           help='Includes the commit author\'s Github ID in the Slack post.')

    my_parser.add_argument('--slack_user_mapping', action='store', type=str,
                           help='The path to a JSON file that maps Github IDs to Slack IDs.')

    my_parser.add_argument('--slack_webhook', action='store',
                           help='The webhook for a Slack channel to post error messages to.')

    my_parser.add_argument('--source_dir', action='store', type=str, help='The path to a cloned Github repo.')

    my_parser.add_argument('--test_only', action='store_true',
                           help='Performs a check without pushing the results anywhere.')

    my_parser.add_argument('--unprocessed', action='store_true',
                           help='Use the Markdown Enricher to move files, but do not process content. Tags and styling remain.')

    my_parser.add_argument('--validation', action='store', type=str,
                           help='Check tags and image file paths.', default='off', choices=['on', 'off'])

    my_parser.add_argument('--version', action='store_true', help='View the installed version of the Markdown Enricher.')

    # Execute the parse_args() method
    args = my_parser.parse_args()

    builder = args.builder
    cleanup_flags_and_content = args.cleanup_flags_and_content
    cleanup_flags_not_content = args.cleanup_flags_not_content
    debug = args.debug
    feature_flag_migration = args.feature_flag_migration
    gh_username = args.gh_username
    gh_token = args.gh_token
    ibm_cloud_docs = args.ibm_cloud_docs
    ibm_cloud_docs_keyref_check = args.ibm_cloud_docs_keyref_check
    ibm_cloud_docs_locations = args.ibm_cloud_docs_locations
    ibm_cloud_docs_prep = args.ibm_cloud_docs_prep
    ibm_cloud_docs_product_name_check = args.ibm_cloud_docs_product_name_check
    ibm_cloud_docs_sitemap_depth = args.ibm_cloud_docs_sitemap_depth
    ibm_cloud_docs_sitemap_rebuild_always = args.ibm_cloud_docs_sitemap_rebuild_always
    ibm_docs = args.ibm_docs
    locations_file = args.locations_file
    output_dir = args.output_dir
    rebuild_all_files = args.rebuild_all_files
    rebuild_files = args.rebuild_files
    slack_bot_token = args.slack_bot_token
    slack_channel = args.slack_channel
    slack_post_start = args.slack_post_start
    slack_post_success = args.slack_post_success
    slack_show_author = args.slack_show_author
    slack_user_mapping = args.slack_user_mapping
    slack_webhook = args.slack_webhook
    source_dir = args.source_dir
    test_only = args.test_only
    unprocessed = args.unprocessed
    validation = args.validation
    version = args.version

    if version is True:
        print('Doctopus Markdown Enricher ' + versionNumber)

    try:
        locations_file
    except Exception:
        locations_file = None

    if ibm_cloud_docs_product_name_check is True:
        ibm_cloud_docs_keyref_check = True

    if ibm_cloud_docs_locations is True:
        try:
            from mdenricher.internal.locations.locationsIBMCloudDocs import locationsIBMCloudDocs
            locationsIBMCloudDocs(locations_file, source_dir)
        except Exception:
            print('Option not available outside of IBM.')
            sys.exit(1)

    elif ibm_cloud_docs_prep is True:
        try:
            from mdenricher.internal.locations.prepIBMCloudDocs import prepIBMCloudDocs
            prepIBMCloudDocs(gh_username, gh_token, locations_file, source_dir)
        except Exception as e:
            print('Option not available outside of IBM.')
            print(e)
            sys.exit(1)

    elif cleanup_flags_and_content is not None or cleanup_flags_not_content is not None:
        from mdenricher.tags.cleanup import cleanup
        cleanup(cleanup_flags_and_content,
                cleanup_flags_not_content,
                source_dir)

    if source_dir is not None:
        from mdenricher.main import main
        main(builder,
             debug,
             feature_flag_migration,
             gh_username,
             gh_token,
             ibm_cloud_docs,
             ibm_cloud_docs_keyref_check,
             ibm_cloud_docs_sitemap_depth,
             ibm_cloud_docs_sitemap_rebuild_always,
             ibm_docs,
             locations_file,
             output_dir,
             rebuild_all_files,
             rebuild_files,
             slack_bot_token,
             slack_channel,
             slack_post_start,
             slack_post_success,
             slack_show_author,
             slack_user_mapping,
             slack_webhook,
             source_dir,
             test_only,
             unprocessed,
             validation,
             versionNumber)
