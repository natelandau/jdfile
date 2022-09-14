[![Test](https://github.com/natelandau/filemanager/actions/workflows/test.yml/badge.svg)](https://github.com/natelandau/filemanager/actions/workflows/test.yml)

# filemanager

A script to normalize filenames and organize files into directories.

## Summary

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

### Enter filemanager

`filemanager` normalizes filenames based on your preferences. It will:

-   Remove special characters
-   Trim multiple separators (`word----word` becomes `word-word`)
-   Normalize to `lowercase`, `uppercase`, or `titlecase`
-   Normalize to a common word separator (`_`, `-`, ` `)
-   Replace all `.jpeg` extensions to `.jpg`
-   Remove common stopwords
-   Parse the filename for a date in many different formats
-   Remove or reformat the date and add it the the beginning of the filename
-   Avoid overwriting files by adding a unique integer when renaming/moving
-   more...

`filemanager` can organize your files into folders.

-   File into directory trees following the [Johnny Decimal](https://johnnydecimal.com) system
-   Parse files and folder names looking for matching terms
-   Uses [nltk](https://www.nltk.org) to lookup synonyms to improve matching
-   Add `.filemanager` files to directories containing a list of words that will match files

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

[projects]                      # Define any number of different projects

[projects.jd]                   # A Johnny Decimal project
name = "test"                   # (Required)  Name of this project (used as a command line option --organize=test)
path = "~/johnnydecimal"        # (Required) Path to the folder containing the Johnny Decimal project
stopwords = ["stopword", "stopword"]   # List of stopwords to be cleaned from filenames within this project

[projects.test2]
name = "test2"
path = "~/somedir/test2"

[projects.work]
name = "work"
path = "~/work-docs/"
```

### Examples

```bash
$ filemanager --add-date --case=title "department 2023 budget 08232002.XLSX"
"department 2023 budget 08232002.XLSX" -> "2002-08-23 Department 2023 budget.xlsx"

$ filemanager --add-date --sep=space --date-format="%b, %Y" "Project_mockups(WIP)___sep92022.pdf"
"Project_mockups(WIP)___sep92022.pdf" -> "Sep, 2022 Project mockups WIP.pdf"

filemanager --organize=work --add-date --sep=underscore "John-Jane-meeting-notes.txt"
"John-Jane-meeting-notes.txt" -> "~/work/10-19 Notes/11 John/11.01 Meetings/2022-09-01_John_Jane_meeting_notes.txt"
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

## Contributing

### Setup: once per device

1. [Generate an SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) and [add the SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
1. Configure SSH to automatically load your SSH keys:
    ```sh
    cat << EOF >> ~/.ssh/config
    Host *
      AddKeysToAgent yes
      IgnoreUnknown UseKeychain
      UseKeychain yes
    EOF
    ```
1. [Install Docker Desktop](https://www.docker.com/get-started).
    - Enable _Use Docker Compose V2_ in Docker Desktop's preferences window.
    - _Linux only_:
        - [Configure Docker and Docker Compose to use the BuildKit build system](https://docs.docker.com/develop/develop-images/build_enhancements/#to-enable-buildkit-builds). On macOS and Windows, BuildKit is enabled by default in Docker Desktop.
        - Export your user's user id and group id so that [files created in the Dev Container are owned by your user](https://github.com/moby/moby/issues/3206):
            ```sh
            cat << EOF >> ~/.bashrc
            export UID=$(id --user)
            export GID=$(id --group)
            EOF
            ```
1. [Install VS Code](https://code.visualstudio.com/) and [VS Code's Remote-Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers). Alternatively, install [PyCharm](https://www.jetbrains.com/pycharm/download/).
    - _Optional:_ Install a [Nerd Font](https://www.nerdfonts.com/font-downloads) such as [FiraCode Nerd Font](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/FiraCode) with `brew tap homebrew/cask-fonts && brew install --cask font-fira-code-nerd-font` and [configure VS Code](https://github.com/tonsky/FiraCode/wiki/VS-Code-Instructions) or [configure PyCharm](https://github.com/tonsky/FiraCode/wiki/Intellij-products-instructions) to use `'FiraCode Nerd Font'`.

### Setup: once per project

#### Local development

1. Clone this repository.
2. Install the Poetry environment with `poetry install`.
3. Activate your Poetry environment with `poetry shell`.
4. Install the pre-commit hooks with `pre-commit install --install-hooks`.

#### Containerized development

1. Clone this repository.
2. Start a [Dev Container](https://code.visualstudio.com/docs/remote/containers) in your preferred development environment:
    - _VS Code_: open the cloned repository and run <kbd>Ctrl/⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> → _Remote-Containers: Reopen in Container_.
    - _PyCharm_: open the cloned repository and [configure Docker Compose as a remote interpreter](https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#docker-compose-remote).
    - _Terminal_: open the cloned repository and run `docker compose run --rm dev` to start an interactive Dev Container.

### Developing

-   Access an interactive terminal within the container from an external terminal application `docker compose exec -it dev /usr/bin/zsh`
-   Rebuild the `app` Docker image `docker compose build --no-cache app`
-   This project follows the [Conventional Commits](https://www.conventionalcommits.org/) standard to automate [Semantic Versioning](https://semver.org/) and [Keep A Changelog](https://keepachangelog.com/) with [Commitizen](https://github.com/commitizen-tools/commitizen).
-   Run `poe` from within the development environment to print a list of [Poe the Poet](https://github.com/nat-n/poethepoet) tasks available to run on this project.
-   Run `poetry add {package}` from within the development environment to install a run time dependency and add it to `pyproject.toml` and `poetry.lock`.
-   Run `poetry remove {package}` from within the development environment to uninstall a run time dependency and remove it from `pyproject.toml` and `poetry.lock`.
-   Run `poetry update` from within the development environment to upgrade all dependencies to the latest versions allowed by `pyproject.toml`.
-   Run `cz bump` to bump the package's version, update the `CHANGELOG.md`, and create a git tag.

```

```
