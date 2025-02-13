"""
Markdown formatting and structure management for dataset conversion.
Maintains async processing capabilities for large datasets.
"""

import asyncio
import logging

class DatasetFormatter:
    def __init__(self, converter):
        """
        Initialize formatter with HTML converter.
        
        Args:
            converter: HTMLToMarkdownConverter instance
        """
        self.converter = converter

    async def format_entry(self, entry):
        """
        Process single JSON entry to Markdown format.
        
        Args:
            entry: Dict with title, url, and html keys
            
        Returns:
            Structured Markdown string for entry
        """
        try:
            title = entry.get("title", "Untitled")
            url = entry.get("url", "")
            content = self.converter.convert(entry.get("html", ""))
            return self._structure_entry(title, url, content)
        except Exception as e:
            logging.error(f"Entry formatting failed: {str(e)}")
            return ""

    def _structure_entry(self, title, url, content):
        """
        Create consistent Markdown structure for entries.
        
        Args:
            title: Page/document title
            url: Source URL
            content: Converted Markdown content
            
        Returns:
            Properly structured Markdown section
        """
        sections = [
            f"## {title}",
            f"[Source]({url})" if url else "",
            content.strip()
        ]
        return "\n\n".join(filter(None, sections))

    async def format_dataset(self, data):
        """
        Process entire dataset with parallel execution.
        
        Args:
            data: List of JSON entries
            
        Returns:
            Combined Markdown document string
        """
        tasks = [self.format_entry(entry) for entry in data]
        results = await asyncio.gather(*tasks)
        return "\n\n".join(filter(None, results))