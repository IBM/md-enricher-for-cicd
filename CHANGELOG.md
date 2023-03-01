# Change log

Notable changes to this project are documented in this file.


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


