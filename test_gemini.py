import os
import geminiapi
import requests
import json
from datetime import datetime

# Test transcript dosyasını oluştur
transcript = """
SPEAKER_00: Hello everyone. Welcome to our meeting.
SPEAKER_01: Hello, good to see you all today.
SPEAKER_00: Let's discuss the project status.
SPEAKER_01: I think we're making good progress.
"""

# Klasörü kontrol et ve oluştur
output_dir = 'custom_output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Transcript dosyasını oluştur
transcript_path = os.path.join(output_dir, 'transcript.txt')
with open(transcript_path, 'w', encoding='utf-8') as f:
    f.write(transcript)
print(f"Transcript dosyası oluşturuldu: {transcript_path}")

# Özel prompt oluşturma (transcripti kullanarak)
prompt = f"""
Generate a professional meeting report following this exact markdown format. Your response should be immediately usable as a markdown document.
Do not include any introductory text or additional explanations.

# Meeting Summary Report

## Executive Overview
[Provide a concise 3-4 sentence overview of the entire meeting. Highlight the main purpose and key outcomes.]

## Meeting Details
- **Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Duration**: [Calculate from transcript timestamps]
- **Number of Active Participants**: [Count of unique speakers from transcript but not their names]
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

# Gemini API için veri hazırlama
api_data = {
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

# API çağrısı ve rapor oluşturma
try:
    # API model ve URL bilgisini kontrol et
    print(f"Using API model: {geminiapi.MODEL}")
    print(f"Using API URL: {geminiapi.url}")
    
    # API isteği yap
    response = requests.post(geminiapi.url, headers=geminiapi.headers, data=json.dumps(api_data))
    
    # Debug için yanıt kodunu kontrol et
    print(f"API Response Status: {response.status_code}")
    
    # API yanıtını işle
    if response.status_code == 200:
        response_data = response.json()
        
        # API yanıtını kontrol et
        if "candidates" in response_data and len(response_data["candidates"]) > 0:
            generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Emoji karakterlerini temizle
            cleaned_text = geminiapi.clean_emojis(generated_text)
            
            # Markdown içeriğine CSS stil ekle
            styled_text = geminiapi.add_styling_to_markdown(cleaned_text)
            
            # Raporu kaydet
            markdown_path = os.path.join(output_dir, 'meeting_report.md')
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(styled_text)
            
            print(f"✅ Rapor başarıyla oluşturuldu: {markdown_path}")
            
            # PDF oluştur
            pdf_path = os.path.join(output_dir, 'meeting_report.pdf')
            geminiapi.create_pdf_from_markdown(markdown_path, pdf_path)
            
            print(f"✅ PDF başarıyla oluşturuldu: {pdf_path}")
        else:
            print("❌ API error: No candidates in response")
            if "error" in response_data:
                print(f"API error: {response_data['error']['message']}")
            
            # Fallback olarak basit bir rapor oluştur
            geminiapi.create_fallback_report()
    else:
        print(f"❌ API error: HTTP status {response.status_code}")
        print(f"Error details: {response.text}")
        
        # Fallback olarak basit bir rapor oluştur
        geminiapi.create_fallback_report()
        
except Exception as e:
    print(f"❌ Error generating report with Gemini API: {str(e)}")
    # Fallback olarak basit bir rapor oluştur
    geminiapi.create_fallback_report()

print("Test tamamlandı!") 