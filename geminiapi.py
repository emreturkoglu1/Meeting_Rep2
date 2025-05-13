import requests
import json
import os
import re

API_KEY = "AIzaSyDWc6YD_9vys2xUaGAAQwnvvTRnLX_FnlQ"  # Replace with your actual API key

# Güncellenmiş API modeli ve URL
MODEL = "gemini-1.5-flash"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

headers = {
    "Content-Type": "application/json"
}

# Function to add CSS for better styling when converted to PDF
def add_styling_to_markdown(markdown_content):
    css_style = """
<style>
body {
font-family: 'Arial', sans-serif;
line-height: 1.6;
color: #333;
max-width: 900px;
margin: 0 auto;
padding: 20px;
}
h1 {
color: #2c3e50;
border-bottom: 2px solid #3498db;
padding-bottom: 10px;
font-size: 28px;
}
h2 {
color: #2980b9;
border-bottom: 1px solid #bdc3c7;
padding-bottom: 5px;
margin-top: 25px;
font-size: 22px;
}
table {
border-collapse: collapse;
width: 100%;
margin: 20px 0;
}
th, td {
border: 1px solid #ddd;
padding: 12px;
text-align: left;
}
th {
background-color: #f2f2f2;
font-weight: bold;
}
tr:nth-child(even) {
background-color: #f9f9f9;
}
ul, ol {
padding-left: 20px;
}
li {
margin-bottom: 5px;
}
.priority-high {
color: #e74c3c;
font-weight: bold;
}
.priority-medium {
color: #f39c12;
}
.priority-low {
color: #27ae60;
}
.emotion-neutral {
color: #7f8c8d;
}
.emotion-happy {
color: #2ecc71;
}
.emotion-sad {
color: #3498db;
}
.emotion-surprised {
color: #9b59b6;
}
.emotion-angry {
color: #e74c3c;
}
.report-section {
background-color: #f9f9f9;
border-left: 4px solid #3498db;
padding: 15px;
margin: 15px 0;
border-radius: 0 5px 5px 0;
}
hr {
border: 0;
height: 1px;
background: #ddd;
margin: 30px 0;
}
</style>
"""
    # Check if the markdown content already has a CSS style tag
    if "<style>" in markdown_content:
        return markdown_content
    else:
        return css_style + "\n" + markdown_content

# Function to clean emojis from the text
def clean_emojis(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# ReportLab ile PDF oluşturma - stil çakışması düzeltildi
def create_pdf_from_markdown(markdown_path, pdf_path):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    # Markdown içeriğini oku
    with open(markdown_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # CSS stilini kaldır (PDF'e dahil edilmeyecek)
    if "<style>" in markdown_content and "</style>" in markdown_content:
        style_start = markdown_content.find("<style>")
        style_end = markdown_content.find("</style>") + len("</style>")
        markdown_content = markdown_content[style_end:]
    
    # PDF dökümanını oluştur
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Özel stiller - yeni isimler vererek çakışmayı önle
    title_style = styles['Title']
    heading1_style = ParagraphStyle(
        name='CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=10
    )
    heading2_style = ParagraphStyle(
        name='CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8
    )
    normal_style = styles['Normal']
    
    # PDF içeriğini oluştur
    story = []
    
    # Satır satır işle
    current_list = []
    in_list = False
    in_table = False
    table_data = []
    table_headers = []
    
    for line in markdown_content.split('\n'):
        line = line.strip()
        
        if not line:
            # Boş satır
            if in_list:
                # Listeyi sonlandır ve PDF'e ekle
                story.append(Spacer(1, 6))
                in_list = False
            continue
            
        if line.startswith('# '):
            # Başlık 1
            story.append(Paragraph(line[2:], title_style))
        elif line.startswith('## '):
            # Başlık 2
            story.append(Paragraph(line[3:], heading1_style))
        elif line.startswith('### '):
            # Başlık 3
            story.append(Paragraph(line[4:], heading2_style))
        elif line.startswith('- '):
            # Liste öğesi
            if not in_list:
                in_list = True
            story.append(Paragraph('• ' + line[2:], normal_style))
        elif line.startswith('|') and not in_table:
            # Tablo başlangıcı
            in_table = True
            header_cells = [cell.strip() for cell in line.split('|')[1:-1]]
            table_headers = header_cells
        elif line.startswith('|') and in_table and '---' in line:
            # Tablo ayırıcı satırı, yoksay
            continue
        elif line.startswith('|') and in_table:
            # Tablo satırı
            row_cells = [cell.strip() for cell in line.split('|')[1:-1]]
            table_data.append(row_cells)
        elif line.startswith('---'):
            # Yatay çizgi
            story.append(Spacer(1, 10))
        else:
            # Normal metin
            story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 6))
    
        # Tabloyu işle
        if in_table and (not line.startswith('|') or not line):
            # Tablo bitti
            in_table = False
            
            if table_headers and table_data:
                # Tablo verileri ve başlıkları varsa, tabloyu oluştur
                all_data = [table_headers] + table_data
                table = Table(all_data)
                
                # Tablo stili
                table_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ])
                
                table.setStyle(table_style)
                story.append(table)
                story.append(Spacer(1, 12))
                
                # Tablo verilerini temizle
                table_headers = []
                table_data = []
    
    # PDF oluştur
    doc.build(story)
    print(f"ReportLab ile PDF dosyası oluşturuldu: {pdf_path}")
    return True

