# Meeting Expression Analyzer

This project analyzes meeting recordings by combining audio diarization (speaker identification) with facial expression recognition to create comprehensive meeting reports.

## Features

- **Video Processing**: Extract audio and video from meeting recordings
- **Audio Diarization**: Identify different speakers in the meeting
- **Speech-to-Text**: Convert spoken words to text with timestamps
- **Facial Expression Analysis**: Analyze participant emotions during the meeting
- **Report Generation**: Create comprehensive PDF meeting reports
- **Email Integration**: Send reports directly to specified email addresses

## Installation

1. Clone this repository:
```bash
git clone https://github.com/emreturkoglu1/Meeting_Rep2.git
cd meeting-expression-analyzer
```

2. Create a virtual environment:
```bash
python -m venv meetingenv
```

3. Activate the virtual environment:
   - Windows: `meetingenv\Scripts\activate`
   - MacOS/Linux: `source meetingenv/bin/activate`

4. Install required Python packages:
```bash
pip install -r requirements.txt
```

5. Install markdown-pdf globally using npm:
```bash
npm install -g markdown-pdf
```

## Usage

### Web Interface

1. Start the web server:
```bash
python parser.py
```

2. Open your browser and navigate to `http://localhost:8000`

3. Upload your meeting recording video through the interface

4. Provide your email address to receive the report

5. Download the processed results and analysis

### Email Service

The application can send reports directly to your email:

```bash
python send_meeting_report.py --recipient your@email.com --report path/to/report.pdf
```

## Project Structure

- `parser.py`: Main web server and processing pipeline
- `audio_diarization/`: Speaker identification module
- `facial-expression-recognition-openCV/`: Facial analysis module
- `email_service/`: Email delivery system
- `frontend/`: Web interface files
- `custom_output/`: Generated reports and processed files
- `uploads/`: Temporary storage for uploaded files

## Dependencies

- PyTorch ecosystem for machine learning
- ffmpeg for video processing
- OpenCV for facial recognition
- pyannote.audio for speaker diarization
- Whisper for speech-to-text

## License

MIT License 