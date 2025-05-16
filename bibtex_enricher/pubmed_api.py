"""
PubMed API client for retrieving publication metadata using BioPython's Entrez.
"""
from typing import Dict, Optional, List
import logging
from Bio import Entrez
from difflib import SequenceMatcher
import re
import time

logger = logging.getLogger(__name__)

class PubMedAPI:
    def __init__(self, email: str, api_key: Optional[str] = None):
        """
        Initialize PubMed API client.
        
        Args:
            email: Required email for NCBI Entrez
            api_key: Optional NCBI API key for higher rate limits
        """
        if not email:
            raise ValueError("Email is required for PubMed API")
            
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key
            
    def clean_title(self, title: str) -> str:
        """
        Clean and normalize a title for searching.
        
        Args:
            title: Original title
            
        Returns:
            Cleaned title
        """
        # Remove special characters and extra whitespace
        title = re.sub(r'[^\w\s-]', ' ', title)
        title = ' '.join(title.split())
        return title.lower()

    def title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate similarity ratio between two titles.
        
        Args:
            title1: First title
            title2: Second title
            
        Returns:
            Similarity ratio between 0 and 1
        """
        return SequenceMatcher(None, 
                             self.clean_title(title1),
                             self.clean_title(title2)).ratio()
    
    def get_by_pmid(self, pmid: str) -> Optional[Dict]:
        """
        Retrieve publication metadata by PubMed ID.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary of metadata if found, None otherwise
        """
        try:
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="xml")
                    records = Entrez.read(handle)
                    if records['PubmedArticle']:
                        return records['PubmedArticle'][0]
                    return None
                except Exception as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    
        except Exception as e:
            logger.error(f"Error fetching PMID {pmid} from PubMed: {str(e)}")
            return None
    
    def search_by_title(self, title: str, min_similarity: float = 0.85) -> Optional[Dict]:
        """
        Search for publication by title.
        
        Args:
            title: Publication title
            min_similarity: Minimum similarity ratio to consider a match
            
        Returns:
            Best matching result if found, None otherwise
        """
        try:
            # Clean title for search
            search_title = self.clean_title(title)
            
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    # First search for PMIDs
                    search_handle = Entrez.esearch(db="pubmed", term=f"{search_title}[Title]", retmax=5)
                    search_results = Entrez.read(search_handle)
                    
                    if not search_results['IdList']:
                        return None
                        
                    # Fetch full records for the PMIDs
                    fetch_handle = Entrez.efetch(db="pubmed", id=search_results['IdList'], rettype="xml", retmode="xml")
                    records = Entrez.read(fetch_handle)
                    
                    # Find best matching result
                    best_match = None
                    best_similarity = 0
                    
                    for article in records['PubmedArticle']:
                        article_title = article['MedlineCitation']['Article']['ArticleTitle']
                        similarity = self.title_similarity(title, article_title)
                        
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = article
                    
                    if best_similarity >= min_similarity:
                        return best_match
                        
                    logger.debug(f"No results met minimum similarity threshold ({min_similarity}) for title: {title}")
                    return None
                    
                except Exception as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            
        except Exception as e:
            logger.error(f"Error searching for title '{title}' on PubMed: {str(e)}")
            return None
    
    def get_abstract(self, entry: Dict) -> Optional[str]:
        """
        Extract abstract from PubMed metadata.
        
        Args:
            entry: PubMed metadata dictionary
            
        Returns:
            Abstract text if found, None otherwise
        """
        try:
            article = entry['MedlineCitation']['Article']
            if 'Abstract' in article:
                return article['Abstract']['AbstractText'][0]
            return None
        except (KeyError, IndexError):
            return None 