# Fallback rapor oluşturma fonksiyonu
def create_fallback_report():
    # Basit bir rapor oluştur
    fallback_report = """<style>
body {
font-family: 'Arial', sans-serif;
line-height: 1.6;
color: #333;
max-width: 900px;
margin: 0 auto;
padding: 20px;
}
h1 {
color: #2c3e50;
border-bottom: 2px solid #3498db;
padding-bottom: 10px;
font-size: 28px;
}
h2 {
color: #2980b9;
border-bottom: 1px solid #bdc3c7;
padding-bottom: 5px;
margin-top: 25px;
font-size: 22px;
}
table {
border-collapse: collapse;
width: 100%;
margin: 20px 0;
}
th, td {
border: 1px solid #ddd;
padding: 12px;
text-align: left;
}
th {
background-color: #f2f2f2;
font-weight: bold;
}
tr:nth-child(even) {
background-color: #f9f9f9;
}
ul, ol {
padding-left: 20px;
}
li {
margin-bottom: 5px;
}
.priority-high {
color: #e74c3c;
font-weight: bold;
}
.priority-medium {
color: #f39c12;
}
.priority-low {
color: #27ae60;
}
hr {
border: 0;
height: 1px;
background: #ddd;
margin: 30px 0;
}
</style>
# Meeting Summary Report

## Executive Overview
This meeting report was automatically generated from the uploaded meeting recording. The API integration is currently having temporary issues.

## Meeting Details
- **Date**: Auto-generated report
- **Participants**: Extracted from audio diarization
- **Duration**: Based on transcript timestamps

## Transcript Summary
The full transcript is available in the transcript.txt file.
"""
    
    # Raporu kaydet
    markdown_path = os.path.join('custom_output', 'meeting_report.md')
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(fallback_report)
    
    print("✅ Simple fallback report created successfully!")
    
    # PDF oluştur
    pdf_path = os.path.join('custom_output', 'meeting_report.pdf')
    try:
        create_pdf_from_markdown(markdown_path, pdf_path)
    except Exception as e:
        print(f"❌ Error creating PDF from fallback report: {str(e)}")

# Test için transcript içeriğini oku, eğer yoksa boş döndür
transcript = ""
transcript_path = os.path.join('custom_output', 'transcript.txt')
try:
    if os.path.exists(transcript_path):
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
except Exception:
    pass

# Define your prompt as a single string
prompt = f"""
Generate a professional meeting report following this exact markdown format. Your response should be immediately usable as a markdown document.
Do not include any introductory text or additional explanations.

# Meeting Summary Report

## Executive Overview
[Provide a concise 3-4 sentence overview of the entire meeting. Highlight the main purpose and key outcomes.]

## Meeting Details
- **Date**: [Extract or estimate based on discussion]
- **Duration**: [Calculate from transcript timestamps]
- **Participants**: [List all speakers identified in the transcript]
- **Topics Covered**: [List 3-5 main topics discussed]

## Key Discussion Points
[Provide 3-5 bullet points highlighting the most important discussions]
- [Key point 1]
- [Key point 2]
- [Key point 3]

## Decisions Made
[List all decisions or conclusions reached during the meeting. If none are explicitly stated, derive them from the context.]
- [Decision 1]
- [Decision 2]
- [Decision 3]

## Action Items
| Action | Assigned To | Due Date | Priority |
|--------|-------------|----------|----------|
| [Action 1] | [Person] | [Date if mentioned] | [High/Medium/Low] |
| [Action 2] | [Person] | [Date if mentioned] | [High/Medium/Low] |
| [Action 3] | [Person] | [Date if mentioned] | [High/Medium/Low] |

## Follow-up Required
[List any topics that need to be addressed in future meetings or require additional discussion]
- [Follow-up 1]
- [Follow-up 2]

## Facial Expression Analysis
### Overall Emotion Distribution
[Calculate and report the percentage distribution of different emotions detected during the meeting]
[Identify and highlight the most prevalent emotions]

## Key Insights & Recommendations
[Provide 2-3 paragraphs of analysis and recommendations based on the meeting content]

## Meeting Effectiveness Assessment
[Evaluate the overall effectiveness of the meeting based on clarity of purpose, participant engagement, time management, decision-making, and action planning]

---

### Transcript Summary
[Provide a condensed version of the transcript focusing only on the substantive exchanges]

Transcript:
{transcript}
"""

data = {
    "contents": [{
        "parts": [{"text": prompt}]
    }],
    "generationConfig": {
        "temperature": 0.2,
        "topP": 0.8,
        "topK": 40,
        "maxOutputTokens": 4096
    }
}

# API isteğini yap ve raporu kaydet
try:
    # Gemini API kullanarak rapor oluşturalım
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    # API yanıtını kontrol et ve debug bilgisi ekle
    print(f"API Response Status: {response.status_code}")
    if response.status_code != 200:
        print(f"API Error Response: {response.text}")
    
    response_data = response.json()
    
    # API yanıtını kontrol et
    if "candidates" in response_data and len(response_data["candidates"]) > 0:
        generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        
        # Emoji karakterlerini temizle
        cleaned_text = clean_emojis(generated_text)
        
        # Markdown içeriğine CSS stil ekle
        styled_text = add_styling_to_markdown(cleaned_text)
        
        # Raporu kaydet
        markdown_path = os.path.join('custom_output', 'meeting_report.md')
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(styled_text)
        
        print("✅ Meeting report generated successfully with Gemini API!")
        
        # PDF oluştur
        pdf_path = os.path.join('custom_output', 'meeting_report.pdf')
        create_pdf_from_markdown(markdown_path, pdf_path)
        
    else:
        print("❌ API error: No candidates in response")
        if "error" in response_data:
            print(f"API error: {response_data['error']['message']}")
        
        # Fallback olarak basit bir rapor oluştur
        create_fallback_report()
        
except Exception as e:
    print(f"❌ Error generating report with Gemini API: {str(e)}")
    # Fallback olarak basit bir rapor oluştur
    create_fallback_report()

# End of file