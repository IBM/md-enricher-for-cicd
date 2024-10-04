#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

from setuptools import setup

if __name__ == "__main__":
    setup(
    name='doctopus-markdown-enricher',
    python_requires='>3.8.0',
    version='1.2.7.6.20241004',
    description='Single source your markdown documentation.',
    author='Kristin Brown',
    author_email='kakronst@us.ibm.com',
    packages=['mdenricher', 'mdenricher.cleanupEachFile', 'mdenricher.conrefs', 'mdenricher.errorHandling', 'mdenricher.images', 'mdenricher.repos', 'mdenricher.setup', 'mdenricher.sitemap', 'mdenricher.sourceFileList', 'mdenricher.tags'],
    entry_points={
        "console_scripts": [
            "mdenricher=mdenricher.start:start"
        ]
    },
    install_requires=[
        'pytz>=2022.2.1',
        'PyYAML>=6.0',
        'requests>=2.32.2',
        'python-dotenv>=0.20.0',
        'jsonschema',
        'slack_sdk'
    ],
    project_urls={
    'Documentation': 'https://pages.github.ibm.com/IBM/md-enricher-for-cicd',
    'Source': 'https://github.ibm.com/IBM/md-enricher-for-cicd',
    'Issues': 'https://github.ibm.com/IBM/md-enricher-for-cicd/issues',
    }
)
