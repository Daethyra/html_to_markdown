"""
Markdown formatting and structure management
"""

import logging
import re

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
            f"<!-- Entry start: {title} -->",
            f"## {title}",
            f"[Source]({url})" if url else "",
            self._escape_md_in_content(content.strip()),
            "<!-- Entry end -->"
        ]
        return "\n\n".join([s for s in sections if s.strip()])

    def _escape_md_in_content(self, content):
        """Safer escaping that preserves code block context"""
        lines = []
        code_block_depth = 0
        current_fence = None
        
        for line in content.split('\n'):
            fence_match = re.match(r'^(?P<fence>`{3,})', line)
            if fence_match:
                if not current_fence:
                    code_block_depth += 1
                    current_fence = fence_match.group('fence')
                elif line.strip() == current_fence:
                    code_block_depth -= 1
                    current_fence = None
                lines.append(line)
                continue
            
            if code_block_depth > 0:
                lines.append(line)
            else:
                line = re.sub(r'(?<!\\)([#*_~|<>\[\]{}`-])', r'\\\1', line)
                lines.append(line)
        
        return '\n'.join(lines)

    def _escape_markdown_syntax(self, line):
        """Escape Markdown special characters outside code blocks"""
        # Escape headers
        line = re.sub(r'^(#{1,6})(?!#)', lambda m: '\\' * len(m.group(1)) + m.group(1), line)
        
        # Escape other special characters
        special_chars = r'*_{}[]()#+-.!|`~'
        for char in special_chars:
            line = line.replace(char, f'\\{char}')
        
        # Preserve links and images
        line = re.sub(r'(!?\[.*?\])(\()', lambda m: m.group(1).replace('\\', '') + m.group(2), line)
        
        return line

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