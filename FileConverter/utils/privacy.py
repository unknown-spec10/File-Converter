"""Privacy protection utilities for sensitive document handling."""
import re
import logging
from typing import Dict, List, Tuple
import os

logger = logging.getLogger(__name__)


class PrivacyChecker:
    """Check documents for sensitive information patterns."""
    
    # Sensitive patterns to detect
    PATTERNS = {
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'api_key': r'\b(sk|pk|api)[-_]?[a-zA-Z0-9]{20,}\b',
        'password': r'(password|passwd|pwd)[\s:=]+\S+',
    }
    
    # Confidentiality markers
    MARKERS = [
        'confidential',
        'secret',
        'classified',
        'proprietary',
        'internal only',
        'do not distribute',
        'attorney-client',
        'hipaa',
        'private',
        'restricted',
    ]
    
    def __init__(self):
        """Initialize privacy checker."""
        self.findings = []
    
    def check_text(self, text: str) -> Tuple[bool, List[str]]:
        """Check text for sensitive patterns.
        
        Args:
            text: Text to check
        
        Returns:
            Tuple of (has_sensitive_info, list_of_findings)
        """
        self.findings = []
        
        # Check patterns
        for pattern_name, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                self.findings.append(f"{pattern_name}: {len(matches)} occurrence(s)")
                logger.warning(f"Found sensitive pattern: {pattern_name}")
        
        # Check markers
        text_lower = text.lower()
        for marker in self.MARKERS:
            if marker in text_lower:
                self.findings.append(f"Confidentiality marker: '{marker}'")
                logger.warning(f"Found confidentiality marker: {marker}")
        
        has_sensitive = len(self.findings) > 0
        
        return has_sensitive, self.findings
    
    def check_layout_data(self, layout_data: Dict) -> Tuple[bool, List[str]]:
        """Check extracted layout data for sensitive information.
        
        Args:
            layout_data: Layout data dict from LayoutExtractor
        
        Returns:
            Tuple of (has_sensitive_info, list_of_findings)
        """
        all_text = []
        
        # Collect all text from layout
        for page in layout_data.get('pages', []):
            for block in page.get('blocks', []):
                text = block.get('text', '')
                if text:
                    all_text.append(text)
        
        combined_text = '\n'.join(all_text)
        return self.check_text(combined_text)


class DataMinimizer:
    """Minimize data sent to external APIs."""
    
    @staticmethod
    def anonymize_layout_data(layout_data: Dict) -> Dict:
        """Remove or anonymize sensitive information from layout data.
        
        Args:
            layout_data: Original layout data
        
        Returns:
            Anonymized layout data
        """
        import copy
        anonymized = copy.deepcopy(layout_data)
        
        # Remove file metadata
        if 'metadata' in anonymized:
            metadata = anonymized['metadata']
            # Keep only essential fields
            anonymized['metadata'] = {
                'total_pages': metadata.get('total_pages', 0),
                # Remove filename, author, etc.
            }
        
        # Anonymize text in blocks
        for page in anonymized.get('pages', []):
            for block in page.get('blocks', []):
                if 'text' in block:
                    block['text'] = DataMinimizer._anonymize_text(block['text'])
        
        return anonymized
    
    @staticmethod
    def _anonymize_text(text: str) -> str:
        """Anonymize sensitive patterns in text.
        
        Args:
            text: Original text
        
        Returns:
            Anonymized text
        """
        # Replace emails
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL]',
            text
        )
        
        # Replace phone numbers
        text = re.sub(
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            '[PHONE]',
            text
        )
        
        # Replace SSN
        text = re.sub(
            r'\b\d{3}-\d{2}-\d{4}\b',
            '[SSN]',
            text
        )
        
        # Replace credit cards
        text = re.sub(
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            '[CARD]',
            text
        )
        
        return text
    
    @staticmethod
    def should_use_local_mode(layout_data: Dict, strict: bool = False) -> bool:
        """Determine if document should use local-only processing.
        
        Args:
            layout_data: Layout data to check
            strict: If True, be more conservative
        
        Returns:
            True if should use local mode
        """
        checker = PrivacyChecker()
        has_sensitive, findings = checker.check_layout_data(layout_data)
        
        if has_sensitive:
            logger.warning("Sensitive information detected in document:")
            for finding in findings:
                logger.warning(f"  - {finding}")
            logger.warning("Recommendation: Use local-only mode (text/ocr)")
            
            # Check environment variable for override
            disable_groq = os.getenv('DISABLE_GROQ_MODE', 'false').lower() == 'true'
            if disable_groq:
                logger.info("DISABLE_GROQ_MODE is set, forcing local mode")
                return True
            
            # In strict mode, always use local for sensitive content
            if strict:
                return True
        
        return False


def audit_api_request(layout_data: Dict, audit_file: str = 'groq_audit_log.json') -> None:
    """Save API request data for audit purposes.
    
    Args:
        layout_data: Data being sent to API
        audit_file: Path to audit log file
    """
    import json
    from datetime import datetime
    from pathlib import Path
    
    # Check if audit mode is enabled
    if os.getenv('GROQ_AUDIT_MODE', 'false').lower() != 'true':
        return
    
    audit_entry = {
        'timestamp': datetime.now().isoformat(),
        'total_pages': layout_data.get('total_pages', 0),
        'total_blocks': sum(
            len(page.get('blocks', []))
            for page in layout_data.get('pages', [])
        ),
        'data': layout_data
    }
    
    audit_path = Path(audit_file)
    
    # Append to audit log
    existing_logs = []
    if audit_path.exists():
        with open(audit_path, 'r') as f:
            existing_logs = json.load(f)
    
    existing_logs.append(audit_entry)
    
    with open(audit_path, 'w') as f:
        json.dump(existing_logs, f, indent=2)
    
    logger.info(f"✓ API request audited: {audit_file}")


if __name__ == "__main__":
    # Test privacy checker
    test_text = """
    John Doe
    Email: john.doe@example.com
    Phone: 555-123-4567
    SSN: 123-45-6789
    
    CONFIDENTIAL - DO NOT DISTRIBUTE
    """
    
    checker = PrivacyChecker()
    has_sensitive, findings = checker.check_text(test_text)
    
    print(f"Has sensitive info: {has_sensitive}")
    print(f"Findings: {findings}")
