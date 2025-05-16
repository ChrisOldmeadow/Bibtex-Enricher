"""
Semantic Scholar API client for retrieving publication metadata.
"""
import requests
from typing import Dict, Optional
import time
import logging
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class SemanticScholarAPI:
    BASE_URL = "https://api.semanticscholar.org/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Semantic Scholar API client.
        
        Args:
            api_key: Optional API key for higher rate limits
        """
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'x-api-key': api_key})
    
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
        Retrieve publication metadata by DOI.
        
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
                    response = self.session.get(f"{self.BASE_URL}/paper/{doi}")
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching DOI {doi} from Semantic Scholar: {str(e)}")
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
                    params = {'query': search_title, 'limit': 5}  # Get more results to find best match
                    response = self.session.get(f"{self.BASE_URL}/paper/search", params=params)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            
            data = response.json()
            if data['total'] == 0:
                return None
            
            # Find best matching result
            best_match = None
            best_similarity = 0
            
            for paper in data['papers']:
                if 'title' not in paper:
                    continue
                    
                similarity = self.title_similarity(title, paper['title'])
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = paper
            
            if best_similarity >= min_similarity:
                # If we found a good match, get full paper details by ID
                if best_match.get('paperId'):
                    paper_details = self.session.get(f"{self.BASE_URL}/paper/{best_match['paperId']}")
                    paper_details.raise_for_status()
                    return paper_details.json()
                return best_match
            
            logger.debug(f"No results met minimum similarity threshold ({min_similarity}) for title: {title}")
            return None
            
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            logger.error(f"Error searching for title '{title}' on Semantic Scholar: {str(e)}")
            return None
    
    def get_abstract(self, entry: Dict) -> Optional[str]:
        """
        Extract abstract from Semantic Scholar metadata.
        
        Args:
            entry: Semantic Scholar metadata dictionary
            
        Returns:
            Abstract text if found, None otherwise
        """
        return entry.get('abstract') 