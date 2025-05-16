"""
Main module for enriching BibTeX entries with abstracts.
"""
from typing import Optional, Dict, List
import logging
from pathlib import Path
import requests_cache
from tqdm import tqdm

from .bibio import BibIO
from .crossref_api import CrossrefAPI
from .semantic_scholar_api import SemanticScholarAPI
from .pubmed_api import PubMedAPI
from .elsevier_api import ElsevierAPI

logger = logging.getLogger(__name__)

class BibTeXEnricher:
    def __init__(self, 
                 crossref_email: Optional[str] = None,
                 semantic_scholar_key: Optional[str] = None,
                 pubmed_email: Optional[str] = None,
                 pubmed_api_key: Optional[str] = None,
                 elsevier_api_key: Optional[str] = None,
                 cache_path: Optional[str] = None):
        """
        Initialize the BibTeX enricher.
        
        Args:
            crossref_email: Optional email for Crossref polite pool
            semantic_scholar_key: Optional API key for Semantic Scholar
            pubmed_email: Optional email for PubMed API
            pubmed_api_key: Optional API key for PubMed
            elsevier_api_key: Optional API key for Elsevier
            cache_path: Optional path to cache API responses
        """
        self.crossref = CrossrefAPI(email=crossref_email)
        self.semantic_scholar = SemanticScholarAPI(api_key=semantic_scholar_key)
        self.pubmed = PubMedAPI(email=pubmed_email, api_key=pubmed_api_key) if pubmed_email else None
        self.elsevier = ElsevierAPI(api_key=elsevier_api_key) if elsevier_api_key else None
        
        if cache_path:
            requests_cache.install_cache(cache_path)
    
    def enrich_entry(self, 
                     entry: Dict[str, str], 
                     use_semantic_scholar: bool = True,
                     use_pubmed: bool = True,
                     use_elsevier: bool = True,
                     dry_run: bool = False) -> Dict[str, str]:
        """
        Enrich a single BibTeX entry with abstract.
        
        Args:
            entry: BibTeX entry dictionary
            use_semantic_scholar: Whether to try Semantic Scholar as fallback
            use_pubmed: Whether to try PubMed as another source
            use_elsevier: Whether to try Elsevier API
            dry_run: If True, only simulate the enrichment
            
        Returns:
            Enriched entry dictionary
        """
        entry_id = BibIO.get_entry_identifier(entry)
        
        if dry_run:
            logger.info(f"Would process entry: {entry_id}")
            return entry
            
        if 'abstract' in entry and entry['abstract']:
            logger.info(f"Entry already has abstract: {entry_id}")
            return entry

        logger.info(f"Processing entry: {entry_id}")

        # Try to get DOI from Crossref title search first if no DOI present
        doi = entry.get('doi')
        if not doi and 'title' in entry:
            logger.info(f"No DOI found, searching Crossref by title: {entry['title'][:50]}...")
            crossref_data = self.crossref.search_by_title(entry['title'])
            if crossref_data and 'DOI' in crossref_data:
                doi = crossref_data['DOI']
                logger.info(f"Found DOI from title search: {doi}")
                entry['doi'] = doi  # Add DOI to entry
        
        # 1. Try Elsevier first (if we have API key)
        if use_elsevier and self.elsevier:
            logger.info("Trying Elsevier API...")
            # Try DOI first
            if doi:
                logger.info(f"Searching Elsevier by DOI: {doi}")
                elsevier_data = self.elsevier.get_by_doi(doi)
                if elsevier_data:
                    abstract = self.elsevier.get_abstract(elsevier_data)
                    if abstract:
                        logger.info("Found abstract from Elsevier (DOI)")
                        entry['abstract'] = abstract
                        return entry
            
            # Try title search
            if 'title' in entry:
                logger.info(f"Searching Elsevier by title: {entry['title'][:50]}...")
                elsevier_data = self.elsevier.search_by_title(entry['title'])
                if elsevier_data:
                    abstract = self.elsevier.get_abstract(elsevier_data)
                    if abstract:
                        logger.info("Found abstract from Elsevier (title)")
                        entry['abstract'] = abstract
                        return entry
        
        # 2. Try PubMed second
        if use_pubmed and self.pubmed:
            logger.info("Trying PubMed API...")
            # Try PMID if available
            if 'pmid' in entry:
                logger.info(f"Searching PubMed by PMID: {entry['pmid']}")
                pubmed_data = self.pubmed.get_by_pmid(entry['pmid'])
                if pubmed_data:
                    abstract = self.pubmed.get_abstract(pubmed_data)
                    if abstract:
                        logger.info("Found abstract from PubMed (PMID)")
                        entry['abstract'] = abstract
                        return entry
            
            # Try title search
            if 'title' in entry:
                logger.info(f"Searching PubMed by title: {entry['title'][:50]}...")
                pubmed_data = self.pubmed.search_by_title(entry['title'])
                if pubmed_data:
                    abstract = self.pubmed.get_abstract(pubmed_data)
                    if abstract:
                        logger.info("Found abstract from PubMed (title)")
                        entry['abstract'] = abstract
                        return entry
        
        # 3. Try Crossref third
        logger.info("Trying Crossref API...")
        if doi:
            logger.info(f"Searching Crossref by DOI: {doi}")
            crossref_data = self.crossref.get_by_doi(doi)
            if crossref_data:
                abstract = self.crossref.get_abstract(crossref_data)
                if abstract:
                    logger.info("Found abstract from Crossref (DOI)")
                    entry['abstract'] = abstract
                    return entry
        
        if 'title' in entry:
            logger.info(f"Searching Crossref by title: {entry['title'][:50]}...")
            crossref_data = self.crossref.search_by_title(entry['title'])
            if crossref_data:
                abstract = self.crossref.get_abstract(crossref_data)
                if abstract:
                    logger.info("Found abstract from Crossref (title)")
                    entry['abstract'] = abstract
                    return entry
        
        # 4. Try Semantic Scholar as last resort
        if use_semantic_scholar:
            logger.info("Trying Semantic Scholar API...")
            # Try DOI
            if doi:
                logger.info(f"Searching Semantic Scholar by DOI: {doi}")
                ss_data = self.semantic_scholar.get_by_doi(doi)
                if ss_data:
                    abstract = self.semantic_scholar.get_abstract(ss_data)
                    if abstract:
                        logger.info("Found abstract from Semantic Scholar (DOI)")
                        entry['abstract'] = abstract
                        return entry
            
            # Try title search
            if 'title' in entry:
                logger.info(f"Searching Semantic Scholar by title: {entry['title'][:50]}...")
                ss_data = self.semantic_scholar.search_by_title(entry['title'])
                if ss_data:
                    abstract = self.semantic_scholar.get_abstract(ss_data)
                    if abstract:
                        logger.info("Found abstract from Semantic Scholar (title)")
                        entry['abstract'] = abstract
                        return entry
        
        logger.warning(f"Could not find abstract for: {entry_id}")
        return entry
    
    def enrich_file(self,
                    input_path: str,
                    output_path: str,
                    use_semantic_scholar: bool = True,
                    use_pubmed: bool = True,
                    use_elsevier: bool = True,
                    dry_run: bool = False) -> Dict[str, int]:
        """
        Enrich all entries in a BibTeX file with abstracts.
        
        Args:
            input_path: Path to input .bib file
            output_path: Path to save enriched .bib file
            use_semantic_scholar: Whether to try Semantic Scholar as fallback
            use_pubmed: Whether to try PubMed as another source
            use_elsevier: Whether to try Elsevier API
            dry_run: If True, only simulate the enrichment
            
        Returns:
            Dictionary with statistics about the enrichment process
        """
        stats = {
            'total': 0,
            'enriched': 0,
            'failed': 0,
            'already_had_abstract': 0
        }
        
        # Load input file
        logger.info(f"Loading BibTeX file: {input_path}")
        bib_db = BibIO.load_bibtex(input_path)
        stats['total'] = len(bib_db.entries)
        logger.info(f"Found {stats['total']} entries to process")
        
        # Process each entry
        for i, entry in enumerate(bib_db.entries, 1):
            logger.info(f"\nProcessing entry {i} of {stats['total']}")
            had_abstract = 'abstract' in entry and entry['abstract']
            
            enriched_entry = self.enrich_entry(
                entry,
                use_semantic_scholar=use_semantic_scholar,
                use_pubmed=use_pubmed,
                use_elsevier=use_elsevier,
                dry_run=dry_run
            )
            
            if had_abstract:
                stats['already_had_abstract'] += 1
            elif 'abstract' in enriched_entry and enriched_entry['abstract']:
                stats['enriched'] += 1
            else:
                stats['failed'] += 1
                
            # Log progress
            logger.info(f"Progress: {i}/{stats['total']} entries processed")
            logger.info(f"Stats so far: {stats['enriched']} enriched, {stats['failed']} failed, {stats['already_had_abstract']} already had abstracts")
        
        # Save enriched file
        if not dry_run:
            logger.info(f"Saving enriched BibTeX file to: {output_path}")
            BibIO.save_bibtex(bib_db, output_path)
        
        logger.info("\nEnrichment complete!")
        logger.info(f"Final stats: {stats['total']} total entries")
        logger.info(f"           {stats['enriched']} entries enriched")
        logger.info(f"           {stats['failed']} entries failed")
        logger.info(f"           {stats['already_had_abstract']} entries already had abstracts")
        
        return stats 