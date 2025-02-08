class HTMLTemplates:
    BASE = """
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <style>
            body {{
                background-color: {bg_tertiary};
                color: {text_primary};
                font-family: 'Consolas', 'Menlo', 'Monaco', monospace;
                padding: 8px;
                margin: 0;
            }}
            pre {{
                background-color: {bg_secondary};
                padding: 8px;
                border-radius: 4px;
                overflow-x: auto;
            }}
            code {{
                font-family: 'Consolas', 'Menlo', 'Monaco', monospace;
            }}
            a {{
                color: {accent};
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 8px 0;
            }}
            th, td {{
                border: 1px solid {border};
                padding: 6px;
            }}
            th {{
                background-color: {bg_secondary};
            }}
            .mermaid {{
                background-color: {bg_secondary};
                padding: 8px;
                border-radius: 4px;
                margin: 8px 0;
            }}
            h3 {{
                margin-top: 16px;
                margin-bottom: 8px;
                color: {text_primary};
            }}
            hr {{
                border: none;
                border-top: 1px solid {border};
                margin: 16px 0;
            }}
        </style>
    </head>
    <body>
        {content}
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'dark',
                themeVariables: {{
                    'background-color': '{bg_secondary}',
                    'primaryColor': '{accent}',
                    'primaryTextColor': '{text_primary}',
                    'primaryBorderColor': '{border}',
                    'lineColor': '{text_primary}',
                    'secondaryColor': '{bg_tertiary}',
                    'tertiaryColor': '{bg_primary}'
                }},
                securityLevel: 'loose',
                fontFamily: 'Consolas, Menlo, Monaco, monospace'
            }});
            // Force mermaid to render after a short delay
            setTimeout(function() {{
                mermaid.init(undefined, document.querySelectorAll('.mermaid'));
            }}, 500);
        </script>
    </body>
    </html>
    """

    ERROR = """
    <h3 style="color: {error_color};">Error Occurred</h3>
    <p>{message}</p>
    """

    LOADING = """
    <h3 style="color: {text_secondary};">
        Processing... Please wait while I prepare your response.
    </h3>
    """
