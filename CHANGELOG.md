# Change log

Notable changes to this project are documented in this file.

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


