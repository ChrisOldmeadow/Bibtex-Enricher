#!/usr/bin/env python3
"""
Command-line interface for BibTeX enricher.
"""
import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

from bibtex_enricher.enrich import BibTeXEnricher

def setup_logging(verbose: bool):
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="Enrich BibTeX files with abstracts from Crossref, Semantic Scholar, PubMed, and Elsevier"
    )
    
    parser.add_argument(
        "input_file",
        type=str,
        help="Input .bib file path"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output .bib file path (default: input_with_abstracts.bib)",
    )
    
    parser.add_argument(
        "--no-semantic-scholar",
        action="store_true",
        help="Disable Semantic Scholar fallback"
    )
    
    parser.add_argument(
        "--no-pubmed",
        action="store_true",
        help="Disable PubMed as a source"
    )
    
    parser.add_argument(
        "--no-elsevier",
        action="store_true",
        help="Disable Elsevier as a source"
    )
    
    parser.add_argument(
        "--crossref-email",
        type=str,
        help="Email for Crossref polite pool (default: from CROSSREF_EMAIL env var)"
    )
    
    parser.add_argument(
        "--semantic-scholar-key",
        type=str,
        help="API key for Semantic Scholar (default: from SEMANTIC_SCHOLAR_KEY env var)"
    )
    
    parser.add_argument(
        "--pubmed-email",
        type=str,
        help="Email for PubMed API (default: from PUBMED_EMAIL env var)"
    )
    
    parser.add_argument(
        "--pubmed-api-key",
        type=str,
        help="API key for PubMed (default: from PUBMED_API_KEY env var)"
    )
    
    parser.add_argument(
        "--elsevier-api-key",
        type=str,
        help="API key for Elsevier (default: from ELSEVIER_API_KEY env var)"
    )
    
    parser.add_argument(
        "--cache-dir",
        type=str,
        help="Directory to cache API responses"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate enrichment without making changes"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        logging.error(f"Input file not found: {input_path}")
        sys.exit(1)
    
    # Set default output path if not specified
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_with_abstracts.bib"
    
    # Setup cache
    cache_path = Path(args.cache_dir) / "api_cache" if args.cache_dir else None
    
    # Get API credentials from environment variables if not provided as arguments
    crossref_email = args.crossref_email or os.getenv('CROSSREF_EMAIL')
    semantic_scholar_key = args.semantic_scholar_key or os.getenv('SEMANTIC_SCHOLAR_KEY')
    pubmed_email = args.pubmed_email or os.getenv('PUBMED_EMAIL')
    pubmed_api_key = args.pubmed_api_key or os.getenv('PUBMED_API_KEY')
    elsevier_api_key = args.elsevier_api_key or os.getenv('ELSEVIER_API_KEY')
    
    # Initialize enricher
    enricher = BibTeXEnricher(
        crossref_email=crossref_email,
        semantic_scholar_key=semantic_scholar_key,
        pubmed_email=pubmed_email,
        pubmed_api_key=pubmed_api_key,
        elsevier_api_key=elsevier_api_key,
        cache_path=cache_path
    )
    
    # Process file
    try:
        stats = enricher.enrich_file(
            str(input_path),
            str(output_path),
            use_semantic_scholar=not args.no_semantic_scholar,
            use_pubmed=not args.no_pubmed,
            use_elsevier=not args.no_elsevier,
            dry_run=args.dry_run
        )
        
        # Print summary
        print("\nEnrichment Summary:")
        print(f"Total entries: {stats['total']}")
        print(f"Already had abstract: {stats['already_had_abstract']}")
        print(f"Successfully enriched: {stats['enriched']}")
        print(f"Failed to enrich: {stats['failed']}")
        
        if not args.dry_run:
            print(f"\nEnriched file saved to: {output_path}")
        
    except Exception as e:
        logging.error(f"Error enriching file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 