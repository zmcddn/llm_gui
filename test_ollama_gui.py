import sys
import unittest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication, QTextEdit
from PySide6.QtWebEngineWidgets import QWebEngineView
from main import OllamaGUI, CollapsibleFrame
import json
import tempfile

# Create QApplication instance for tests
app = QApplication(sys.argv)

class TestOllamaGUI(unittest.TestCase):
    def setUp(self):
        self.gui = OllamaGUI()

    def test_initial_state(self):
        """Test initial state of the GUI"""
        self.assertIsNotNone(self.gui.model_panel)
        self.assertIsNotNone(self.gui.thinking_panel)
        self.assertIsNotNone(self.gui.output_panel)
        self.assertIsNotNone(self.gui.raw_panel)

        # Test that output panel uses QWebEngineView
        self.assertIsInstance(self.gui.output_panel.display, QWebEngineView)
        # Test that thinking panel uses QTextEdit
        self.assertIsInstance(self.gui.thinking_panel.display, QTextEdit)

    def test_format_prompt(self):
        """Test prompt formatting"""
        test_input = "Hello, world!"
        formatted = self.gui._format_prompt(test_input)
        self.assertIn("<think>", formatted)
        self.assertIn("<output>", formatted)
        self.assertIn("<mermaid>", formatted)
        self.assertIn(test_input, formatted)

    @patch('requests.post')
    def test_call_ollama_api(self, mock_post):
        """Test API call functionality"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        response = self.gui._call_ollama_api("test input")
        self.assertEqual(response, mock_response)
        mock_post.assert_called_once()

    def test_extract_thinking_content(self):
        """Test thinking content extraction"""
        test_response = "<think>Testing thoughts</think>"
        content = self.gui._extract_thinking_content(test_response,
            pattern=self.gui._process_streaming_response.__defaults__[0]['think'])
        self.assertEqual(content, "Testing thoughts")

    def test_extract_output_content(self):
        """Test output content extraction"""
        test_response = "<output>Test output</output>"
        content = self.gui._extract_output_content(test_response,
            pattern=self.gui._process_streaming_response.__defaults__[0]['output'])
        self.assertEqual(content, "Test output")

    def test_generate_html_output(self):
        """Test HTML generation with various content types"""
        test_cases = [
            # Test Markdown
            {
                "input": "# Header\n**Bold**",
                "expected": ["<h1>Header</h1>", "<strong>Bold</strong>"]
            },
            # Test Mermaid
            {
                "input": "<mermaid>graph TD\nA-->B</mermaid>",
                "expected": ['<div class="mermaid">', "graph TD", "A-->B"]
            },
            # Test Code Blocks
            {
                "input": "```python\nprint('hello')\n```",
                "expected": ["<pre>", "<code>", "print('hello')"]
            },
            # Test Tables
            {
                "input": "| Header |\n|--------|",
                "expected": ["<table>", "<th>", "Header"]
            }
        ]

        for case in test_cases:
            html = self.gui._generate_html_output(case["input"])
            for expected in case["expected"]:
                self.assertIn(expected, html)
            # Check for required HTML structure
            self.assertIn("<html>", html)
            self.assertIn("<head>", html)
            self.assertIn("<body>", html)
            self.assertIn("mermaid.initialize", html)

    def test_display_html_in_output(self):
        """Test HTML display handling for different widget types"""
        test_html = "<p>Test</p>"
        # Should not raise any errors
        self.gui._display_html_in_output(test_html)

        # Test with both widget types
        self.assertIsInstance(self.gui.output_panel.display, QWebEngineView)
        self.assertIsInstance(self.gui.thinking_panel.display, QTextEdit)

    def test_model_selector(self):
        """Test model selector functionality"""
        self.assertIsNotNone(self.gui.model_selector)
        self.assertTrue(self.gui.model_selector.count() > 0)

    def test_chat_history(self):
        """Test chat history management"""
        test_input = "Test message"
        self.gui.model_input.setPlainText(test_input)
        self.gui.process_input()
        self.assertEqual(len(self.gui.chat_history), 1)
        self.assertEqual(self.gui.chat_history[0]["content"], test_input)

    @patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
    def test_load_conversation(self, mock_file_dialog):
        """Test conversation loading"""
        test_data = {
            "model": "deepseek-r1:32b",
            "history": [{"role": "user", "content": "test"}]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as tf:
            json.dump(test_data, tf)
            tf.flush()
            mock_file_dialog.return_value = (tf.name, "JSON Files (*.json)")

            self.gui.load_conversation()
            self.assertEqual(self.gui.chat_history, test_data["history"])
            self.assertEqual(self.gui.model_selector.currentText(), test_data["model"])

class TestCollapsibleFrame(unittest.TestCase):
    def setUp(self):
        self.frame = CollapsibleFrame("Test Frame")

    def test_initial_state(self):
        """Test initial state of CollapsibleFrame"""
        self.assertFalse(self.frame.is_collapsed)
        self.assertTrue(self.frame.content.isVisible())

    def test_toggle_content(self):
        """Test content toggling"""
        # Test collapsing
        self.frame.toggle_content()
        self.assertTrue(self.frame.is_collapsed)
        self.assertFalse(self.frame.content.isVisible())
        self.assertEqual(self.frame.content.maximumHeight(), 0)

        # Test expanding
        self.frame.toggle_content()
        self.assertFalse(self.frame.is_collapsed)
        self.assertTrue(self.frame.content.isVisible())
        self.assertEqual(self.frame.content.maximumHeight(), 16777215)

if __name__ == '__main__':
    unittest.main()
