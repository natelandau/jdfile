[![PyPI version](https://badge.fury.io/py/jdfile.svg)](https://badge.fury.io/py/jdfile) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/jdfile) [![Python Code Checker](https://github.com/natelandau/jdfile/actions/workflows/automated-tests.yml/badge.svg)](https://github.com/natelandau/jdfile/actions/workflows/automated-tests.yml) [![codecov](https://codecov.io/gh/natelandau/jdfile/branch/main/graph/badge.svg?token=Y11Z883PMI)](https://codecov.io/gh/natelandau/jdfile)

# jdfile

`jdfile` cleans and normalizes filenames. In addition, if you have directories which follow the [Johnny Decimal](https://johnnydecimal.com), jdfile can move your files into the appropriate directory.

`jdfile` cleans filenames based on your preferences.

-   Remove special characters
-   Trim multiple separators (`word----word` becomes `word-word`)
-   Normalize to `lower case`, `upper case`, `sentence case`, or `title case`
-   Normalize all files to a common word separator (`_`, `-`, ` `)
-   Enforce lowercase file extensions
-   Remove common English stopwords
-   Split `camelCase` words into separate words (`camel Case`)
-   Parse the filename for a date in many different formats
-   Remove or reformat the date and add it to the the beginning of the filename
-   Avoid overwriting files by adding a unique integer when renaming/moving
-   Clean entire directory trees
-   Optionally, show previews of changes to be made before commiting
-   Ignore files listed in a config file by filename or by regex
-   Specify casing for words which should never be changed (ie. `iMac` will never be re-cased)

`jdfile` can organize your files into folders.

-   Move files into directory trees following the [Johnny Decimal](https://johnnydecimal.com) system
-   Parse files and folder names looking for matching terms
-   Uses [nltk](https://www.nltk.org) to lookup synonyms to improve matching
-   Add `.jdfile` files to directories containing a list of words that will match files

### Why build this?

It's nearly impossible to file away documents with normalized names when everyone has a different convention for naming files. On any given day, tons of files are attached to emails or sent via Slack by people who have their won way of naming files. For example:

-   `department 2023 financials and budget 08232002.xlsx`
-   `some contract Jan7 reviewed NOT FINAL (NL comments) v13.docx`
-   `John&Jane-meeting-notes.txt`
-   `Project_mockups(WIP)___sep92022.pdf`
-   `FIRSTNAMElastname Resume (#1) [companyname].PDF`
-   `code_to_review.js`

If you are a person who archives documents there are a number of problems with these files.

-   No self-evident way to organize them into folders
-   No common patterns to search for
-   Dates all over the place or nonexistent
-   No consistent casing
-   No consistent word separators
-   Special characters within text
-   I could go on and on...

Additionally, even if the filenames were normalized, filing documents manually is a pain.

`jdfile` is created to solve for these problems by providing an easy CLI to normalize the filename and organize it into an appropriate directory on your computer.

## Install

jdfile requires Python v3.10 or above

```bash
pip install pip install obsidian-metadata
```

## Usage

Run `jdfile --help` for usage

### Configuration

To organize files into folders, a valid [toml](https://toml.io/en/) configuration file is required at `~/.jdfile/jdfile.toml`

```toml
# The name of the project is used as a command line option.
# (e.g. --organize=project_name)
[project_name]
    # (Required) Path to the folder containing the Johnny Decimal project
    path = "~/johnnydecimal"

    # An optional date format. If specified, the date will be appended to the filename
    # See https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes for details on how to specify a date.
    date_format = "None"

    # Ignores dotfiles (files that start with a period) when cleaning a directory.  true or false
    ignore_dotfiles = true

    # Files in this list will be skipped.
    ignored_files = ['file1.txt', 'file2.txt']

    # File names matching this regex will be skipped.
    # IMPORTANT: You must double escape within the pattern
    ignored_regex = [".*\\.tar.gz$"]

    # Force the casing of certain words. Great for acronyms or proper nouns.
    match_case = ["CEO", "CEOs", "iMac", "iPhone"]

    # Overwrite existing files. true or false. If false, unique integers will be appended to the filename.
    overwrite_existing = false

    # Separator to use between words. Options: "ignore", "underscore", "space", "dash", "none"
    separator = "ignore"

    # Split CamelCase words into separate words. true or false
    split_words = false

    # Optional list of project specific stopwords to be stripped from filenames
    stopwords = ["stopword1", "stopword2"]

    # Strip stopwords from filenames. true or false
    strip_stopwords = true

    # Transform case of filenames.
    # Options: "lower", "upper", "title", "CamelCase", "sentence", "ignore",
    transform_case = "ignore"

    # Use the nltk wordnet corpus to find synonyms for words in filenames. true or false
    # Note, this will download a large corpus (~400mb) the first time it is run.
    use_synonyms = false
```

### Example usage

```bash
# Normalize all files in a directory to lowercase, with underscore separators
$ jdfile --case=lower --separator=underscore /path/to/directory

# Clean all files in a directory and confirm all changes before committing them
$ jdfile --clean /path/to/directory

# Strip common English stopwords from all files in a directory
$ jdfile --stopwords /path/to/directory

# Transform a date and add it to the filename
$ jdfile --date-format="%Y-%m-%d" ./somefile_march 3rd, 2022.txt

# Print a tree representation of a Johnny Decimal project
$ jdfile --project=[project_name] --tree

# Use the settings of a project in the config file to clean filenames without
# organizing them into folders
$ jdfile --project=[project_name] --no-organize path/to/some_file.jpg

# Organize files into a Johnny Decimal project with specified terms with title casing
$ jdfile ---project=[project_name] --term=term1 --term=term2 path/to/some_file.jpg
```

### Tips

Adding custom functions to your `.bashrc` or `.zshrc` can save time and ensure your filename preferences are always used.

```bash
# ~/.bashrc
if command -v jdfile &>/dev/null; then

    clean() {
        # DESC:	 Clean filenames using the jdfile package
        if [[ $1 == "--help" || $1 == "-h" ]]; then
            jdfile --help
        else
            jdfile --sep=space --case=title --confirm "$@"
        fi
    }

    wfile() {
        # DESC:	 File work documents
        if [[ $1 == "--help" || $1 == "-h" ]]; then
            jdfile --help
        else
            jdfile --project=work "$@"
        fi
    }
fi
```

## Caveats

`jdfile` is built for my own personal use. YMMV depending on your system and requirements. I make no warranties for any data loss that may result from use. I strongly recommend running in `--dry-run` mode prior to updating files.

## Contributing

### Setup: Once per project

There are two ways to contribute to this project.

#### 1. Local development

1. Install Python 3.10 and [Poetry](https://python-poetry.org)
2. Clone this repository. `git clone https://github.com/natelandau/jdfile.git`
3. Install the Poetry environment with `poetry install`.
4. Activate your Poetry environment with `poetry shell`.
5. Install the pre-commit hooks with `pre-commit install --install-hooks`.

#### 2. Containerized development

1. Clone this repository. `git clone https://github.com/natelandau/jdfile.git`
2. Open the repository in Visual Studio Code
3. Start the [Dev Container](https://code.visualstudio.com/docs/remote/containers). Run <kbd>Ctrl/⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> → _Remote-Containers: Reopen in Container_.
4. Run `poetry env info -p` to find the PATH to the Python interpreter if needed by VSCode.

### Developing

-   This project follows the [Conventional Commits](https://www.conventionalcommits.org/) standard to automate [Semantic Versioning](https://semver.org/) and [Keep A Changelog](https://keepachangelog.com/) with [Commitizen](https://github.com/commitizen-tools/commitizen).
    -   When you're ready to commit changes run `cz c`
-   Run `poe` from within the development environment to print a list of [Poe the Poet](https://github.com/nat-n/poethepoet) tasks available to run on this project. Common commands:
    -   `poe lint` runs all linters
    -   `poe test` runs all tests with Pytest
-   Run `poetry add {package}` from within the development environment to install a run time dependency and add it to `pyproject.toml` and `poetry.lock`.
-   Run `poetry remove {package}` from within the development environment to uninstall a run time dependency and remove it from `pyproject.toml` and `poetry.lock`.
-   Run `poetry update` from within the development environment to upgrade all dependencies to the latest versions allowed by `pyproject.toml`.
