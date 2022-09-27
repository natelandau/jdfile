## v0.4.5 (2022-09-27)

### Fix

- **clean**: do not strip separators from dates in YYYY-MM-DD at beginning of filename

## v0.4.4 (2022-09-26)

### Fix

- **organize**: fix for not showing relative path to target folder

## v0.4.3 (2022-09-25)

### Fix

- **organize**: show paths relative to project root

## v0.4.2 (2022-09-23)

### Fix

- **stopwords**: remove numbers from stopwords list
- **clean**: specify a date for a file with --date
- **organize**: fix display of progress bar when selecting multiple folders
- **stopwords**: make less restrictive
- **organize**: don't clean files without a matching folder

### Refactor

- simplify coutning files with changes
- refactor filenames and function locations

## v0.4.1 (2022-09-20)

### Fix

- **clean**: add progress bar
- **clean**: retain camelcase words specified in config file 'match_case'

## v0.4.0 (2022-09-19)

### Feat

- **cli**: add -split-words to split camelCase into separate words
- **cli**: add --filter-correct option
- add --depth option
- **clean**: matching casing for specified words
- display output in tables, allow iterating over multiple files

### Fix

- **logging**: add trace level logs
- break folder names into individual words
- **stopwords**: remove 'org', 'points', 'sr', and 'project'
- don't show diff if no changes
- don't ask for user input when no changes
- **clean**: ignore files named .filemanager

### Refactor

- **logging**: date matching to TRACE
- remove unnessary functions

## v0.3.0 (2022-09-12)

### Feat

- **organize**: file directly to a specified --number
- **organize**: add skip and abort to organize options

### Fix

- **organize**: correctly escape variable name
- correctly filter ignored files

## v0.2.0 (2022-09-11)

### Feat

- **organize**: confirm move if single folder found
- **organize**: print matching terms

### Fix

- **config**: remove non-standard config file locations
- fix error when no ignored_files specified

## v0.1.1 (2022-09-11)

### Refactor

- **organize**: refactor building project folder lists
- rename cabinets to projects

## v0.1.0 (2022-09-09)

### Feat

- **options**: Add `--version` flag to print version number and then exit
- Organize files into johnny decimal folders

## v0.0.2 (2022-09-04)

### Fix

- default to clean filenames

## v0.0.1 (2022-09-04)

### Fix

- don't overwrite files when names unchanged
- replace files
- initial clean command
