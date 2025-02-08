from dataclasses import dataclass

from styles import Styles


@dataclass
class HTMLStyle:
    bg_tertiary: str
    bg_secondary: str
    bg_primary: str
    text_primary: str
    accent: str
    border: str

    @classmethod
    def default(cls):
        return cls(
            bg_tertiary=Styles.BACKGROUND_TERTIARY,
            bg_secondary=Styles.BACKGROUND_SECONDARY,
            bg_primary=Styles.BACKGROUND_PRIMARY,
            text_primary=Styles.TEXT_PRIMARY,
            accent=Styles.ACCENT_COLOR,
            border=Styles.BORDER_COLOR,
        )


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
            ::-webkit-scrollbar {{
                width: 12px;
                height: 12px;
            }}
            ::-webkit-scrollbar-track {{
                background: {bg_tertiary};
            }}
            ::-webkit-scrollbar-thumb {{
                background: {bg_secondary};
                border-radius: 6px;
                border: 3px solid {bg_tertiary};
            }}
            ::-webkit-scrollbar-thumb:hover {{
                background: {accent};
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

    @staticmethod
    def apply_style(content: str, style: HTMLStyle = None) -> str:
        """Apply HTML styling to content"""
        if style is None:
            style = HTMLStyle.default()
        return HTMLTemplates.BASE.format(content=content, **style.__dict__)
