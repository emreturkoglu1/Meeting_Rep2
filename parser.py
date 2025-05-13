import ffmpeg
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import cgi
import tempfile
import json
from audio_diarization.whisper_diarization import process_audio_diarization
from email_service import EmailIntegration
import sys
import importlib.util

# Define the custom output directory
CUSTOM_OUTPUT_DIR = 'custom_output'
UPLOADS_DIR = 'uploads'

# Create the directories if they don't exist
for directory in [CUSTOM_OUTPUT_DIR, UPLOADS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Initialize email service with hardcoded credentials
email_service = EmailIntegration(
    sender_email="se3006meetingreport@gmail.com",
    sender_password="cyxe skmq bzpa chbf"
)

# Yüz ifadesi analizi modülünü doğrudan dosya yolundan import edelim
facial_main_path = os.path.join(os.path.dirname(__file__), "facial-expression-recognition-openCV", "main.py")
spec = importlib.util.spec_from_file_location("facial_analysis", facial_main_path)
facial_analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(facial_analysis)
analyze_video = facial_analysis.analyze_video

def send_progress(self, message):
    """Send a progress update to the client"""
    progress_data = json.dumps({"progress": message}) + "\n"
    self.wfile.write(progress_data.encode())

def extract_video(input_file, output_video):
    # Extract video only
    ffmpeg.input(input_file).output(output_video, vcodec='copy', an=None).run()

def extract_audio(input_file, output_audio):
    # Extract audio only (convert to MP3)
    ffmpeg.input(input_file).output(output_audio, acodec='libmp3lame', vn=None).run()

def cleanup_files():
    """Clean up temporary files after processing"""
    files_to_remove = [
        # Sadece yüklenen dosyaları temizle, çıktı dosyalarını tutuyoruz
        os.path.join(UPLOADS_DIR, '*')  # Remove all files in uploads directory
    ]
    
    for file_pattern in files_to_remove:
        try:
            if '*' in file_pattern:
                # Handle directory cleanup
                import glob
                for file in glob.glob(file_pattern):
                    if os.path.exists(file):
                        os.remove(file)
            else:
                # Handle single file
                if os.path.exists(file_pattern):
                    os.remove(file_pattern)
        except Exception as e:
            print(f"Warning: Could not remove {file_pattern}: {str(e)}")

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Serve the HTML file
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('frontend/index.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/styles.css':
            # Serve the CSS file
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('frontend/styles.css', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/script.js':
            # Serve the JavaScript file
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            with open('frontend/script.js', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/download-report':
            # Serve the PDF report file
            report_path = os.path.join(CUSTOM_OUTPUT_DIR, 'meeting_report.pdf')
            if os.path.exists(report_path):
                self.send_response(200)
                self.send_header('Content-type', 'application/pdf')
                self.send_header('Content-Disposition', 'attachment; filename="meeting_report.pdf"')
                self.end_headers()
                with open(report_path, 'rb') as file:
                    self.wfile.write(file.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Report not found')
        elif self.path.startswith('/custom_output/'):
            # Serve files from custom_output directory
            file_path = self.path[1:]  # Remove leading slash
            
            # Handle query parameters in URL (like cache busting parameters)
            if '?' in file_path:
                file_path = file_path.split('?')[0]
            
            print(f"Requested file: {file_path}")
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_response(200)
                if file_path.endswith('.mp4'):
                    self.send_header('Content-type', 'video/mp4')
                    print(f"Sending video file: {file_path}, size: {os.path.getsize(file_path)} bytes")
                elif file_path.endswith('.wav'):
                    self.send_header('Content-type', 'audio/wav')
                elif file_path.endswith('.csv'):
                    self.send_header('Content-type', 'text/csv')
                elif file_path.endswith('.txt'):
                    self.send_header('Content-type', 'text/plain')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                
                # Add comprehensive Cross-Origin headers
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, HEAD')
                self.send_header('Access-Control-Allow-Headers', 'Origin, Accept, Content-Type, X-Requested-With, Content-Length')
                
                # Add cache control headers
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                
                # Add content length header
                file_size = os.path.getsize(file_path)
                self.send_header('Content-Length', str(file_size))
                
                self.end_headers()
                
                # Use binary mode for all files and handle large files properly
                try:
                    with open(file_path, 'rb') as file:
                        chunk_size = 8192  # 8KB chunks
                        while True:
                            chunk = file.read(chunk_size)
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                except Exception as e:
                    print(f"Error sending file {file_path}: {str(e)}")
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                error_msg = f"File not found: {file_path}"
                self.wfile.write(error_msg.encode())
                print(error_msg)
        elif self.path == '/processing-status':
            # İşlem durumunu JSON olarak döndüren endpoint
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # İşlem durumunu belirle (gerçek bir işlem takibi ekleyebilirsiniz)
            # Şimdilik basit bir örnek
            progress_data = {
                'progress': 75,  # Yüzde olarak ilerleme
                'status': 'Processing facial expressions...',
                'completed': False
            }
            
            # İşlenen video dosyasını kontrol et
            processed_video_path = os.path.join(CUSTOM_OUTPUT_DIR, 'output_processed.mp4')
            if os.path.exists(processed_video_path):
                # Dosya varsa, işlem tamamlanmış olabilir
                # İşlem durumunu güncelleyin
                progress_data['progress'] = 100
                progress_data['status'] = 'Processing completed!'
                progress_data['completed'] = True
            
            self.wfile.write(json.dumps(progress_data).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found.')

    def do_POST(self):
        if self.path == '/upload':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse the multipart form data
            content_type = self.headers['Content-Type']
            if 'boundary=' in content_type:
                boundary = content_type.split('boundary=')[1].encode()
                
                # Find the start of the file data
                file_start = post_data.find(b'filename="')
                if file_start != -1:
                    # Extract filename
                    filename_start = file_start + 10
                    filename_end = post_data.find(b'"', filename_start)
                    filename = post_data[filename_start:filename_end].decode()
                    
                    # Extract email
                    email_start = post_data.find(b'name="email"')
                    if email_start != -1:
                        email_start = post_data.find(b'\r\n\r\n', email_start) + 4
                        email_end = post_data.find(b'\r\n--', email_start)
                        email = post_data[email_start:email_end].decode()
                    else:
                        email = None
                    
                    # Extract file data
                    file_data_start = post_data.find(b'\r\n\r\n', filename_end) + 4
                    file_data_end = post_data.find(b'\r\n--', file_data_start)
                    file_data = post_data[file_data_start:file_data_end]
                    
                    # Set up streaming response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Transfer-Encoding', 'chunked')
                    self.end_headers()
                    
                    try:
                        # Save the file
                        file_path = os.path.join(UPLOADS_DIR, filename)
                        with open(file_path, 'wb') as f:
                            f.write(file_data)
                        
                        # Extract video
                        video_path = os.path.join(CUSTOM_OUTPUT_DIR, 'output_video.mp4')
                        extract_video(file_path, video_path)
                        print("\n✅ Video extraction completed successfully!")
                        # Send progress update after video extraction
                        send_progress(self, "Extracting video completed")
                        
                        # Extract audio
                        audio_path = os.path.join(CUSTOM_OUTPUT_DIR, 'output_audio.wav')
                        extract_audio(file_path, audio_path)
                        print("✅ Audio extraction completed successfully!")
                        # Send progress update after audio extraction
                        send_progress(self, "Extracting audio completed")
                        
                        # Process audio through diarization
                        print("\n🔄 Starting audio diarization process...")
                        try:
                            diarization_results = process_audio_diarization(audio_path)
                            if diarization_results is None or len(diarization_results) == 0:
                                raise Exception("Diarization returned no results")
                            print("✅ Audio diarization completed successfully!")
                            print(f"📝 Found {len(diarization_results)} speech segments")
                        except Exception as e:
                            print(f"❌ Error during diarization: {str(e)}")
                            raise
                        
                        # Send progress update after diarization
                        send_progress(self, "Processing audio through diarization completed")
                        
                        # Yüz ifadesi analizi işlemini başlat
                        print("\n🔄 Starting facial expression analysis...")
                        send_progress(self, "Starting facial expression analysis")
                        
                        try:
                            # Facial expression analysis için dosya yollarını belirle
                            processed_video_path = os.path.join(CUSTOM_OUTPUT_DIR, 'output_processed.mp4')
                            emotion_csv_path = os.path.join(CUSTOM_OUTPUT_DIR, 'emotion_analysis.csv')
                            
                            # Analiz fonksiyonunu çağır
                            facial_analysis_success = analyze_video(video_path, processed_video_path, emotion_csv_path)
                            
                            if facial_analysis_success:
                                print("✅ Facial expression analysis completed successfully!")
                                # CSV dosyasını oku ve duygu analizi sonuçlarını al
                                facial_data = []
                                try:
                                    import csv
                                    with open(emotion_csv_path, 'r') as csvfile:
                                        reader = csv.DictReader(csvfile)
                                        for row in reader:
                                            facial_data.append(row)
                                    print(f"Read {len(facial_data)} facial expression records from CSV")
                                except Exception as e:
                                    print(f"Warning: Could not read facial expression data: {str(e)}")
                            else:
                                print("❌ Facial expression analysis failed")
                        except Exception as e:
                            print(f"❌ Error during facial expression analysis: {str(e)}")
                            facial_data = []
                        
                        # Send progress update after facial analysis
                        send_progress(self, "Facial expression analysis completed")
                        
                        # Send email if provided
                        email_sent = False
                        if email and True:
                            print("\n📧 Preparing email with meeting report...")
                            try:
                                # Format and save the transcript first
                                transcript_text = "Meeting Transcript:\n\n"
                                for segment in diarization_results:
                                    transcript_text += f"[{segment['start_time']:.2f} - {segment['end_time']:.2f}] {segment['speaker']}: {segment['text']}\n\n"
                                
                                # Save transcript to a file
                                transcript_path = os.path.join(CUSTOM_OUTPUT_DIR, 'transcript.txt')
                                with open(transcript_path, 'w') as f:
                                    f.write(transcript_text)
                                print("✅ Transcript file created successfully")
                                
                                # Generate meeting report using Gemini API
                                import geminiapi
                                
                                # Markdown'dan PDF oluşturma (ReportLab ile)
                                markdown_path = os.path.join(CUSTOM_OUTPUT_DIR, 'meeting_report.md')
                                pdf_path = os.path.join(CUSTOM_OUTPUT_DIR, 'meeting_report.pdf')
                                
                                # Burada ReportLab kullanılacak - geminiapi içinde tanımlı
                                try:
                                    print("Converting markdown to PDF using ReportLab...")
                                    # Doğrudan geminiapi içindeki fonksiyonu çağırıyoruz
                                    geminiapi.create_pdf_from_markdown(markdown_path, pdf_path)
                                    print("✅ PDF report generated successfully with ReportLab")
                                except Exception as e:
                                    print(f"❌ Error converting markdown to PDF: {str(e)}")
                                    raise
                                
                                # Send the report via email
                                email_sent = email_service.send_meeting_report(
                                    recipient_email=email,
                                    report_file_path=pdf_path,  # Send PDF instead of markdown
                                    meeting_data={'transcript': diarization_results},
                                    custom_subject='Your Meeting Report',
                                    custom_body='Please find attached the meeting report generated from your meeting.'
                                )
                                if email_sent:
                                    print("✅ Email sent successfully!")
                                else:
                                    print("❌ Failed to send email")
                            except Exception as e:
                                print(f"❌ Error preparing/sending email: {str(e)}")
                                raise
                        
                        print("\n🎉 All processes completed successfully!")
                        
                        # Send final response
                        final_response = {
                            'status': 'complete',
                            'message': 'File processed successfully',
                            'results': {
                                'audio_file': '/custom_output/output_audio.wav',
                                'video_file': '/custom_output/output_video.mp4',
                                'processed_video': '/custom_output/output_processed.mp4',
                                'facial_analysis': '/custom_output/emotion_analysis.csv',
                                'diarization': diarization_results,
                                'email_sent': email_sent
                            }
                        }
                        self.wfile.write(json.dumps(final_response).encode())
                        
                        # Clean up only upload files, keep processed files
                        cleanup_files()
                        print("✅ Temporary upload files cleaned up successfully")
                        
                    except Exception as e:
                        # Send error response
                        error_response = {
                            'status': 'error',
                            'message': str(e)
                        }
                        self.wfile.write(json.dumps(error_response).encode())
                    return
            
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'error', 'message': 'Invalid request'}).encode())

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
