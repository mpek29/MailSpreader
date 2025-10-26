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

| Command                                  | Description                                                                |
| ---------------------------------------- | -------------------------------------------------------------------------- |
| `list-industries-to-linkedin-url`        | Convert a list of industries into LinkedIn URLs                            |
| `linkedin-url-to-profil-json`            | Convert LinkedIn URLs into a JSON list of company profile URLs             |
| `profil-url-to-metadata-json`            | Convert company profile URLs into JSON metadata                            |
| `metadata-json-to-email-json-auto`       | Generate a JSON of emails from metadata JSON (automatic mode)              |
| `metadata-json-to-email-json-manual`     | Generate a JSON of emails from metadata JSON (manual/operator-assisted)    |
| `metadata-json-to-summaries-json`        | Generate a JSON of business summaries from metadata and config             |
| `summaries-json-en-to-fr`                | Translate summaries JSON from English to French                            |
| `metadata-email-json-to-spreadsheet`     | Merge metadata, email, and summaries JSON into a CSV spreadsheet           |

## Example Workflows

### Convert industries YAML into LinkedIn URLs

This repository includes a collection of `.yaml` files that contain various industries available as filters on LinkedIn. These files, referred to as "list of industries files," enable users to target specific industries for job applications. You can find these files in the following directory: `src/mail_spreader/templates/job/`.

To customize your experience, you have the option to create your own "list of industries" `.yaml` file to better suit your needs.

The following command converts a specified industries `.yaml` file into a corresponding LinkedIn search URL. The generated URL will be saved in a file named `urls.yaml`.

```bash
mail-spreader list-industries-to-linkedin-url .\templates\job\electronics_industries.yaml -o urls.yaml
```

This command processes the electronics_industries.yaml file and creates a LinkedIn search URL that targets the specified industries.

### Change the URL to your desired location

The URL generated previously does not include a location filter. To customize it, simply open the URL and add your desired location.

Next, you can add the updated URL along with your LinkedIn credentials to the `config.yaml` file, located in the following directory: `src/mail_spreader/templates`. For security reasons, consider creating a separate LinkedIn account to avoid potential bans.

**Important**: Ensure that the total number of pages in your LinkedIn search does not exceed 100 pages. If your search generates more than 100 pages, you will need to split the LinkedIn search URL into multiple URLs. One effective approach is to create separate URLs for each industry, location if possible, available job etc...

Once you have your URLs ready, you can add them to the `config.yaml` file in a YAML list format.

### Convert LinkedIn URLs into JSON

```bash
mail-spreader linkedin-url-to-profil-json .\templates\config.yaml -o profiles.json
```
Extracts each company's profile URL from the LinkedIn search results contained in `config.yaml` and saves them to the specified JSON file.

### Convert profiles JSON into metadata JSON

```bash
mail-spreader profil-url-to-metadata-json config.yaml profiles.json -o metadata.json
```
Extracts metadata from each company's LinkedIn profile URL — including company name, website, and company description.

### Split a large company dataset into multiple smaller JSON files

```bash
mail-spreader split-companies companies.json output_dir --chunk-size 50
```

> This command splits a JSON file containing  
> `{ company_names, company_websites, company_about_texts }`  
> into several synchronized JSON files, each containing a subset of the data.

### Extract emails automatically from metadata

```bash
mail-spreader metadata-json-to-email-json-auto metadata.json -o emails.json
```

### Extract emails manually with operator assistance

```bash
mail-spreader metadata-json-to-email-json-manual metadata.json -o emails.json
```

### Generate business summaries

```bash
mail-spreader metadata-json-to-summaries-json config.yaml metadata.json -o summaries.json
```

### Translate summaries from English to French

```bash
mail-spreader summaries-json-en-to-fr summaries.json -o summaries_fr.json
```

### Export all data into a spreadsheet

```bash
mail-spreader metadata-email-json-to-spreadsheet metadata.json emails.json summaries.json -o prospects.csv
```

## 🌟 License

This project is open-source. Feel free to use, modify, and contribute! 🚀
