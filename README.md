[![Python Code Checker](https://github.com/natelandau/filemanager/actions/workflows/python-code-checker.yml/badge.svg)](https://github.com/natelandau/filemanager/actions/workflows/python-code-checker.yml) [![Current Release](https://github.com/natelandau/filemanager/actions/workflows/release-checker.yml/badge.svg)](https://github.com/natelandau/filemanager/actions/workflows/release-checker.yml) [![codecov](https://codecov.io/gh/natelandau/filemanager/branch/main/graph/badge.svg?token=Y11Z883PMI)](https://codecov.io/gh/natelandau/filemanager)

# filemanager

A script to normalize filenames and (optionally) organize files into directories following the [Johnny Decimal](https://johnnydecimal.com) system.

`filemanager` normalizes filenames based on your preferences.

-   Remove special characters
-   Trim multiple separators (`word----word` becomes `word-word`)
-   Normalize to `lowercase`, `uppercase`, or `titlecase`
-   Normalize to a common word separator (`_`, `-`, ` `)
-   Replace all `.jpeg` extensions to `.jpg`
-   Remove common stopwords
-   Parse the filename for a date in many different formats
-   Remove or reformat the date and add it to the the beginning of the filename
-   Avoid overwriting files by adding a unique integer when renaming/moving
-   Clean entire directory trees
-   Shows previews of changes to be made before commiting
-   Ignore files listed in config
-   Specify casing for words which should never be changed
-   more...

`filemanager` can organize your files into folders.

-   Move files into directory trees following the [Johnny Decimal](https://johnnydecimal.com) system
-   Parse files and folder names looking for matching terms
-   Uses [nltk](https://www.nltk.org) to lookup synonyms to improve matching
-   Add `.filemanager` files to directories containing a list of words that will match files

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

`Filemanager` is created to solve for these problems by providing an easy CLI to normalize the filename and organize it into an appropriate directory on your computer.

## Install

Pip

```bash
pip install git+https://github.com/natelandau/filemanager
```

[PIPX](https://pypa.github.io/pipx/)

```bash
pipx install git+https://github.com/natelandau/filemanager
```

## Usage

Run `filemanager --help` for usage

### Configuration

`filemanager` will clean filenames without needing a configuration file. To organize files into folders, a valid [toml](https://toml.io/en/) configuration file is required at `~/.filemanager/filemanager.toml`

```toml
ignored_files = ['.DS_Store', '.bashrc', 'something_not_to_rename'] # If cleaning an entire directory, files in this list will be skipped
match_case = ["OKR", "OKRs", "KPI", "KPIs"]  # Force the casing of certain words. Great for acronyms or proper nouns.

[projects]                      # Define any number of different projects

[projects.jd_folder]            # A Johnny Decimal project
name = "test"                   # (Required)  Name of this project (used as a command line option --organize=test)
path = "~/johnnydecimal"        # (Required) Path to the folder containing the Johnny Decimal project
stopwords = ["stopword", "stopword"]   # Optional list of project specific stopwords

[projects.test2]
name = "test2"
path = "~/somedir/test2"

[projects.work]
name = "work"
path = "~/work-docs/"
```

### Examples

```bash
# Normalize all files in a directory to lowercase, with underscore separators
$ filemanager --case=lower --separator=underscore /path/to/directory

# Organize files into a specified Johnny Decimal folder and add a date
$ filemanager --organize=project --add-date --number=23.01 some_file.jpg

# Print a tree representation of a Johnny Decimal project
$ filemanager --organize=project --tree

# Organize files into a Johnny Decimal project with specified terms with title casing
$ filemanager --case=title --organize=project --term=term1 --term=term2 some_file.jpg

# Run in --dry_run mode to avoid making permanent changes on all files within two levels
$ filemanager --dry-run --diff --depth 2 /path/to/directory

# Run on a whole directory and filter out files that are already correct from the output
$ filemanager --filter-correct /path/to/directory

# Run on a whole directory and accept the first option for all prompts
$ filemanager --force /path/to/**directory**
```

### Tips

Adding custom functions to your `.bashrc` or `.zshrc` can save time and ensure your filename preferences are always used.

```bash
# ~/.bashrc
if command -v filemanager &>/dev/null; then

    cf() {
        # DESC:	 Clean filenames using the filemanager package
        if [[ $1 == "--help" || $1 == "-h" ]]; then
            filemanager --help
        else
            filemanager --sep=space --case=title "$@"
        fi
    }

    cfd() {
        # DESC:	 Clean filenames using the filemanager package
        if [[ $1 == "--help" || $1 == "-h" ]]; then
            filemanager --help
        else
            filemanager --add-date --sep=space --case=title "$@"
        fi
    }

    wfile() {
        # DESC:	 File work documents using the Johnny Decimal System and the filemanager package
        if [[ $1 == "--help" || $1 == "-h" ]]; then
            filemanager --help
        else
            filemanager --add-date --sep=underscore --case=lower --organize=work "$@"
        fi
    }

    pfile() {
        # DESC:	 File personal documents using the Johnny Decimal System and the filemanager package
        if [[ $1 == "--help" || $1 == "-h" ]]; then
            filemanager --help
        else
            filemanager --add-date --sep=space --case=title --organize=personal "$@"
        fi
    }
fi
```

## Caveats

`filemanager` is built for my own personal use. YMMV depending on your system and requirements. I make no warranties for any data loss that may result from use. I strongly recommend running in `--dry-run` mode prior to updating files.

# Contributing

Thank you for taking an interest in improving Filemanager.

## Setup: Once per project

There are two ways to contribute to this project.

### 1. Local development

1. Install Python 3.10 and [Poetry](https://python-poetry.org)
2. Clone this repository. `git clone https://github.com/natelandau/filemanager.git`
3. Install the Poetry environment with `poetry install`.
4. Activate your Poetry environment with `poetry shell`.
5. Install the pre-commit hooks with `pre-commit install --install-hooks`.

### 2. Containerized development

1. Clone this repository. `git clone https://github.com/natelandau/filemanager.git`
2. Open the repository in Visual Studio Code
3. Start the [Dev Container](https://code.visualstudio.com/docs/remote/containers). Run <kbd>Ctrl/⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> → _Remote-Containers: Reopen in Container_.

## Developing

-   This project follows the [Conventional Commits](https://www.conventionalcommits.org/) standard to automate [Semantic Versioning](https://semver.org/) and [Keep A Changelog](https://keepachangelog.com/) with [Commitizen](https://github.com/commitizen-tools/commitizen).
    -   When you're ready to commit changes run `cz c`
-   Run `poe` from within the development environment to print a list of [Poe the Poet](https://github.com/nat-n/poethepoet) tasks available to run on this project. Common commands:
    -   `poe lint` runs all linters
    -   `poe test` runs all tests with Pytest
-   Run `poetry add {package}` from within the development environment to install a run time dependency and add it to `pyproject.toml` and `poetry.lock`.
-   Run `poetry remove {package}` from within the development environment to uninstall a run time dependency and remove it from `pyproject.toml` and `poetry.lock`.
-   Run `poetry update` from within the development environment to upgrade all dependencies to the latest versions allowed by `pyproject.toml`.
