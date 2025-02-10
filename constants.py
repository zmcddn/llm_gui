MODEL_LIST = [
    "deepseek-r1:32b",
    "deepseek-r1:8b",
    "deepseek-r1:1.5b",
    "llama2",
    "mistral",
    "codellama",
]
APP_NAME = "Ollama GUI"
FORMATTING_INSTRUCTIONS = """
Please format your response with <think> tags for your thinking process and <output> tags for the final response. If you need to include any chart, please use Mermaid syntax within <mermaid> tags.

Example format:
<think>
Here's my thinking process...
</think>
<output>
Here's my final response...
(Can include mermaid diagrams like this:)
<mermaid>
graph TD
    A-->B
</mermaid>
</output>
"""
