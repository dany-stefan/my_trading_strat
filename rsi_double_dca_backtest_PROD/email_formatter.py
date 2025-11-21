"""
Shared email formatting utilities for RSI strategy monitoring
"""

def convert_to_html(text):
    """Convert plain text email to HTML with styled tables matching markdown format."""
    html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 10px;
            line-height: 1.7;
            color: #333;
            font-size: 17px;
            -webkit-text-size-adjust: 100%;
            margin: 0;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            max-width: 100%;
            margin: 0 auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            font-size: 26px;
            font-weight: 700;
            margin: 20px 0 25px 0;
            line-height: 1.3;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            border-bottom: 3px solid #34495e;
            padding-bottom: 12px;
            font-size: 21px;
            font-weight: 700;
            line-height: 1.4;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            font-size: 15px;
            table-layout: fixed;
            overflow-x: auto;
            display: block;
        }
        th {
            background-color: #3498db;
            color: white;
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
            border: 1px solid #2980b9;
            font-size: 13px;
            word-wrap: break-word;
            line-height: 1.3;
        }
        td {
            padding: 10px 8px;
            border: 1px solid #ddd;
            background-color: white;
            font-size: 15px;
            word-wrap: break-word;
            line-height: 1.4;
        }
        tbody td {
            background-color: white !important;
            color: #333 !important;
        }
        tbody tr:nth-child(even) td {
            background-color: #f8f9fa !important;
        }
        .status-box {
            background-color: #d4edda;
            border-left: 5px solid #28a745;
            padding: 18px;
            margin: 20px 0;
            border-radius: 6px;
            font-size: 17px;
        }
        .warning-box {
            background-color: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 18px;
            margin: 20px 0;
            border-radius: 6px;
            font-size: 17px;
        }
        .test-notice {
            background-color: #cce5ff;
            border: 3px solid #2196f3;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
        }
        .info-section {
            background-color: #f8f9fa;
            padding: 16px;
            border-radius: 6px;
            margin: 12px 0;
            border-left: 4px solid #6c757d;
            font-size: 16px;
            line-height: 1.6;
        }
        .divider {
            border: none;
            border-top: 4px double #34495e;
            margin: 30px 0;
            height: 4px;
        }
        p {
            margin: 14px 0;
            font-size: 17px;
            line-height: 1.6;
        }
        strong {
            color: #2c3e50;
            font-weight: 700;
        }
        em {
            font-style: italic;
            color: #555;
        }
        .section-title {
            font-size: 19px;
            font-weight: 700;
            color: #2c3e50;
            margin: 25px 0 15px 0;
            line-height: 1.4;
        }
        .number-step {
            font-size: 18px;
            font-weight: 700;
            color: #3498db;
            margin: 15px 0;
            line-height: 1.5;
        }
        @media only screen and (max-width: 600px) {
            .container {
                padding: 12px;
            }
            table {
                font-size: 14px;
                display: block;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }
            th {
                padding: 10px 6px;
                font-size: 12px;
                line-height: 1.2;
            }
            td {
                padding: 10px 6px;
                font-size: 14px;
                line-height: 1.3;
            }
            td:first-child {
                font-weight: 600;
                min-width: 100px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
"""
    
    # Process the text line by line
    lines = text.split('\n')
    in_table = False
    table_headers = []
    
    for line in lines:
        # Detect test mode notice
        if '🧪 THIS IS A TEST EMAIL' in line or 'PREVIEW ONLY' in line:
            html += f'<div class="test-notice">{line}</div>\n'
        # Detect main header
        elif line.startswith('🎯 RSI STRATEGY MONITOR'):
            html += f'<h1>{line}</h1>\n'
        # Skip ASCII divider lines completely
        elif line.startswith('════') or line.startswith('═══'):
            continue
        # Detect ASCII table borders (ignore them)
        elif line.startswith('┌─') or line.startswith('├─') or line.startswith('└─'):
            continue
        # Detect markdown-style table header row
        elif not in_table and '|' in line and ('Rank' in line or 'Variant' in line or 'Cadence' in line or 'Strategy' in line):
            in_table = True
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            table_headers = cells
            html += '<table>\n<thead>\n<tr>'
            for cell in cells:
                html += f'<th>{cell}</th>'
            html += '</tr>\n</thead>\n<tbody>\n'
        # Detect markdown table separator row (|-----|-----|)
        elif in_table and '|' in line and '---' in line:
            continue
        # Detect markdown table data rows (when already in a table)
        elif in_table and '|' in line and line.strip().startswith('|'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            # All data rows are white (removed highlight logic)
            html += f'<tr>'
            for cell in cells:
                # Remove markdown bold markers
                cell = cell.replace('**', '')
                html += f'<td>{cell}</td>'
            html += '</tr>\n'
        # Detect end of table (empty line after table rows)
        elif in_table and not line.strip():
            html += '</tbody>\n</table>\n'
            in_table = False
            html += '<br>\n'
        # ASCII table rows with │
        elif line.startswith('│') and not in_table:
            # Skip ASCII table rows - we handle markdown tables instead
            continue
        # Regular content
        else:
            # Close table if we're in a table and encounter non-table content
            if in_table and '|' not in line:
                html += '</tbody>\n</table>\n'
                in_table = False
                html += '<br>\n'
            
            if line.strip():
                # Status boxes
                if line.startswith('🔥 RECOMMENDATION') or line.startswith('✅ RAINY'):
                    html += f'<div class="status-box"><strong>{line}</strong></div>\n'
                elif line.startswith('⚠️') or line.startswith('💰 RECOMMENDATION'):
                    html += f'<div class="warning-box"><strong>{line}</strong></div>\n'
                # Section headers with emojis
                elif line.startswith('📊') or line.startswith('📈') or line.startswith('💵'):
                    html += f'<h2>{line}</h2>\n'
                # Numbered steps (1️⃣, 2️⃣, etc.)
                elif '1️⃣' in line or '2️⃣' in line or '3️⃣' in line:
                    html += f'<p class="number-step">{line}</p>\n'
                # Info sections (bullet points)
                elif line.startswith('•'):
                    # Make text after colon bold
                    if ':' in line:
                        parts = line.split(':', 1)
                        html += f'<div class="info-section"><strong>{parts[0]}:</strong> {parts[1]}</div>\n'
                    else:
                        html += f'<div class="info-section">{line}</div>\n'
                # Numbered lists
                elif len(line) > 2 and line[0].isdigit() and line[1] == '.':
                    html += f'<div class="info-section">{line}</div>\n'
                # Key Metrics or special labels
                elif line.startswith('Key Metrics:') or line.startswith('Your Choice') or line.startswith('Expected Long-Term'):
                    html += f'<p class="section-title">{line}</p>\n'
                # Lines with checkmarks
                elif line.startswith('✅') or line.startswith('✔️'):
                    html += f'<p><strong>{line}</strong></p>\n'
                # Regular paragraphs - check for inline formatting
                else:
                    # Convert markdown-style bold (**text**) to HTML
                    formatted_line = line
                    import re
                    # Bold: **text** -> <strong>text</strong>
                    formatted_line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', formatted_line)
                    # Italic: *text* -> <em>text</em> (single asterisk not part of bold)
                    formatted_line = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', formatted_line)
                    html += f'<p>{formatted_line}</p>\n'
            else:
                html += '<br>\n'
    
    # Close any open table
    if in_table:
        html += '</tbody>\n</table>\n'
    
    html += """
    </div>
</body>
</html>
"""
    
    return html
