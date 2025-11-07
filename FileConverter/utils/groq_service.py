"""Groq AI service for intelligent document reconstruction.

This module uses Groq's ultra-fast LLM inference to:
1. Analyze extracted PDF layout data
2. Reconstruct proper document structure (headings, lists, paragraphs)
3. Generate semantic style tags for accurate DOCX formatting
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from dotenv import load_dotenv
    # Load .env file from project root (override=True ensures .env takes precedence)
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)
except ImportError:
    pass  # dotenv is optional

logger = logging.getLogger(__name__)


@dataclass
class GroqConfig:
    """Configuration for Groq API."""
    api_key: str
    model: str = "llama-3.3-70b-versatile" 
    temperature: float = 0.1 
    max_tokens: int = 8000


class GroqDocumentReconstructor:
    """AI-powered document structure reconstruction using Groq."""
    
    def __init__(self, config: Optional[GroqConfig] = None):
        """Initialize Groq service.
        
        Args:
            config: Groq configuration. If None, will try to load from env.
        """
        if Groq is None:
            raise RuntimeError(
                "Groq library not installed. Install with: pip install groq"
            )
        
        if config is None:
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError(
                    "GROQ_API_KEY not found in environment. "
                    "Set it with: export GROQ_API_KEY='your-key-here'"
                )
            config = GroqConfig(api_key=api_key)
        
        self.config = config
        self.client = Groq(api_key=config.api_key)
        logger.info(f"Groq service initialized with model: {config.model}")
    
    def reconstruct_document(
        self, 
        layout_data: Dict[str, Any],
        pass_type: str = "layout"
    ) -> Dict[str, Any]:
        """Reconstruct document structure using AI reasoning.
        
        Args:
            layout_data: Structured layout data from PDF extraction
            pass_type: Type of reconstruction
                - 'layout': Clean structure, fix bullets, group paragraphs
                - 'style': Assign semantic tags (Heading, Body, List, etc.)
                - 'hybrid': Both layout + style in one pass
        
        Returns:
            Reconstructed document with AI corrections
        """
        if pass_type == "layout":
            return self._layout_reconstruction_pass(layout_data)
        elif pass_type == "style":
            return self._style_tagging_pass(layout_data)
        elif pass_type == "hybrid":
            return self._hybrid_reconstruction_pass(layout_data)
        else:
            raise ValueError(f"Unknown pass_type: {pass_type}")
    
    def _layout_reconstruction_pass(self, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        """First pass: Clean and structure paragraphs, bullets, lists."""
        
        prompt = self._build_layout_prompt(layout_data)
        
        logger.info("🧠 Groq AI: Analyzing document layout...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_layout_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            result_text = response.choices[0].message.content or ""
            
            # Parse AI response into structured format
            reconstructed = self._parse_ai_response(result_text, layout_data)
            
            tokens_used = response.usage.total_tokens if response.usage else 0
            logger.info(f"✓ Layout reconstruction complete ({tokens_used} tokens)")
            
            return reconstructed
            
        except Exception as e:
            logger.error(f"Groq API error during layout reconstruction: {e}")
            raise
    
    def _style_tagging_pass(self, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Second pass: Assign semantic style tags."""
        
        prompt = self._build_style_prompt(layout_data)
        
        logger.info("🎨 Groq AI: Assigning semantic styles...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_style_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            result_text = response.choices[0].message.content or ""
            
            # Parse style tags
            styled = self._parse_style_response(result_text, layout_data)
            
            tokens_used = response.usage.total_tokens if response.usage else 0
            logger.info(f"✓ Style tagging complete ({tokens_used} tokens)")
            
            return styled
            
        except Exception as e:
            logger.error(f"Groq API error during style tagging: {e}")
            raise
    
    def _hybrid_reconstruction_pass(self, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combined pass: Layout + Style in one call."""
        
        prompt = self._build_hybrid_prompt(layout_data)
        
        logger.info("⚡ Groq AI: Full document reconstruction (layout + style)...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_hybrid_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            result_text = response.choices[0].message.content or ""
            
            # Parse complete reconstruction
            reconstructed = self._parse_hybrid_response(result_text, layout_data)
            
            tokens_used = response.usage.total_tokens if response.usage else 0
            logger.info(f"✓ Hybrid reconstruction complete ({tokens_used} tokens)")
            
            return reconstructed
            
        except Exception as e:
            logger.error(f"Groq API error during hybrid reconstruction: {e}")
            raise
    
    def _get_layout_system_prompt(self) -> str:
        """System prompt for layout reconstruction."""
        from utils.ai_prompts import get_system_prompt
        # Use centralized prompt with fallback
        try:
            return get_system_prompt('pdf_to_docx')
        except:
            # Fallback prompt if import fails
            return """You are an expert document layout analyzer specializing in PDF-to-DOCX conversion.

Your task is to analyze extracted PDF layout data and reconstruct it into clean, properly structured content.

Key responsibilities:
1. Fix broken bullet points and numbered lists
2. Group related paragraphs correctly
3. Detect heading hierarchies (H1, H2, H3)
4. Preserve indentation and list nesting
5. Remove duplicate line breaks
6. Merge split lines that belong together

Output format: JSON with cleaned structure including:
- blocks: array of content blocks
- each block has: type (heading/paragraph/list_item/list), text, level (for headings/lists)

Be precise and maintain the original meaning while fixing formatting issues."""
    
    def _get_style_system_prompt(self) -> str:
        """System prompt for style tagging."""
        return """You are a semantic document tagger specializing in Word document styles.

Analyze the document structure and assign precise semantic tags for each block.

Available styles:
- Title: Main document title
- Heading 1, Heading 2, Heading 3: Section headings
- List Bullet: Unordered list items
- List Number: Ordered list items
- Normal: Regular body text
- Quote: Quoted or indented text
- Caption: Image/table captions

Output format: JSON array where each element has:
- original_text: the text block
- style: the Word style to apply
- confidence: your confidence level (0-1)

Consider font size, position, content, and context when assigning styles."""
    
    def _get_hybrid_system_prompt(self) -> str:
        """System prompt for combined reconstruction."""
        from utils.ai_prompts import PDF_TO_DOCX_SYSTEM_PROMPT
        try:
            return PDF_TO_DOCX_SYSTEM_PROMPT
        except:
            # Fallback
            return """You are an AI document reconstruction specialist for PDF-to-DOCX conversion.

Perform BOTH layout cleaning AND style tagging in a single pass.

Tasks:
1. Analyze the extracted PDF layout (text, coordinates, fonts, indentation)
2. Reconstruct proper document structure (fix bullets, merge lines, detect headings)
3. Assign semantic Word styles to each block

Output format: JSON with array of blocks, each containing:
- text: the cleaned text content
- style: Word style (Title, Heading 1/2/3, List Bullet, List Number, Normal, Quote)
- level: indent/hierarchy level (0-based)
- original_indices: which input blocks this combines

Important:
- Preserve all content, just restructure it
- Fix common PDF extraction issues (broken bullets, wrong spacing)
- Use context to distinguish headings from body text (font size, position, content)
- Maintain proper list hierarchy and indentation

Be intelligent but conservative - when uncertain, default to "Normal" style."""
    
    def _build_layout_prompt(self, layout_data: Dict[str, Any]) -> str:
        """Build user prompt for layout reconstruction."""
        
        # Summarize layout data for the prompt
        summary = {
            "total_pages": layout_data.get("total_pages", 0),
            "blocks": []
        }
        
        for page in layout_data.get("pages", []):
            for block in page.get("blocks", []):
                summary["blocks"].append({
                    "text": block.get("text", "")[:200],  # Truncate long text
                    "x0": round(block.get("x0", 0), 1),
                    "font": block.get("font", "unknown"),
                    "size": block.get("size", 0),
                    "indent_level": block.get("indent_level", 0)
                })
        
        prompt = f"""Analyze this PDF layout data and reconstruct it with proper structure:

{json.dumps(summary, indent=2)}

Please:
1. Fix bullet points (look for •, -, *, →, etc.)
2. Group paragraphs correctly
3. Detect headings (larger fonts, bold, positional cues)
4. Maintain proper indentation for nested lists
5. Remove extra line breaks

Return JSON with cleaned blocks."""
        
        return prompt
    
    def _build_style_prompt(self, layout_data: Dict[str, Any]) -> str:
        """Build user prompt for style tagging."""
        
        blocks = []
        for page in layout_data.get("pages", []):
            for block in page.get("blocks", []):
                blocks.append({
                    "text": block.get("text", "")[:150],
                    "font_size": block.get("size", 0),
                    "font_name": block.get("font", ""),
                    "indent": block.get("indent_level", 0)
                })
        
        prompt = f"""Assign semantic Word styles to these document blocks:

{json.dumps(blocks[:50], indent=2)}

Return JSON array with style assignments for each block."""
        
        return prompt
    
    def _build_hybrid_prompt(self, layout_data: Dict[str, Any]) -> str:
        """Build user prompt for hybrid reconstruction."""
        
        # Compact representation of layout data
        pages_data = []
        
        for page_num, page in enumerate(layout_data.get("pages", []), 1):
            page_info = {
                "page": page_num,
                "blocks": []
            }
            
            for block in page.get("blocks", []):
                page_info["blocks"].append({
                    "text": block.get("text", ""),
                    "x0": round(block.get("x0", 0), 1),
                    "y0": round(block.get("y0", 0), 1),
                    "font": block.get("font", "unknown"),
                    "size": round(block.get("size", 0), 1),
                    "indent": block.get("indent_level", 0)
                })
            
            pages_data.append(page_info)
        
        prompt = f"""Reconstruct this PDF document with proper structure and Word styles.

INPUT DATA:
{json.dumps(pages_data, indent=2)}

TASK:
1. Clean the layout (fix bullets, merge lines, remove extra breaks)
2. Assign Word styles (Title, Heading 1/2/3, List Bullet, Normal, etc.)
3. Maintain proper hierarchy and indentation

OUTPUT FORMAT:
{{
  "blocks": [
    {{
      "text": "cleaned text content",
      "style": "Word style name",
      "level": 0,
      "original_indices": [0, 1]
    }},
    ...
  ]
}}

Analyze carefully and provide the reconstructed document."""
        
        return prompt
    
    def _parse_ai_response(self, response_text: str, original_data: Dict) -> Dict[str, Any]:
        """Parse AI response for layout reconstruction."""
        
        try:
            # Try to extract JSON from response
            # AI might wrap it in markdown code blocks
            cleaned = response_text.strip()
            
            if "```json" in cleaned:
                start = cleaned.find("```json") + 7
                end = cleaned.find("```", start)
                cleaned = cleaned[start:end].strip()
            elif "```" in cleaned:
                start = cleaned.find("```") + 3
                end = cleaned.find("```", start)
                cleaned = cleaned[start:end].strip()
            
            result = json.loads(cleaned)
            
            return {
                "status": "success",
                "reconstructed": result,
                "original": original_data
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
            logger.debug(f"Raw response: {response_text[:500]}")
            
            # Fallback: return as plain text
            return {
                "status": "parse_error",
                "raw_text": response_text,
                "original": original_data
            }
    
    def _parse_style_response(self, response_text: str, original_data: Dict) -> Dict[str, Any]:
        """Parse AI response for style tagging."""
        return self._parse_ai_response(response_text, original_data)
    
    def _parse_hybrid_response(self, response_text: str, original_data: Dict) -> Dict[str, Any]:
        """Parse AI response for hybrid reconstruction."""
        return self._parse_ai_response(response_text, original_data)
    
    def validate_reconstruction(self, reconstructed: Dict[str, Any]) -> bool:
        """Validate that AI reconstruction is valid.
        
        Returns:
            True if valid, False otherwise
        """
        if reconstructed.get("status") != "success":
            return False
        
        result = reconstructed.get("reconstructed", {})
        
        # Check for required structure
        if "blocks" not in result:
            logger.warning("AI response missing 'blocks' field")
            return False
        
        blocks = result["blocks"]
        if not isinstance(blocks, list):
            logger.warning("'blocks' is not a list")
            return False
        
        # Validate each block
        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                logger.warning(f"Block {i} is not a dict")
                return False
            
            if "text" not in block:
                logger.warning(f"Block {i} missing 'text' field")
                return False
        
        return True


def test_groq_connection(api_key: Optional[str] = None) -> bool:
    """Test Groq API connection.
    
    Args:
        api_key: API key to test. If None, uses env variable.
    
    Returns:
        True if connection successful
    """
    try:
        config = GroqConfig(api_key=api_key) if api_key else None
        service = GroqDocumentReconstructor(config)
        
        # Simple test
        test_data = {
            "total_pages": 1,
            "pages": [{
                "page": 1,
                "blocks": [
                    {"text": "Test Document", "x0": 72, "font": "Arial-Bold", "size": 18, "indent_level": 0},
                    {"text": "This is a test paragraph.", "x0": 72, "font": "Arial", "size": 12, "indent_level": 0}
                ]
            }]
        }
        
        result = service.reconstruct_document(test_data, pass_type="hybrid")
        
        if service.validate_reconstruction(result):
            logger.info("✓ Groq connection test successful")
            return True
        else:
            logger.warning("Groq responded but output validation failed")
            return False
            
    except Exception as e:
        logger.error(f"Groq connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test script
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s'
    )
    
    # Ensure .env is loaded for testing
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Loaded .env from {env_path}")
    except Exception as e:
        logger.debug(f"Could not load .env: {e}")
    
    if len(sys.argv) > 1:
        # Test with provided API key
        api_key = sys.argv[1]
        test_groq_connection(api_key)
    else:
        # Test with env variable
        test_groq_connection()
