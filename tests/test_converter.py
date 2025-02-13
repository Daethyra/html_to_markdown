"""
Unit tests for HTMLToMarkdownConverter (properly escaped)
"""

import pytest
from context_converter.converter import HTMLToMarkdownConverter

@pytest.fixture
def converter():
    return HTMLToMarkdownConverter()

def test_headings(converter):
    html = """
    <h1>Main</h1>
    <h2>Sub <span>heading</span></h2>
    """
    expected = r"""
# Main

## Sub heading
    """.strip()
    assert converter.convert(html) == expected

def test_paragraphs(converter):
    html = """
    <p>First</p>
    <p>Second<br>with<br/>breaks</p>
    """
    expected = "First\n\nSecond  \nwith  \nbreaks"
    assert converter.convert(html) == expected

def test_lists(converter):
    html = """
    <ul><li>Item</li></ul>
    <ol start="2"><li>Ordered</li></ol>
    """
    expected = "- Item\n\n2. Ordered"
    assert converter.convert(html) == expected

def test_tables(converter):
    html = """
    <table>
      <tr><th>Head</th></tr>
      <tr><td>Data</td></tr>
    </table>
    """
    expected = "| Head |\n|------|\n| Data |"
    assert converter.convert(html) == expected

def test_code_blocks(converter):
    html = """
    <pre><code class="language-py">print()</code></pre>
    <code>inline</code>
    """
    expected = "```py\nprint()\n```\n\n`inline`"
    assert converter.convert(html) == expected

def test_links(converter):
    html = '<a href="/link" title="tooltip">Text</a>'
    expected = r'[Text](/link "tooltip")'
    assert converter.convert(html) == expected

def test_images(converter):
    html = '<img src="img.jpg" alt="Alt text" title="Image">'
    expected = '![Alt text](img.jpg "Image")'
    assert converter.convert(html) == expected

def test_special_chars(converter):
    html = "<p>*Stars* &amp; &lt;tags&gt;</p>"
    expected = r"\*Stars\* & <tags>"
    assert converter.convert(html) == expected

def test_element_removal(converter):
    html = """
    <header>Header</header>
    <script>alert();</script>
    <div class="cookie">Cookies</div>
    <nav>Nav</nav>
    """
    assert converter.convert(html).strip() == ""

def test_mixed_content(converter):
    html = """
    <div>
        <h3>Mix</h3>
        <p>Text with <em>emphasis</em></p>
        <ul>
            <li><a href="#"><strong>Bold</strong> link</a></li>
        </ul>
    </div>
    """
    expected = """
### Mix

Text with *emphasis*

- [**Bold** link](#)
    """.strip()
    assert converter.convert(html) == expected