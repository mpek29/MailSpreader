# MailSpreader

## 🚀 Overview

![Main Preview](assets/img/main.png)

The **MailSpreader** is an open-source Python project that automates the creation of a structured spreadsheet used for targeted email campaigns via **Thunderbird**. It collects and processes company information from LinkedIn, extracts relevant details, and formats them into a mailing-ready table.

## 🎯 Highlights

| 💡 Feature                    | 📌 Description                                                    |
| ----------------------------- | ----------------------------------------------------------------- |
| 🎯 **Targeted Lead Scraping** | Collect LinkedIn profiles filtered by topic and location          |
| 🌐 **Smart Data Extraction**  | Get company websites and summaries from LinkedIn "About" sections |
| 📧 **Email Retrieval**        | Use Google to discover emails via domain-based queries            |
| ✍️ **Auto Summary Builder**   | Convert text into business blurbs: "specialized in..."            |
| 📁 **Mail-Ready Export**      | Generate Thunderbird-compatible spreadsheets                      |

## ⚙️ Workflow Overview

1. **Input Criteria**: Define target themes and locations.
2. **Profile Collection**: Scrape LinkedIn for matching companies.
3. **Data Extraction**: Retrieve website and "About" content from each profile.
4. **Email Retrieval**: Use Google queries to find contact emails tied to domain names.
5. **Summary Construction**: Parse and rephrase descriptions for clarity and consistency.
6. **Spreadsheet Generation**: Output all data in a tabular format ready for Thunderbird.

## 📊 Example Spreadsheet Format

| Company Name | Business Summary                          | Email                                             |
| ------------ | ----------------------------------------- | ------------------------------------------------- |
| Example Corp | Specialized in renewable energy solutions | [contact@example.com](mailto:contact@example.com) |
| TechSoft Ltd | Specialized in SaaS for retail management | [info@techsoft.io](mailto:info@techsoft.io)       |

## 📁 Project Structure

```
mailspreader/
├── data/                     # Input/output data files
│   └── prospect_list.xlsx
├── mailspreader/            # Core package
│   ├── linkedin_scraper.py  # Functions to scrape LinkedIn profiles
│   ├── website_parser.py    # Email extraction from websites
│   ├── summarizer.py        # Summary generation logic
│   └── exporter.py          # Spreadsheet generation
├── assets/                  # Images and media for documentation
│   └── img/
├── run.sh                   # Shell script to run the main program
├── .gitignore
├── LICENSE
├── README.md
└── main.py                  # Entry-point script
```

## 🌟 License

This project is open-source. Feel free to use, modify, and contribute! 🚀
