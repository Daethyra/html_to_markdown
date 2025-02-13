"""
Core HTML to Markdown conversion with BeautifulSoup cleanup
"""

from bs4 import BeautifulSoup
from markdownify import markdownify as md
import logging

class HTMLToMarkdownConverter:
    def __init__(self, strip_tags=None, convert_links=True):
        """
        Initialize HTML converter with cleanup rules
        
        :param strip_tags: List of HTML tags to remove completely
        :param convert_links: Convert links to Markdown format
        """
        self.strip_tags = strip_tags or ["script", "style", "meta", "nav", "footer"]
        self.convert_links = convert_links
        self._remove_selectors = [
            "header", ".navbar", ".menu", "#sidebar",
            "#ad-container", 'div[class*="cookie"]', "aside", "form"
        ]

    def convert(self, html_content):
        """
        Convert HTML content to cleaned Markdown format
        
        :param html_content: Raw HTML string input
        :return: Cleaned Markdown content string
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            self._remove_unwanted_elements(soup)
            return self._html_to_markdown(str(soup))
        except Exception as e:
            logging.error(f"Conversion error: {str(e)}")
            raise

    def _remove_unwanted_elements(self, soup):
        """Remove configured elements from BeautifulSoup tree"""
        # Remove by CSS selectors
        for selector in self._remove_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Remove by tag names
        for tag in self.strip_tags:
            for element in soup.find_all(tag):
                element.decompose()

    def _html_to_markdown(self, html):
        """Convert cleaned HTML to Markdown with proper formatting"""
        return md(
            html,
            heading_style="ATX",
            bullets="-*",
            strip=self.strip_tags,
            convert_links=self.convert_links
        ).strip()