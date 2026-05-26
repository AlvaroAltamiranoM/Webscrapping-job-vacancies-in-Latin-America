# Web-scraping Job Vacancies in Latin America

A multi-country pipeline that scrapes online job postings across Latin America and converts unstructured ad text into harmonized, analysis-ready labor market data. The core contribution is the data infrastructure: collecting and standardizing high-frequency vacancy data at regional scale.

## Problem

Online job portals offer timely, granular signals on labor demand, but in Latin America they lack standardized occupational and sectoral classifications and use inconsistent formats across countries and sites. This project builds reusable tooling to collect that information at scale and harmonize it into a common relational structure suitable for cross-country analysis.

## Data

- ~3 million job postings scraped across 18 LAC countries, collected weekly from late 2019 to early 2022
- Country-level datasets with ~15 standardized variables each (title, description, economic activity, location, education, salary, contract type, dates, and others)
- Raw postings consolidated per country into a unified relational schema

## Method

**Scraping (the reusable core):** Two-stage Beautiful Soup scraper - first enumerating active listings, then parsing each individual ad - with weekly downloads stored as structured CSV per country.

**Harmonization:** NLP-based cleaning to reconcile inconsistent formats across portals: date standardization to ISO 8601, salary and numeric parsing, and dictionaries to normalize categorical fields (education, working hours, languages). This step turns heterogeneous raw ads into comparable variables.

**Downstream analysis (applied per country as needed):** The harmonized data supports occupation classification (TF-IDF plus cosine similarity against the ISCO standard) and skill-content clustering (K-means on skill n-grams). These were demonstrated in a Chile case study assessing how well online ads represent official labor market statistics.

## Use cases

- Constructing high-frequency labor demand indicators where official statistics lag
- Tracking skill-requirement shifts across occupations over time
- Validating online vacancy data against official surveys before using it for policy analysis

## Stack

`Python` | `BeautifulSoup` | `pandas` | `NLP` | `scikit-learn` | `TF-IDF / cosine similarity` | `K-means`

## Context

Developed for labor market research at the IDB and World Bank, applying online job-ad data to questions that standard household and firm surveys answer with delay.
