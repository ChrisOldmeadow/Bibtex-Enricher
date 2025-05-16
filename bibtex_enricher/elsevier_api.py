"""
Elsevier API client for retrieving publication metadata.
"""
from typing import Dict, Optional, List
import logging
import requests
from difflib import SequenceMatcher
import re
import time

logger = logging.getLogger(__name__)

class ElsevierAPI:
    def __init__(self, api_key: str):
        """
        Initialize Elsevier API client.
        
        Args:
            api_key: Required Elsevier API key
        """
        if not api_key:
            raise ValueError("API key is required for Elsevier API")
            
        self.session = requests.Session()
        self.session.headers.update({
            'X-ELS-APIKey': api_key,
            'Accept': 'application/json'
        })
    
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
    
    def get_by_doi(self, doi: str) -> Optional[Dict]:
        """
        Retrieve publication metadata by DOI using Elsevier's Abstract Retrieval API.
        
        Args:
            doi: DOI string
            
        Returns:
            Dictionary of metadata if found, None otherwise
        """
        try:
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    # Use Abstract Retrieval API
                    response = self.session.get(
                        f"https://api.elsevier.com/content/abstract/doi/{doi}",
                        params={'view': 'FULL'}  # Get full text view including abstract
                    )
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching DOI {doi} from Elsevier: {str(e)}")
            return None
    
    def search_by_title(self, title: str, min_similarity: float = 0.85) -> Optional[Dict]:
        """
        Search for publication by title using Elsevier's Search API.
        
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
                    # Use Scopus Search API
                    response = self.session.get(
                        "https://api.elsevier.com/content/search/scopus",
                        params={
                            'query': f'title("{title}")',
                            'field': 'doi,title,abstract',
                            'count': 5
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'search-results' not in data or 'entry' not in data['search-results']:
                        return None
                    
                    # Find best matching result
                    best_match = None
                    best_similarity = 0
                    
                    for entry in data['search-results']['entry']:
                        if 'dc:title' not in entry:
                            continue
                            
                        similarity = self.title_similarity(title, entry['dc:title'])
                        
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = entry
                    
                    if best_similarity >= min_similarity and best_match and 'prism:doi' in best_match:
                        # Get full abstract using the DOI
                        return self.get_by_doi(best_match['prism:doi'])
                    
                    logger.debug(f"No results met minimum similarity threshold ({min_similarity}) for title: {title}")
                    return None
                    
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching for title '{title}' on Elsevier: {str(e)}")
            return None
    
    def get_abstract(self, entry: Dict) -> Optional[str]:
        """
        Extract abstract from Elsevier metadata.
        
        Args:
            entry: Elsevier metadata dictionary
            
        Returns:
            Abstract text if found, None otherwise
        """
        try:
            # Navigate through the JSON structure to find the abstract
            if 'abstracts-retrieval-response' in entry:
                # From Abstract Retrieval API
                core_data = entry['abstracts-retrieval-response']['coredata']
                if 'dc:description' in core_data:
                    return core_data['dc:description']
            elif 'full-text-retrieval-response' in entry:
                # From Full Text API
                core_data = entry['full-text-retrieval-response']['coredata']
                if 'dc:description' in core_data:
                    return core_data['dc:description']
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Error extracting abstract from Elsevier response: {str(e)}")
            return None 