#!/usr/bin/env python3
"""
PDF Content Processor for RAG Knowledge Base
Downloads, extracts, and processes PDF content for integration into the RAG system
"""

import os
import json
import re
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import hashlib
from urllib.parse import urljoin, urlparse

# Set up logging
logger = logging.getLogger(__name__)

try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    print("PyPDF2 not found. Install with: pip install PyPDF2")
    PDF_SUPPORT = False

try:
    import pdfplumber
    ADVANCED_PDF_SUPPORT = True
except ImportError:
    print("pdfplumber not found. Install with: pip install pdfplumber")
    ADVANCED_PDF_SUPPORT = False

class PDFProcessor:
    """Processes PDF documents for RAG knowledge base integration"""
    
    def __init__(self, storage_dir="/tmp/tileshop_pdfs"):
        self.storage_dir = storage_dir
        self.knowledge_base_dir = os.path.join(storage_dir, "knowledge_base")
        
        # Create directories if they don't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(self.knowledge_base_dir, exist_ok=True)
        
        # Knowledge base structure
        self.kb_categories = {
            'installation_guide': 'Installation Guides',
            'care_instructions': 'Care & Maintenance', 
            'specification_sheet': 'Technical Specifications',
            'warranty_info': 'Warranty Information',
            'user_manual': 'User Manuals',
            'general_resource': 'General Resources'
        }
    
    def download_pdf(self, pdf_url: str, pdf_title: str) -> Optional[str]:
        """Download PDF and return local file path"""
        try:
            # Create a safe filename
            safe_title = re.sub(r'[^\w\s-]', '', pdf_title)
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            
            # Generate unique filename with hash
            url_hash = hashlib.md5(pdf_url.encode()).hexdigest()[:8]
            filename = f"{safe_title}_{url_hash}.pdf"
            file_path = os.path.join(self.storage_dir, filename)
            
            # Skip if already downloaded
            if os.path.exists(file_path):
                logger.info(f"PDF already exists: {filename}")
                return file_path
            
            # Download the PDF
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(pdf_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Verify it's actually a PDF
            if not response.content.startswith(b'%PDF'):
                logger.warning(f"URL doesn't contain valid PDF content: {pdf_url}")
                return None
            
            # Save the PDF
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded PDF: {filename} ({len(response.content)} bytes)")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to download PDF {pdf_url}: {e}")
            return None
    
    def extract_text_from_pdf(self, file_path: str) -> Optional[str]:
        """Extract text content from PDF file"""
        if not PDF_SUPPORT:
            logger.error("PDF processing not available - install PyPDF2")
            return None
        
        try:
            # Try pdfplumber first (better text extraction)
            if ADVANCED_PDF_SUPPORT:
                return self._extract_with_pdfplumber(file_path)
            else:
                return self._extract_with_pypdf2(file_path)
                
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            return None
    
    def _extract_with_pdfplumber(self, file_path: str) -> str:
        """Extract text using pdfplumber (preferred method)"""
        import pdfplumber
        
        text_content = []
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(f"--- Page {page_num} ---\n{text.strip()}")
        
        return "\n\n".join(text_content)
    
    def _extract_with_pypdf2(self, file_path: str) -> str:
        """Extract text using PyPDF2 (fallback method)"""
        import PyPDF2
        
        text_content = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(f"--- Page {page_num} ---\n{text.strip()}")
        
        return "\n\n".join(text_content)
    
    def process_pdf_for_knowledge_base(self, pdf_data: Dict) -> Optional[Dict]:
        """Process a single PDF and prepare for knowledge base"""
        pdf_url = pdf_data.get('url')
        pdf_title = pdf_data.get('title', 'Unknown Document')
        pdf_type = pdf_data.get('type', 'general_resource')
        
        if not pdf_url:
            return None
        
        # Download PDF
        file_path = self.download_pdf(pdf_url, pdf_title)
        if not file_path:
            return None
        
        # Extract text content
        text_content = self.extract_text_from_pdf(file_path)
        if not text_content:
            return None
        
        # Process and structure the content
        structured_content = self._structure_content(text_content, pdf_type, pdf_title)
        
        # Create knowledge base entry
        kb_entry = {
            'id': hashlib.md5(pdf_url.encode()).hexdigest(),
            'title': pdf_title,
            'type': pdf_type,
            'category': self.kb_categories.get(pdf_type, 'General Resources'),
            'url': pdf_url,
            'file_path': file_path,
            'content': structured_content,
            'raw_text': text_content,
            'processed_at': datetime.now().isoformat(),
            'word_count': len(text_content.split()),
            'page_count': text_content.count('--- Page ')
        }
        
        # Save to knowledge base
        self._save_to_knowledge_base(kb_entry)
        
        return kb_entry
    
    def _structure_content(self, text_content: str, pdf_type: str, title: str) -> Dict:
        """Structure PDF content based on type"""
        structured = {
            'title': title,
            'type': pdf_type,
            'sections': []
        }
        
        # Split content by pages first
        pages = text_content.split('--- Page ')
        
        if pdf_type == 'installation_guide':
            structured['sections'] = self._extract_installation_sections(text_content)
        elif pdf_type == 'care_instructions':
            structured['sections'] = self._extract_care_sections(text_content)
        elif pdf_type == 'specification_sheet':
            structured['sections'] = self._extract_spec_sections(text_content)
        elif pdf_type == 'warranty_info':
            structured['sections'] = self._extract_warranty_sections(text_content)
        else:
            # General structure - just split by common section headers
            structured['sections'] = self._extract_general_sections(text_content)
        
        return structured
    
    def _extract_installation_sections(self, text: str) -> List[Dict]:
        """Extract installation guide sections"""
        sections = []
        common_headers = [
            r'(?:STEP\s+\d+|Step\s+\d+)',
            r'(?:INSTALLATION|Installation)',
            r'(?:PREPARATION|Preparation)',
            r'(?:TOOLS|Tools\s+Required|Materials)',
            r'(?:SAFETY|Safety\s+Instructions)',
            r'(?:BEFORE\s+YOU\s+BEGIN|Before\s+Starting)',
            r'(?:FINISHING|Finishing\s+Steps)',
            r'(?:MAINTENANCE|Care\s+Instructions)'
        ]
        
        return self._extract_sections_by_headers(text, common_headers, 'installation')
    
    def _extract_care_sections(self, text: str) -> List[Dict]:
        """Extract care instruction sections"""
        common_headers = [
            r'(?:DAILY\s+CARE|Daily\s+Maintenance)',
            r'(?:CLEANING|Cleaning\s+Instructions)',
            r'(?:STAIN\s+REMOVAL|Stain\s+Treatment)',
            r'(?:DO\s+NOT|Avoid|Warning)',
            r'(?:RECOMMENDED|Recommended\s+Products)',
            r'(?:SEALING|Sealer\s+Application)',
            r'(?:TROUBLESHOOTING|Common\s+Issues)'
        ]
        
        return self._extract_sections_by_headers(text, common_headers, 'care')
    
    def _extract_spec_sections(self, text: str) -> List[Dict]:
        """Extract specification sheet sections"""
        common_headers = [
            r'(?:PRODUCT\s+SPECIFICATIONS|Product\s+Details)',
            r'(?:DIMENSIONS|Size\s+Information)',
            r'(?:TECHNICAL\s+DATA|Technical\s+Properties)',
            r'(?:PERFORMANCE|Performance\s+Ratings)',
            r'(?:CERTIFICATIONS|Standards)',
            r'(?:APPLICATIONS|Suitable\s+Uses)',
            r'(?:PACKAGING|Box\s+Information)'
        ]
        
        return self._extract_sections_by_headers(text, common_headers, 'specification')
    
    def _extract_warranty_sections(self, text: str) -> List[Dict]:
        """Extract warranty information sections"""
        common_headers = [
            r'(?:WARRANTY\s+TERMS|Warranty\s+Coverage)',
            r'(?:EXCLUSIONS|What\s+is\s+Not\s+Covered)',
            r'(?:CLAIMS|How\s+to\s+File\s+a\s+Claim)',
            r'(?:CONTACT|Customer\s+Service)',
            r'(?:DURATION|Warranty\s+Period)',
            r'(?:TRANSFERABILITY|Transfer\s+of\s+Warranty)'
        ]
        
        return self._extract_sections_by_headers(text, common_headers, 'warranty')
    
    def _extract_general_sections(self, text: str) -> List[Dict]:
        """Extract general document sections"""
        common_headers = [
            r'(?:INTRODUCTION|Overview)',
            r'(?:DESCRIPTION|Product\s+Description)',
            r'(?:FEATURES|Key\s+Features)',
            r'(?:BENEFITS|Advantages)',
            r'(?:APPLICATIONS|Uses)',
            r'(?:SPECIFICATIONS|Details)',
            r'(?:INSTALLATION|How\s+to\s+Install)',
            r'(?:MAINTENANCE|Care\s+Instructions)',
            r'(?:CONTACT|More\s+Information)'
        ]
        
        return self._extract_sections_by_headers(text, common_headers, 'general')
    
    def _extract_sections_by_headers(self, text: str, headers: List[str], section_type: str) -> List[Dict]:
        """Extract sections based on header patterns"""
        sections = []
        
        # Combine all header patterns
        combined_pattern = '|'.join(f'({header})' for header in headers)
        
        # Split text by headers
        parts = re.split(f'({combined_pattern})', text, flags=re.IGNORECASE | re.MULTILINE)
        
        current_header = None
        current_content = []
        
        for part in parts:
            if part is None:
                continue
            part = part.strip()
            if not part:
                continue
            
            # Check if this part is a header
            if re.match(combined_pattern, part, re.IGNORECASE):
                # Save previous section if exists
                if current_header and current_content:
                    sections.append({
                        'header': current_header,
                        'content': '\n'.join(current_content).strip(),
                        'type': section_type
                    })
                
                # Start new section
                current_header = part
                current_content = []
            else:
                # Add to current section content
                if part and len(part) > 10:  # Only add substantial content
                    current_content.append(part)
        
        # Add final section
        if current_header and current_content:
            sections.append({
                'header': current_header,
                'content': '\n'.join(current_content).strip(),
                'type': section_type
            })
        
        return sections
    
    def _save_to_knowledge_base(self, kb_entry: Dict):
        """Save knowledge base entry to file"""
        category_dir = os.path.join(self.knowledge_base_dir, kb_entry['type'])
        os.makedirs(category_dir, exist_ok=True)
        
        filename = f"{kb_entry['id']}.json"
        file_path = os.path.join(category_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(kb_entry, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved to knowledge base: {kb_entry['title']}")
    
    def get_knowledge_base_summary(self) -> Dict:
        """Get summary of processed knowledge base"""
        summary = {
            'total_documents': 0,
            'categories': {},
            'last_updated': datetime.now().isoformat()
        }
        
        for category in self.kb_categories.keys():
            category_dir = os.path.join(self.knowledge_base_dir, category)
            if os.path.exists(category_dir):
                files = [f for f in os.listdir(category_dir) if f.endswith('.json')]
                summary['categories'][category] = {
                    'count': len(files),
                    'display_name': self.kb_categories[category]
                }
                summary['total_documents'] += len(files)
        
        return summary
    
    def search_knowledge_base(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Search knowledge base content"""
        results = []
        query_lower = query.lower()
        
        categories_to_search = [category] if category else self.kb_categories.keys()
        
        for cat in categories_to_search:
            category_dir = os.path.join(self.knowledge_base_dir, cat)
            if not os.path.exists(category_dir):
                continue
            
            for filename in os.listdir(category_dir):
                if not filename.endswith('.json'):
                    continue
                
                file_path = os.path.join(category_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        kb_entry = json.load(f)
                    
                    # Search in title, content, and sections
                    relevance_score = 0
                    matched_sections = []
                    
                    # Check title
                    if query_lower in kb_entry['title'].lower():
                        relevance_score += 10
                    
                    # Check sections
                    for section in kb_entry['content'].get('sections', []):
                        section_text = (section.get('header', '') + ' ' + section.get('content', '')).lower()
                        if query_lower in section_text:
                            relevance_score += 5
                            matched_sections.append(section)
                    
                    # Check raw text
                    if query_lower in kb_entry.get('raw_text', '').lower():
                        relevance_score += 1
                    
                    if relevance_score > 0:
                        results.append({
                            'title': kb_entry['title'],
                            'type': kb_entry['type'],
                            'category': kb_entry['category'],
                            'url': kb_entry['url'],
                            'relevance_score': relevance_score,
                            'matched_sections': matched_sections[:3],  # Top 3 sections
                            'file_path': kb_entry['file_path']
                        })
                
                except Exception as e:
                    logger.error(f"Error searching file {filename}: {e}")
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:10]  # Top 10 results

def process_product_pdfs(product_data: Dict) -> Dict:
    """Process all PDFs for a product and return knowledge base summary"""
    processor = PDFProcessor()
    
    resources = product_data.get('resources')
    if not resources:
        return {'processed': 0, 'errors': 0}
    
    try:
        resources_data = json.loads(resources) if isinstance(resources, str) else resources
    except (json.JSONDecodeError, TypeError):
        return {'processed': 0, 'errors': 0}
    
    pdf_documents = resources_data.get('pdf_documents', [])
    if not pdf_documents:
        return {'processed': 0, 'errors': 0}
    
    processed = 0
    errors = 0
    
    for pdf_data in pdf_documents:
        try:
            kb_entry = processor.process_pdf_for_knowledge_base(pdf_data)
            if kb_entry:
                processed += 1
                logger.info(f"Processed PDF: {pdf_data.get('title', 'Unknown')}")
            else:
                errors += 1
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_data.get('url', 'Unknown')}: {e}")
            errors += 1
    
    return {
        'processed': processed, 
        'errors': errors,
        'knowledge_base_summary': processor.get_knowledge_base_summary()
    }