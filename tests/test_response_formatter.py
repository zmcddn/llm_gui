import unittest
from pathlib import Path

from llm import MarkdownResponseFormatter

class TestMarkdownResponseFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = MarkdownResponseFormatter()
        self.sample_file = Path("docs/markdown_sample_output.md")
        with open(self.sample_file, "r", encoding="utf-8") as f:
            self.sample_content = f.read()

    def test_extract_section_think(self):
        """Test extracting thinking section"""
        thinking, _ = self.formatter.format_response(self.sample_content)
        self.assertTrue("Okay, so the user is asking for" in thinking)
        self.assertTrue("Putting it all together:" in thinking)

    def test_extract_section_output(self):
        """Test extracting output section"""
        _, output = self.formatter.format_response(self.sample_content)
        self.assertTrue("Customer Journey Flowchart" in output)
        self.assertTrue("Order Processing System" in output)
        self.assertTrue("ASCII art" in output)

    def test_process_mermaid_explicit_tags(self):
        """Test processing explicit mermaid tags"""
        content = """
<mermaid>
graph TD
    A-->B
    B-->C
</mermaid>
"""
        result = self.formatter._process_mermaid(content)
        self.assertTrue('<div class="mermaid">' in result)
        self.assertTrue('graph TD' in result)

    def test_process_mermaid_markdown_style(self):
        """Test processing markdown-style mermaid blocks"""
        content = """
```mermaid
graph TD
    A-->B
    B-->C
```
"""
        result = self.formatter._process_mermaid(content)
        self.assertTrue('<div class="mermaid">' in result)
        self.assertTrue('graph TD' in result)

    def test_empty_content(self):
        """Test handling empty content"""
        thinking, output = self.formatter.format_response("")
        self.assertEqual(thinking, "")
        self.assertEqual(output, "")

    def test_missing_tags(self):
        """Test handling content without think/output tags"""
        content = "Some random text without any tags"
        thinking, output = self.formatter.format_response(content)
        self.assertEqual(thinking, "")
        self.assertEqual(output, "")

    def test_multiple_mermaid_blocks(self):
        """Test handling multiple mermaid blocks"""
        content = """
<mermaid>
graph TD
    A-->B
</mermaid>

```mermaid
graph TD
    C-->D
```
"""
        result = self.formatter._process_mermaid(content)
        self.assertEqual(result.count('<div class="mermaid">'), 2)

    def test_malformed_mermaid(self):
        """Test handling malformed mermaid content"""
        content = """
<mermaid>
invalid mermaid content
</mermaid>
"""
        result = self.formatter._process_mermaid(content)
        self.assertTrue('<div class="mermaid">' in result)
        self.assertTrue('invalid mermaid content' in result)

    def test_nested_tags(self):
        """Test handling nested tags"""
        content = """
<think>
    Outer think
    <think>Inner think</think>
</think>
<output>
    Outer output
    <output>Inner output</output>
</output>
"""
        thinking, output = self.formatter.format_response(content)
        self.assertTrue('Outer think' in thinking)
        self.assertTrue('Inner think' in thinking)
        self.assertTrue('Outer output' in output)
        self.assertTrue('Inner output' in output)

    def test_markdown_formatting(self):
        """Test markdown formatting in output"""
        content = """
<output>
# Header
**Bold text**
*Italic text*
- List item 1
- List item 2
</output>
"""
        _, output = self.formatter.format_response(content)
        self.assertTrue('<h1>Header</h1>' in output)
        self.assertTrue('<strong>Bold text</strong>' in output)
        self.assertTrue('<em>Italic text</em>' in output)
        self.assertTrue('<li>List item 1</li>' in output)

    def test_markdown_list_formatting(self):
        """Test different types and levels of lists"""
        content = """
<output>
### 1. Customer Journey Flowchart
A visual representation of a customer's journey from awareness to purchase:

### 2. Order Processing System
A workflow for an order processing system:

### 3. State Machine Diagram
A state machine representing a user authentication system:

### 4. A simple one
- Bullet point 1
- Bullet point 2
  - Nested bullet 1
  - Nested bullet 2
    - Deep nested bullet
- Bullet point 3

1. Numbered item 1
2. Numbered item 2
   - Mixed bullet under number
   - Another bullet
3. Numbered item 3
</output>
"""
        _, output = self.formatter.format_response(content)

        # Check headers aren't converted to list items
        self.assertIn('<h3>1. Customer Journey Flowchart</h3>', output)
        self.assertIn('<h3>2. Order Processing System</h3>', output)

        # Check bullet points
        self.assertIn('<ul>', output)
        self.assertIn('<li>Bullet point 1</li>', output)

        # Check nested bullets
        self.assertIn('class="nested-list"', output)
        self.assertIn('<li>Nested bullet 1</li>', output)

        # Check numbered lists
        self.assertIn('<ol>', output)
        self.assertIn('<li>Numbered item 1</li>', output)

        # Check mixed list types
        self.assertIn('<li>Mixed bullet under number</li>', output)

    def test_markdown_headers_with_numbers(self):
        """Test headers that start with numbers aren't converted to lists"""
        content = """
<output>
# 1. Top Level Header
## 2.1 Second Level
### 3.1.1 Third Level

Regular text.

1. Actual numbered list
2. Second item
</output>
"""
        _, output = self.formatter.format_response(content)

        self.assertIn('<h1>1. Top Level Header</h1>', output)
        self.assertIn('<h2>2.1 Second Level</h2>', output)
        self.assertIn('<h3>3.1.1 Third Level</h3>', output)
        self.assertIn('<ol>', output)  # Only the actual list should be ordered

    def test_markdown_code_blocks(self):
        """Test code blocks with different languages"""
        content = """
<output>
```python
def hello():
    print("Hello")
```

```json
{
    "key": "value"
}
```
</output>
"""
        _, output = self.formatter.format_response(content)

        self.assertIn('<pre><code class="language-python">', output)
        self.assertIn('<pre><code class="language-json">', output)
        self.assertIn('def hello():', output)
        self.assertIn('"key": "value"', output)

if __name__ == '__main__':
    unittest.main()
