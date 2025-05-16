"""
Streamlit web interface for BibTeX enricher.
"""
import streamlit as st
import tempfile
from pathlib import Path
import logging
import io
import shutil
import os
from dotenv import load_dotenv

from bibtex_enricher.enrich import BibTeXEnricher
from bibtex_enricher.bibio import BibIO

# Load environment variables
load_dotenv()

class StreamlitLogHandler(logging.Handler):
    """Custom logging handler that writes to a Streamlit container."""
    def __init__(self, container):
        super().__init__()
        self.container = container
        self.log_text = []
        
    def emit(self, record):
        # Format the record
        log_entry = self.format(record)
        
        # Add the new log entry
        self.log_text.append(log_entry)
        
        # Keep only the last 10 messages to avoid cluttering
        if len(self.log_text) > 10:
            self.log_text.pop(0)
            
        # Update the Streamlit container
        log_message = "\n".join(self.log_text)
        self.container.code(log_message)

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   datefmt='%H:%M:%S')

def main():
    st.set_page_config(
        page_title="BibTeX Abstract Enricher",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 BibTeX Abstract Enricher")
    st.write("""
    Upload a BibTeX file to enrich its entries with abstracts from Crossref, Semantic Scholar, PubMed, and Elsevier.
    The tool will attempt to find abstracts for entries that don't have them.
    """)
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # API credentials
    with st.sidebar.expander("API Credentials", expanded=True):
        crossref_email = st.text_input(
            "Crossref Email (optional)", 
            value=os.getenv('CROSSREF_EMAIL', ''),
            help="Email for Crossref polite pool"
        )
        semantic_scholar_key = st.text_input(
            "Semantic Scholar API Key (optional)", 
            value=os.getenv('SEMANTIC_SCHOLAR_KEY', ''),
            help="API key for higher rate limits"
        )
        pubmed_email = st.text_input(
            "PubMed Email (required if using PubMed)", 
            value=os.getenv('PUBMED_EMAIL', ''),
            help="Email for PubMed API"
        )
        pubmed_api_key = st.text_input(
            "PubMed API Key (optional)", 
            value=os.getenv('PUBMED_API_KEY', ''),
            help="API key for higher rate limits"
        )
        elsevier_api_key = st.text_input(
            "Elsevier API Key (optional)", 
            value=os.getenv('ELSEVIER_API_KEY', ''),
            help="API key for Elsevier access"
        )
    
    # API toggles
    with st.sidebar.expander("API Sources", expanded=True):
        use_semantic_scholar = st.checkbox("Use Semantic Scholar", value=True, help="Try Semantic Scholar as fallback")
        use_pubmed = st.checkbox("Use PubMed", value=True, help="Try PubMed as another source")
        use_elsevier = st.checkbox("Use Elsevier", value=True, help="Try Elsevier as another source")
    
    # Cache settings
    use_cache = st.sidebar.checkbox("Cache API Responses", value=True, help="Cache responses for faster repeated lookups")
    
    # File upload
    uploaded_file = st.file_uploader("Choose a BibTeX file", type="bib")
    
    if uploaded_file:
        # Create a container for the log output
        log_container = st.empty()
        
        # Create and add our custom handler
        streamlit_handler = StreamlitLogHandler(log_container)
        root_logger = logging.getLogger()
        root_logger.addHandler(streamlit_handler)
        
        # Progress container
        progress_container = st.empty()
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix=".bib", delete=False) as input_file:
            input_path = input_file.name
            input_file.write(uploaded_file.getvalue())
            
        with tempfile.NamedTemporaryFile(suffix=".bib", delete=False) as output_file:
            output_path = output_file.name
            
        # Setup cache
        cache_dir = None
        if use_cache:
            cache_dir = tempfile.mkdtemp()
        
        try:
            # Initialize enricher
            enricher = BibTeXEnricher(
                crossref_email=crossref_email or None,
                semantic_scholar_key=semantic_scholar_key or None,
                pubmed_email=pubmed_email or None,
                pubmed_api_key=pubmed_api_key or None,
                elsevier_api_key=elsevier_api_key or None,
                cache_path=cache_dir
            )
            
            # Run enrichment with progress bar
            with progress_container:
                stats = enricher.enrich_file(
                    input_path,
                    output_path,
                    use_semantic_scholar=use_semantic_scholar,
                    use_pubmed=use_pubmed,
                    use_elsevier=use_elsevier
                )
            
            # Remove the Streamlit handler
            root_logger.removeHandler(streamlit_handler)
            
            # Display statistics
            st.success("Enrichment complete!")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Entries", stats['total'])
            col2.metric("Already Had Abstract", stats['already_had_abstract'])
            col3.metric("Successfully Enriched", stats['enriched'])
            col4.metric("Failed to Enrich", stats['failed'])
            
            # Provide download link
            with open(output_path, 'r') as f:
                output_content = f.read()
                
            st.download_button(
                "Download Enriched BibTeX",
                output_content,
                "enriched.bib",
                "text/plain",
                use_container_width=True
            )
            
        finally:
            # Cleanup temporary files
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)
            if use_cache and cache_dir:
                shutil.rmtree(cache_dir, ignore_errors=True)

if __name__ == "__main__":
    main() 