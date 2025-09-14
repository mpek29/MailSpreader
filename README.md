# MailSpreader

## 🚀 Overview

![Main Preview](assets/img/main.png)

**MailSpreader** is a Python command-line tool to automate LinkedIn-based mailings.
It collects company profiles, extracts metadata, finds emails, generates summaries, and exports data into a spreadsheet-ready format.

## Installation

Clone and install directly from GitHub:

```bash
pip install git+https://github.com/mpek29/MailSpreader
```

## Usage

```bash
mail-spreader [OPTIONS] COMMAND [ARGS]...
```

### Global Options

* `--install-completion` → Install shell completion for the current shell
* `--show-completion` → Show shell completion script
* `--help` → Show this message and exit

## Available Commands

| Command                              | Description                                                      |
| ------------------------------------ | ---------------------------------------------------------------- |
| `linkedin-url-to-profil-json`        | Convert LinkedIn URLs into a JSON list of company profile URLs   |
| `profil-url-to-metadata-json`        | Convert company profile URLs into JSON metadata                  |
| `metadata-json-to-email-json`        | Generate a JSON of emails from metadata JSON                     |
| `metadata-json-to-summaries-json`    | Generate a JSON of business summaries from metadata and emails   |
| `metadata-email-json-to-spreadsheet` | Merge metadata, email, and summaries JSON into a CSV spreadsheet |

## Example Workflows

### Convert LinkedIn URLs into JSON

```bash
mail-spreader linkedin-url-to-profil-json config.yaml -o profiles.json
```

### Convert profiles JSON into metadata JSON

```bash
mail-spreader profil-url-to-metadata-json config.yaml profiles.json -o metadata.json
```

### Extract emails from metadata

```bash
mail-spreader metadata-json-to-email-json metadata.json -o emails.json
```

### Generate business summaries

```bash
mail-spreader metadata-json-to-summaries-json config.yaml metadata.json emails.json -o summaries.json
```

### Export all data into a spreadsheet

```bash
mail-spreader metadata-email-json-to-spreadsheet metadata.json emails.json summaries.json -o prospects.csv
```


## 🌟 License

This project is open-source. Feel free to use, modify, and contribute! 🚀
