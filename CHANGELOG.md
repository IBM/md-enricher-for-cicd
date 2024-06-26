# Change log

Notable changes to this project are documented in this file.


## Version 1.2.4, released 21 June 2024

<dl>
<dt>File handling</dt>
<dd><ul>
<dd>Added <code>.bmp</code> as a default image type.</dd>
<li>Redesigned how images are considered used in content.</li>
<li>Images with source file types are removed from downstream locations.</li>
<li><code>.svg</code> images are no longer considered a source file type by default.</li>
<li>Changes to the feature flag file results in the re-processing of all files.</li>
</ul></dd>

<dt>Bug fixes</dt>
<dd><ul>
<li>A Slack post was not issued for JSON formatting errors in the feature flag file.</li>
<li>Rebuild conflicts between repos built with Travis, then Jenkins.</li>
<li>Too many images deleted from downstream.</li>
<li>Content that is surrounded by a tag and also surrounded by a different tag in the <code>toc.yaml</code> results in duplicate content in the same file.</li>
<li>Images with <code>?raw=true</code> not handled properly.</li>
<li>Comments with reuse snippets in them not handled properly.</li>
</ul></dd>
</dl>


## No updates for version 1.2.3

Changes published internally within IBM.

## Version 1.2.2, released 07 June 2024
<dl>
<dt>New and updated <code>mdenricher</code> command options</dt>
<dd>
<ul><li>Added <code>--slack_post_start</code>.</li>
<li>Added <code>--unprocessed</code> to allow files to be pushed to a downstream location without processing any content.</li>
<li>Enabled values specified with the <code>--slack_webhook</code> and <code>--slack_channel</code> options to be comma-separated lists.</li><ul>
</dd>
</dl>

<dl>
<dt>Content processing improvements</dt>
<dd>
<ul><li>Stopped pushing image source files downstream automatically.</li>
<li>For code block validation, added handling for example codeblocks that use four backticks.</li>
<li>Added <code>ME_ignore</code> to prevent transformation of specific comments and reuse snippets.</li>
<li>If errors exist, such as a mismatched tag, changes are not pushed downstream.</li>
<li>Speed improvements.</li><ul>
</dd>
</dl>

<dl>
<dt>Bug fixes</dt>
<dd>
<ul><li>Commits where summaries include quotation marks do not get pushed downstream.</li>
<li>Comments with <code>#</code> in them removed even when comments are enabled and sitemaps are not enabled.</li>
<li>Images copied to wrong downstream folder.</li>
<li>Changes to feature flag locations don't affect the files that use those tags.</li>
<li>Sitemap exception.</li><ul>
</dd>
</dl>


## Version 1.2.1, released 01 May 2024
<dl>
<dt>Added <code>--gh_username</code> and <code>--gh_token</code> options</dt>
<dd>As an alternative to setting the <code>GH_USERNAME</code> and <code>GH_USERNAME</code> environment variables, you can include authentication by using the <code>--gh_username</code> and <code>--gh_token</code> options with the <code>mdenricher</code> command.</dd>

<dt>marked-it improvements</dt>
<dd><code>_include-segments</code> topics not outputting to the correct filepath.</dd>
<dd>Added support for tags used in <code>.build.yaml</code> and <code>keyref.yaml</code> files.</dd>
<dd>Added warnings when a date can't be updated because the last updated or copyright metadata is not structured properly.</dd></dd>

<dt>Jenkins improvements</dt>
<dd>Includes fixes for variables, branch name gathering, and directory level setting.</dd>

<dt>Bug fixes</dt>
<dd>
    <dd>If the log branch did not already exist, the branch could not be created and logs were not stored.</dd>
    <dd>Last updated and copyright date warnings issued when they don't apply.</dd>
    <dd>Image warning for images that exist.</ldd>
    <dd>Github usernames with <code>@</code> in them fail to authenticate during cloning.</dd>
    </dd></dl>

## Version 1.2.0, released 03 April 2024
<dl>
<dt>Updated packaging</dt>
<dd>Install directly from Github as a Python module. </dd>
<dd>Run the tool as <code>mdenricher</code> instead of running as a Python file.<dd>
<dd>Added <code>--version</code>.</dd>

<dt>Additional build support</dt>
<dd>Added Dockerfile.</dd>
<dd>Added support for IBM Cloud Toolchains.</dd>

<dt>Inline and whole file reuse formatting within comments are no longer transformed.</dt>
<dd>In upstream content, you can hide inline and whole file snippets by enclosing them within HTML comments. Those snippets are not transformed.</dd>

