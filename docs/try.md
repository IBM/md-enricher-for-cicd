

# Try it out!

Try out the Markdown Enricher with example markdown files.

1. Install [Python 3](https://www.python.org/downloads/).
1. Clone the [Markdown Enricher](https://github.com/IBM/md-enricher-for-cicd) repository.
1. In the cloned repository directory, review the contents of the `example` directory.
    - `locations.json`: The output locations (`staging` and `prod`) and the customizations for each one. Note that there isn't much required for pre-processing the files without delivering the output anywhere, just the names of the locations and that no action is required with the output. [Learn more](locations.md).
    - `feature-flags.json`: A configuration file that defines custom tags for marking up content to appear in the output for specific locations. [Learn more](feature-flags.md).
    - `reuse-snippets`: Files that can be referenced in content markdown files and reused as necessary. [Learn more](reuse.md).
    - Markdown files: Content files, which can be stored in subfolders.
1. Install the required modules.
    ```
    pip install -r <PATH>/md-enricher-for-cicd/requirements.txt
    ```
1. Run the start command. [Learn more about start command options](setup.md).
    ```
    python <PATH>/md-enricher-for-cicd/mdEnricherForCICD/start.py --source_dir <SOURCE_FILES_DIRECTORY> --output_dir <OUTPUT_FILES_DIRECTORY> --locations_file <PATH>/locations.json
    ```

    Example:
    ```
    python <PATH>/md-enricher-for-cicd/mdEnricherForCICD/start.py --source_dir <PATH>/md-enricher-for-cicd/example --output_dir <PATH>/md-enricher-for-cicd/example-output --locations_file <PATH>/md-enricher-for-cicd/example/locations.json
    ```
1. Navigate to the output directory and review the output files. Notice how content that had location-specific tags around it only displays in the output for that location.




