# 🗺️ BibTeX Enricher Roadmap

This document outlines the planned features and improvements for BibTeX Enricher.

## 🎯 Current Version (1.0.0)

Core functionality implemented:
- Multiple API support (Elsevier, PubMed, Crossref, Semantic Scholar)
- CLI and web interface
- Real-time logging
- Text cleaning
- API response caching

## 🚀 Short-term Goals (Next Release)

### Bibliography Format Support
- [ ] CSV file support
  - Minimum fields: authors, title, DOI
  - Flexible column mapping
  - Export to BibTeX
- [ ] RIS format support
- [ ] EndNote XML format support
- [ ] Custom format configuration

### API Integrations
- [ ] Add support for IEEE Xplore API
- [ ] Add support for arXiv API
- [ ] Improve error handling for API rate limits

### Performance
- [ ] Implement parallel processing for multiple entries
- [ ] Optimize API request batching
- [ ] Improve cache management

### User Interface
- [ ] Add progress bars in web interface
- [ ] Implement dark mode for web interface
- [ ] Add API status indicators
- [ ] Add file format selection in web interface
- [ ] CSV column mapping interface

### Data Processing
- [ ] Enhanced text cleaning options
- [ ] Support for additional BibTeX fields
- [ ] Custom field mapping configuration
- [ ] Author name normalization across formats

## 🌟 Medium-term Goals

### Features
- [ ] Batch processing of multiple files (any supported format)
- [ ] Export statistics and logs
- [ ] Custom API priority ordering
- [ ] API fallback configuration
- [ ] Citation count enrichment
- [ ] Format conversion tools (CSV ↔ BibTeX ↔ RIS)

### Integration
- [ ] Plugin system for custom API integrations
- [ ] Reference management software integration
- [ ] CI/CD pipeline setup
- [ ] Format converter plugins

### Documentation
- [ ] API integration guide
- [ ] Developer documentation
- [ ] User guide with examples
- [ ] Performance optimization guide
- [ ] Format specification guide

## 🎯 Long-term Vision

### Advanced Features
- [ ] Machine learning for abstract matching
- [ ] DOI prediction for entries without DOI
- [ ] Automated metadata correction
- [ ] Reference cross-linking
- [ ] Smart format detection
- [ ] Bulk format conversion with enrichment

### Platform
- [ ] Web API service
- [ ] Docker container
- [ ] Cloud deployment option
- [ ] User authentication system

## 📋 Completed Features

### Version 1.0.0
- ✅ Multiple API support
- ✅ CLI implementation
- ✅ Web dashboard
- ✅ Real-time logging
- ✅ Text cleaning
- ✅ API response caching

## 🤝 Contributing

We welcome contributions! If you'd like to work on any of these features or have other ideas:
1. Check the GitHub issues to see if someone is already working on it
2. Create a new issue using the feature request template
3. Discuss the implementation approach
4. Submit a pull request

## 📝 Notes

- Priority of features may change based on user feedback
- Some features may require additional API access or credentials
- Performance implications will be considered for each feature
- Format support will focus on common academic reference formats 