"""
Module for cleaning and sanitizing BibTeX entries.
"""
import re
from typing import Dict, Optional
import html
import unicodedata

class BibTeXCleaner:
    @staticmethod
    def clean_abstract(text: Optional[str]) -> Optional[str]:
        """
        Clean abstract text by removing XML/HTML tags, normalizing whitespace,
        and fixing common formatting issues.
        
        Args:
            text: Abstract text to clean
            
        Returns:
            Cleaned abstract text
        """
        if not text:
            return None
            
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove XML/HTML tags (including JATS)
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove LaTeX commands
        text = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})?', ' ', text)
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKC', text)
        
        # Fix common issues
        text = text.replace('\n', ' ')  # Replace newlines with spaces
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)  # Remove control characters
        text = re.sub(r'[^\x00-\x7F]+', lambda m: unicodedata.normalize('NFKD', m.group()), text)  # Handle non-ASCII
        
        # Remove brackets/braces that might be from XML/HTML
        text = re.sub(r'^\s*[\[\{\(]|\[\{\)]\s*$', '', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def clean_title(text: Optional[str]) -> Optional[str]:
        """
        Clean title text, preserving proper capitalization but fixing formatting.
        
        Args:
            text: Title text to clean
            
        Returns:
            Cleaned title text
        """
        if not text:
            return None
            
        # Basic cleaning
        text = html.unescape(text)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = unicodedata.normalize('NFKC', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    @staticmethod
    def clean_author(text: Optional[str]) -> Optional[str]:
        """
        Clean author names, preserving proper formatting.
        
        Args:
            text: Author text to clean
            
        Returns:
            Cleaned author text
        """
        if not text:
            return None
            
        # Basic cleaning
        text = html.unescape(text)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = unicodedata.normalize('NFKC', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common author list formatting issues
        text = re.sub(r'\s*,\s*', ', ', text)  # Normalize commas
        text = re.sub(r'\s*and\s*', ' and ', text)  # Normalize 'and'
        text = text.strip()
        
        return text
    
    @staticmethod
    def clean_entry(entry: Dict[str, str]) -> Dict[str, str]:
        """
        Clean all relevant fields in a BibTeX entry.
        
        Args:
            entry: BibTeX entry dictionary
            
        Returns:
            Cleaned entry dictionary
        """
        # Make a copy to avoid modifying the original
        cleaned = entry.copy()
        
        # Clean fields
        if 'abstract' in cleaned:
            cleaned['abstract'] = BibTeXCleaner.clean_abstract(cleaned['abstract'])
            
        if 'title' in cleaned:
            cleaned['title'] = BibTeXCleaner.clean_title(cleaned['title'])
            
        if 'author' in cleaned:
            cleaned['author'] = BibTeXCleaner.clean_author(cleaned['author'])
            
        # Remove empty fields
        cleaned = {k: v for k, v in cleaned.items() if v is not None and v != ''}
        
        return cleaned 