"""
Core HTML to Markdown conversion with BeautifulSoup cleanup
"""

from bs4 import BeautifulSoup, Comment
from markdownify import MarkdownConverter
import re
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
        self.current_conversion_blocks = []  # Per-conversion code block storage

    def convert(self, html_content):
        """
        Convert HTML content to cleaned Markdown format
        
        :param html_content: Raw HTML string input
        :return: Cleaned Markdown content string
        """
        try:
            self.current_conversion_blocks = []
            soup = BeautifulSoup(html_content, "html.parser")
            self._remove_unwanted_elements(soup)
            self._preserve_code_blocks(soup)
            self._wrap_raw_backticks(soup)  # New raw backtick handling
            return self._html_to_markdown(str(soup))
        except Exception as e:
            logging.error(f"Conversion error: {str(e)}")
            raise
        finally:
            self.current_conversion_blocks = []

    def _preserve_code_blocks(self, soup):
        """Handle formal code blocks with existing backtick sequences"""
        try:
            for pre in soup.find_all('pre'):
                code = pre.find('code')
                if code:
                    # Escape and store code content
                    content = code.text.replace('`', '\u200b`\u200b')
                    lang = self._get_code_language(code)
                    
                    self.current_conversion_blocks.append({
                        'content': content,
                        'language': lang
                    })
                    placeholder = f"CODEBLOCK_{len(self.current_conversion_blocks)-1}_END"
                    code.replace_with(placeholder)
        except Exception as e:
            logging.error(f"Code block preservation failed: {str(e)}")
            raise

    def _wrap_raw_backticks(self, soup):
        """Detect and wrap loose backtick sequences in code blocks"""
        for text_node in soup.find_all(string=True):
            if re.search(r'`{3,}', text_node):
                new_pre = soup.new_tag('pre')
                new_code = soup.new_tag('code')
                new_code.string = text_node
                new_pre.append(new_code)
                text_node.replace_with(new_pre)

    def _get_code_language(self, element):
        """Detect code language from class names"""
        classes = element.get('class', [])
        for cls in classes:
            if cls.startswith('language-'):
                return cls.split('-', 1)[1]
            if cls in ['python', 'js', 'javascript', 'html', 'css', 'bash']:
                return cls
        return ''

    def _remove_unwanted_elements(self, soup):
        """Comprehensive HTML cleanup"""
        # Remove comments
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()

        # Remove by CSS selectors
        for selector in self._remove_selectors:
            for el in soup.select(selector):
                el.decompose()

        # Remove by tag names
        for tag in self.strip_tags:
            for el in soup.find_all(tag):
                el.decompose()

        # Clean empty containers
        for el in soup.find_all():
            if not el.contents and not el.text.strip():
                el.decompose()

    def _html_to_markdown(self, html):
        """Convert HTML to Markdown with proper block state handling"""
        class CodeSafeConverter(MarkdownConverter):
            def __init__(self, blocks=None, **kwargs):
                super().__init__(**kwargs)
                self.blocks = blocks or []  # Initialize blocks properly

            def convert_pre(self, el, text, convert_as_inline=False):
                match = re.search(r'CODEBLOCK_(\d+)_END', text)
                if match:
                    idx = int(match.group(1))
                    try:
                        block = self.blocks[idx]
                        content = block['content'].replace('\u200b`\u200b', '`')
                        max_backticks = max(len(m.group(0)) for m in re.finditer(r'`+', content)) if '`' in content else 0
                        fence_length = max(4, max_backticks + 1)
                        fence = '`' * fence_length
                        lang = f"{block['language']}\n" if block['language'] else ''
                        return f"\n{fence}{lang}{content}\n{fence}\n"
                    except IndexError:
                        logging.error(f"Missing code block at index {idx}")
                return super().convert_pre(el, text, convert_as_inline)

        # Pass blocks explicitly to the converter
        converter = CodeSafeConverter(
            blocks=self.current_conversion_blocks,
            heading_style="ATX",
            bullets="-*",
            strip=self.strip_tags,
            convert_links=self.convert_links,
            escape_underscores=False
        )
        
        markdown = converter.convert(html)
        return self._normalize_code_fences(markdown)

    def _normalize_code_fences(self, markdown):
        """Finalize code fence formatting"""
        # Clean temporary fence markers
        markdown = re.sub(r'(`+)x0', r'\1', markdown)
        
        lines = markdown.split('\n')
        output = []
        fence_stack = []
        current_fence = None

        for line in lines:
            fence_match = re.match(r'^(?P<fence>`{4,})', line)
            if fence_match:
                fence = fence_match.group('fence')
                if not fence_stack:
                    fence_stack.append(fence)
                    output.append(fence)
                else:
                    expected = fence_stack.pop()
                    output.append(expected)
            else:
                output.append(line)

        # Close any remaining open fences
        while fence_stack:
            output.append(fence_stack.pop())

        # Escape loose triple+ backticks outside code blocks
        return self._escape_loose_backticks('\n'.join(output))

    def _escape_loose_backticks(self, markdown):
        """Escape remaining backtick sequences in normal text"""
        in_code_block = False
        buffer = []
        
        for line in markdown.split('\n'):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                buffer.append(line)
                continue
            
            if not in_code_block:
                line = re.sub(r'(?<!`)``+(?!`)', lambda m: '\\' * len(m.group(0)) + m.group(0), line)
            
            buffer.append(line)
        
        return '\n'.join(buffer)