<dt>Bug fixes</dt>
<dd>All dates updated in the output of <code>--rebuild_all_files</code> instead of only in the files that were updated.</dd>
</dl>


## Version 1.1.9, released 06 March 2024
<dl>
<dt>Bug fixes</dt>
<dd><ul>
    <li>Error level too high for missing Github IDs in the user mapping file when posting ephemeral Slack messages.</li>
    <li>Error when pushing log files to branch: <code>local variable 'contains' referenced before assignment</code>.</li>
    </ul></dd>
</dl>


## No release for 01 February 2024
No changes were made to warrant a new release this month.

## Version 1.1.8, released 02 January 2024
<dl>
<dt>Bug fixes</dt>
<dd><ul>
    <li>An empty build number environment variable prevents logs from being committed to the logs branch.</li>
    <li>Setting a feature flag to <code>all</code> allowed content to go to the wrong location.</li>
    </ul></dd>
</dl>

## Version 1.1.7, released 01 December 2023

<dl>
<dt>Multiple commits per build are now used so that source files get processed faster</dt>
<dd>How the commit information is gathered has changed. Previously, there was a 1:1 matching of commits to Travis builds. Whatever the current commit ID was for the Travis build, that's what was used to compare against the last commit ID that the Markdown Enricher ran on. Now, the Markdown Enricher pulls source and gets the commit ID and related source files for the latest commit, allowing your changes to make it downstream with fewer builds. This change allows the Travis setting **Auto cancel branch builds** to be used and helps to alleviate problems with long queued Travis builds and wait times.</dd>

<dt>Rebuilds that rebuild the files you want rebuilt</dt>
<dd>Previously, if a build was kicked off but there were no new commits to process or Github was unaccessible, the Markdown Enricher exited. Now the build number, the previous commit ID, and the current commit ID are all stored in the last commit file in the logs branch rather than just the current commit ID. On rebuilds of already processed content, the build number can be found, then the compared commits from that build, and the same diff can be made to process those files again. In a Travis build, click the <b>Restart</b> button to try it out. With a rebuild, you might notice the landing page and sitemap dates update, but if no changes were found in a topic, the date in that topic is not updated downstream.</dd>

<dt>Changed supported values for <code>location_commit_summary_style</code></dt>
<dd>For <code>location_commit_summary_style</code> in locations files, revised acceptable values are <code>Author</code>, <code>AuthorAndSummary</code>, <code>BuildNumber</code>, <code>BuildNumberAndSummary</code>, <code>CommitID</code>, <code>CommitIDAndSummary</code>, <code>CommitIDAndAuthor</code>, and <code>Summary</code>.</dd>

<dt>Location names can be used as feature flag names</dt>
<dd>Location names can be used as feature flag names to allow content with the tag name to be delivered to multiple locations. For example, if you have <code>cli-draft</code> and <code>draft</code> as locations in your locations file, you can also set a feature flag name as <code>draft</code> with the value of <code>cli-draft,draft</code> to deliver upstream content tagged with <code>draft</code> to go to both of the downstream locations of <code>cli-draft</code> and <code>draft</code>.</dd>

<dt>Improved messaging when permissions are insufficient upstream</dt>
<dd>Instead of just exiting when an issue with permissions exists, a few workarounds have been added. If the Github user ID does not have write access in the upstream source repo, a warning is issued that logs cannot be stored. If a diff cannot be done on the changed files, all of the files are processed.</dd>
</dl>

## Version 1.1.6, released 01 November 2023
<dl>
<dt>Bug fix</dt>
<dd><ul>
    <li>Typo in the documentation</li>
    </ul>
</dd>
</dl>

## Version 1.1.5, released 02 October 2023
<dl>
<dt>Bug fixes</dt>
<dd><ul>
    <li>For branches that already existed, a 422 error occurred when creating pull requests.</li>
    <li>New branches weren't pushed up to the remote repo.</li>
    <li>Copyright date was not updating if it was the only change to the file.</li>
    </ul>
</dd>
</dl>

## Version 1.1.4, released 01 September 2023
<dl>
<dt>Bug fix: Deletions not occurring downstream</dt>
<dd>When deleting a file upstream, the file was not also deleted from the downstream locations.</dd>
</dl>

## Version 1.1.3, released 07 August 2023
<dl>
<dt>Bug fix: Images not being copied downstream</dt>
<dd>Fixed a missing copy command after verifying that the image does exist.</dd>
<dt>Added debugging</dt>
<dd>Added debugging logs to understand why a file might be ignored and not get processed.</dd>
</dl>

## Version 1.1.2, released 06 July 2023

