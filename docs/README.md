<!--
# Copyright 2022, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
# Last updated: 2024-07-13
-->

# Markdown Enricher

Welcome to the Markdown Enricher! 

Markdown is a great authoring language for both readability and simplicity, but if you've used markdown for awhile, you know that it's not perfect. The larger your content set is, the harder it is to maintain. Enter the [Markdown Enricher](https://github.com/IBM/md-enricher-for-cicd)!


## What is it?
The Markdown Enricher is a pre-processing script that brings a few of the best features of more complex authoring methods to markdown and other text-based files. Manage one set of source files, run Markdown Enricher on those files, and get customized sets of output to use wherever you need them. Use the continuous integration and continuous delivery capabilities in the Markdown Enricher, or use other tools to pick up from there.

## Why would writers want to use the Markdown Enricher?
The [Markdown Enricher](https://github.com/IBM/md-enricher-for-cicd)'s best quality is that it helps writers get similar content to multiple places with some differences between them. Here are some other benefits.

* Single-sourced markdown content authoring and delivery
* Adaptable from simple to complex use cases
* While it was designed for markdown, you can define any text-based language to run on
* No more copying and pasting from one Git branch to another when must branches diverge and must stay diverged
* No Git CLI knowledge required
* No merge conflicts between downstream branches
* In editor feature flag control
* In editor content delivery control
* Single-sourced, customized, shared content between branches or repositories
* Set up automatic merges of the output to Github, auto-generated pull requests in Github, or set up your own tools to push the output to
* Custom content re-use (word, phrase, sentence, paragraph, section, or topic)
* Quicker overall delivery times by minimizing errors and repetitive tasks
* Pick up where another writer left off by using tags as a kind of progress indicators
* No impact to downstream automation such as HTML processors
* Quick one-time setup
* Detailed logs and optional Slack posts to troubleshoot issues
* Local transformation for testing or for pushing the output files to a content management system that is not Github


## Potential use cases

- Staging versus production content
- Internal versus external content
- Web versus PDF content
- Cloud versus on-prem content
- Docs for multiple tools that share some common features
- Metadata differences
- Link structure differences
- Reuse across files


## Use these tools in conjunction with the Markdown Enricher

The Markdown Enricher is designed to bring continuous integration and continuous delivery capabilities to the documentation solution you already have, rather than be a stand-alone documentation solution itself. The Markdown Enricher is not a static site generator, have a content management system, or a display framework like other tools, such as Hugo or Jekyll. The Markdown Enricher is great for taking simple solutions and making them more user-friendly for their content developers.

For example, the Markdown Enricher documentation is stored in Git, and then displayed using Github Pages and Docsify. No HTML transformation is necessary in this automation pipeline, but if your display framework does require HTML transformation, include a markdown to HTML processor pipeline.

|Tool|Why use it?|
|--|--|
|[Docsify](https://docsify.js.org/#/?id=docsify)|Site generator to display markdown in the Github Pages framework.|
|[Github Pages](https://pages.github.com/)|Site generator for markdown. |
|[markdown-to-jsx](https://www.npmjs.com/package/markdown-to-jsx)|Parsing engine.|
|[marked-it](https://ibm.github.io/marked-it)|Transform markdown into HTML.|
|[PyMdown](https://facelessuser.github.io/PyMdown/)|Transform markdown into HTML|





