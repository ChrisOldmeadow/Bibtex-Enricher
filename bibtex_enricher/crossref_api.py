"""
Crossref API client for retrieving publication metadata.
"""
import requests
from typing import Dict, Optional
import time
import logging
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class CrossrefAPI:
    BASE_URL = "https://api.crossref.org/works"
    
    def __init__(self, email: Optional[str] = None):
        """
        Initialize Crossref API client.
        
        Args:
            email: Optional email for polite pool
        """
        self.session = requests.Session()
        headers = {'User-Agent': f'BibtexEnricher (mailto:{email})' if email else 'BibtexEnricher'}
        self.session.headers.update(headers)
    
    def get_by_doi(self, doi: str) -> Optional[Dict]:
        """
        Retrieve publication metadata by DOI.
        
        Args:
            doi: DOI string
            
        Returns:
            Dictionary of metadata if found, None otherwise
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/{doi}")
            response.raise_for_status()
            return response.json()['message']
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching DOI {doi}: {str(e)}")
            return None
    
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
            
            params = {
                'query.title': search_title,
                'rows': 5,  # Get more results to find best match
                'select': 'DOI,title,abstract'
            }
            
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    response = self.session.get(self.BASE_URL, params=params)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            
            results = response.json()['message']['items']
            if not results:
                return None
            
            # Find best matching result
            best_match = None
            best_similarity = 0
            
            for result in results:
                if 'title' not in result or not result['title']:
                    continue
                    
                # Crossref returns title as a list
                result_title = result['title'][0] if isinstance(result['title'], list) else result['title']
                similarity = self.title_similarity(title, result_title)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = result
            
            if best_similarity >= min_similarity:
                return best_match
            
            logger.debug(f"No results met minimum similarity threshold ({min_similarity}) for title: {title}")
            return None
            
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            logger.error(f"Error searching for title '{title}': {str(e)}")
            return None
    
    def get_abstract(self, entry: Dict) -> Optional[str]:
        """
        Extract abstract from Crossref metadata.
        
        Args:
            entry: Crossref metadata dictionary
            
        Returns:
            Abstract text if found, None otherwise
        """
        if 'abstract' in entry:
            return entry['abstract']
        return None 