<dl>
<dt>Removed empty lines from downstream <code>toc.yaml</code> files</dt>
<dd>To prevent <code>marked-it</code> transformation errors, lines that only contain newlines (<code>\n</code>) or spaces were removed from downstream <code>toc.yaml</code> files.</dd>
</dl>

## Version 1.1.1, released 01 June 2023

<dl>
<dt><a href="https://nvd.nist.gov/vuln/detail/CVE-2023-32681">CVE-2023-32681</a></dt>
    <dd>Updated <code>requests</code> to minimum version 2.31.0 in the <code>requirements.txt</code>.</dd>
<dt>Removed handling of files that are stored in the <code>.github</code> folder</dt>
    <dd>Any changes made to issue templates or files in the <code>.github</code> kick off builds, but are not processed or included in downstream content.</dd>
<dt>Bug fixes</dt>
    <dd><ul><li>Fixed Travis build URL in Slack posts.</li><li>When no downstream branch is created yet, and the branch is created from the default branch, the build failed when a pull request could not be created to the same branch that changes were pushed to.</li><li>When the downstream branch is created from the default branch, the <code>.travis.yml</code> is included. A secondary build is kicked off, which could be what the user wants if there are other tasks run, but it might not be. The build was not exiting because the upstream repo and branch matched the downstream repo and branch. </li><li>When the upstream repo and branch is the same as the downstream repo and branch, changed warning issued to error.</li></ul></dd>
</dl>

## Version 1.1.0, released 01 May 2023

<dl>
<dt>Added --rebuild_files flag</dt>
    <dd>Use the <code>--rebuild_files</code> flag to force a rebuild of a comma-separated list of files in addition to the changes that kicked off the build. This flag is helpful for forcing a rebuild of something like a landing page so that the date updates even though the content itself does not change often.</dd>
</dl>

## Version 1.0.3, released 03 April 2023

<dl>
<dt>Added file handling for commits with over 300 files</dt>
    <dd>Added Git CLI handling for commits that include over 300 files, since files alphabetically over 300 are not included in the response from the Git API.</dd>
<dt>Bug fix: File deletion issue</dt>
    <dd>Files deleted from upstream repository were not deleted from downstream repositories.</dd>
<dt>Bug fix: Traceback error displayed on JSON errors in locations file</dt>
    <dd>When the locations file contained JSON errors, the validation step led into the build exit step, but not enough information had been collected yet to exit successfully. </dd>
<dt>Bug fix: Broken image links from reused files</dt>
    <dd>In marked-it, when a file was reused and resolved in the sitemap, during link checking, image files referenced in the reused files were not found.</dd>
</dl>

## Version 1.0.2, released 01 March 2023

<dl>  
  <dt>Added <code>--cleanup_flags_and_content</code> and <code>--cleanup_flags_not_content</code> options</dt>
  <dd>Use the <a href="docs/feature-flags.md#Cleaning-up-outdated-feature-flags"><code>--cleanup_flags_and_content</code> and <code>--cleanup_flags_not_content</code></a> options with the start command to remove feature flags and, optionally, the content within the flags from a local clone of source files.</dd>
  <dt>Added marked-it keyref validation for in-repo keyref.yaml files</dt>
  <dd>Validates that marked-it keyrefs in the style of <code>{{site.data.keyword.&lt;keyword&gt;}}</code> start and end with two curly braces. The keyword used is also validated in the <code>keyref.yaml</code> file.</dd>
  <dt>Bug fix: Missing images in Markdown Enricher documentation</dt>
  <dd>Related to images being stored in places other than the <code>images</code> directory in the root of the repository.</dd>
  <dt>Bug fix: Clone error</dt>
  <dd>Added an exit when a clone fails for a downstream location.</dd>
  
</dl>

## Version 1.0.1, released 01 February 2023

<dl>
  <dt>Added sitemap handling for new marked-it reuse methods</dt>
  <dd>Handling includes <a href="https://ibm.github.io/marked-it/#/keyrefs">keyrefs</a>, <a href="https://ibm.github.io/marked-it/#/includes?id=referencing-a-segment-file">segments</a>, <a href="https://ibm.github.io/marked-it/#/includes?id=reusing-chunks-of-a-topic">section reuse</a>, and <a href="https://ibm.github.io/marked-it/#/includes?id=reusing-entire-files">topic reuse</a>.</dd>
  <dt>Bug fix: Images not pushed downstream</dt>
  <dd>Images that were uploaded to the <code>/images</code> directory in the source repo and that were referenced in a markdown file were not being pushed to downstream repos.</dd>
</dl>

##  Version 1.0.0, released 14 December 2022

Initial release


