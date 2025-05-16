# BibTeX Enricher

A Python tool to enrich BibTeX files with abstracts from multiple academic APIs.

## 🌟 Features

- Automatically fetch abstracts for BibTeX entries
- Multiple data sources in order of priority:
  - Elsevier API (for Elsevier journals)
  - PubMed API (for biomedical literature)
  - Crossref API
  - Semantic Scholar API (fallback)
- Search by:
  - DOI (preferred)
  - PMID (for PubMed)
  - Title (fallback)
- Two interfaces:
  - Command-line tool
  - Web dashboard (Streamlit)
- API response caching for faster repeated lookups
- Real-time progress logging
- Text cleaning and sanitization
- Dry-run mode for testing
- Detailed progress and statistics

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/ChrisOldmeadow/bibtex-enricher.git
cd bibtex-enricher
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API credentials:
Create a `.env` file in the project root with your API credentials:
```
CROSSREF_EMAIL=your@email.com
SEMANTIC_SCHOLAR_KEY=your_semantic_scholar_key
PUBMED_EMAIL=your@email.com
PUBMED_API_KEY=your_pubmed_key
ELSEVIER_API_KEY=your_elsevier_key
```

## 📖 Usage

### Command Line Interface

Basic usage:
```bash
python cli.py input.bib
```

This will create `input_with_abstracts.bib` in the same directory.

Advanced options:
```bash
python cli.py input.bib \
  -o output.bib \
  --crossref-email your@email.com \
  --semantic-scholar-key YOUR_API_KEY \
  --pubmed-email your@email.com \
  --pubmed-api-key YOUR_PUBMED_KEY \
  --elsevier-api-key YOUR_ELSEVIER_KEY \
  --cache-dir cache \
  --dry-run \
  -v
```

Options:
- `-o, --output`: Output file path
- `--no-semantic-scholar`: Disable Semantic Scholar fallback
- `--no-pubmed`: Disable PubMed source
- `--no-elsevier`: Disable Elsevier source
- `--crossref-email`: Email for Crossref polite pool
- `--semantic-scholar-key`: API key for Semantic Scholar
- `--pubmed-email`: Email for PubMed API
- `--pubmed-api-key`: API key for PubMed
- `--elsevier-api-key`: API key for Elsevier
- `--cache-dir`: Directory to cache API responses
- `--dry-run`: Simulate enrichment without making changes
- `-v, --verbose`: Enable verbose logging

### Web Dashboard

Run the Streamlit app:
```bash
streamlit run app.py
```

Features:
1. Upload BibTeX file
2. Configure API credentials in sidebar:
   - Crossref email
   - Semantic Scholar API key
   - PubMed email and API key
   - Elsevier API key
3. Toggle data sources:
   - Enable/disable Semantic Scholar
   - Enable/disable PubMed
   - Enable/disable Elsevier
4. Enable/disable caching
5. View real-time progress logging
6. See enrichment statistics
7. Download enriched file

## 🔧 API Usage

You can also use the enricher programmatically:

```python
from bibtex_enricher.enrich import BibTeXEnricher

enricher = BibTeXEnricher(
    crossref_email="your@email.com",
    semantic_scholar_key="YOUR_API_KEY",
    pubmed_email="your@email.com",
    pubmed_api_key="YOUR_PUBMED_KEY",
    elsevier_api_key="YOUR_ELSEVIER_KEY",
    cache_path="cache"
)

stats = enricher.enrich_file(
    "input.bib",
    "output.bib",
    use_semantic_scholar=True,
    use_pubmed=True,
    use_elsevier=True,
    dry_run=False
)

print(f"Enriched {stats['enriched']} entries")
```

## 📝 Notes

- Using an email with Crossref puts you in their "polite pool" with higher rate limits
- Semantic Scholar API key is optional but recommended for higher rate limits
- PubMed email is required if using PubMed API
- Elsevier API key is required for accessing Elsevier content
- Caching significantly speeds up repeated lookups of the same entries
- The tool tries APIs in order: Elsevier → PubMed → Crossref → Semantic Scholar
- Text cleaning removes XML/HTML tags and normalizes formatting

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Elsevier API](https://dev.elsevier.com/)
- [PubMed API](https://www.ncbi.nlm.nih.gov/home/develop/api/)
- [Crossref API](https://api.crossref.org/)
- [Semantic Scholar API](https://api.semanticscholar.org/)
- [bibtexparser](https://bibtexparser.readthedocs.io/) 