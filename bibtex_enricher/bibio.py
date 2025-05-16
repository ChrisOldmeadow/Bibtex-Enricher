"""
BibTeX file I/O operations.
"""
from pathlib import Path
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from typing import Dict, Optional

class BibIO:
    @staticmethod
    def load_bibtex(file_path: str) -> BibDatabase:
        """
        Load a BibTeX file and return its database.
        
        Args:
            file_path: Path to the .bib file
            
        Returns:
            BibDatabase object containing the entries
        """
        with open(file_path) as bibtex_file:
            parser = bibtexparser.bparser.BibTexParser(common_strings=True)
            return bibtexparser.load(bibtex_file, parser=parser)
    
    @staticmethod
    def save_bibtex(database: BibDatabase, output_path: str) -> None:
        """
        Save a BibTeX database to file.
        
        Args:
            database: BibDatabase object to save
            output_path: Path where to save the .bib file
        """
        writer = bibtexparser.bwriter.BibTexWriter()
        writer.indent = '    '
        writer.order_entries_by = ('author', 'year', 'title')
        
        with open(output_path, 'w') as output_file:
            output_file.write(writer.write(database))
    
    @staticmethod
    def get_entry_identifier(entry: Dict[str, str]) -> str:
        """
        Get a unique identifier for a BibTeX entry.
        Prefers DOI, falls back to title.
        
        Args:
            entry: BibTeX entry dictionary
            
        Returns:
            String identifier for the entry
        """
        if 'doi' in entry:
            return f"DOI:{entry['doi']}"
        return f"Title:{entry.get('title', 'Unknown')}" 