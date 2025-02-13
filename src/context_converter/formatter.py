"""
Markdown formatting and structure management
"""

import logging

class DatasetFormatter:
    def __init__(self, converter):
        """
        Initialize formatter with HTML converter
        
        :param converter: HTMLToMarkdownConverter instance
        """
        self.converter = converter

    def format_entry(self, entry):
        """
        Process single JSON entry to Markdown format
        
        :param entry: Dict with title, url, and html keys
        :return: Structured Markdown string for entry
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
        Create consistent Markdown structure for entries
        
        :param title: Page/document title
        :param url: Source URL
        :param content: Converted Markdown content
        :return: Properly structured Markdown section
        """
        sections = [
            f"## {title}",
            f"[Source]({url})" if url else "",
            content.strip()
        ]
        return "\n\n".join(filter(None, sections))

    def format_dataset(self, data):
        """
        Process entire dataset
        
        :param data: List of JSON entries
        :return: Combined Markdown document string
        """
        return "\n\n".join(
            self.format_entry(entry) 
            for entry in data
            if entry.get("html")
        )