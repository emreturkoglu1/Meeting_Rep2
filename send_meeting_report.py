#!/usr/bin/env python3
import os
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Hardcoded sender email configuration
SENDER_EMAIL = "se3006meetingreport@gmail.com"  # Replace with your actual email
SENDER_PASSWORD = "cyxe skmq bzpa chbf"    # Replace with your actual app password

class EmailIntegration:
    def __init__(self, sender_email=None, sender_password=None):
        self.sender_email = sender_email
        self.sender_password = sender_password
        
        if not sender_email or not sender_password:
            print("Warning: Email credentials not provided")
    
    def send_meeting_report(self, recipient_email, report_file_path, meeting_data=None, custom_subject=None, custom_body=None):
        """
        Send meeting report via email
        
        Parameters:
        recipient_email (str): Email address to send the report to
        report_file_path (str): Path to the report file
        meeting_data (dict): Data about the meeting
        custom_subject (str): Custom email subject
        custom_body (str): Custom email body
        
        Returns:
        bool: True if email sent successfully, False otherwise
        """
        # Skip if credentials are missing
        if not self.sender_email or not self.sender_password:
            print("Cannot send email: Credentials not provided")
            return False
            
        # Skip if recipient email is missing or report file doesn't exist
        if not recipient_email:
            print("Cannot send email: Recipient email not provided")
            return False
            
        if not os.path.exists(report_file_path):
            print(f"Cannot send email: Report file not found at {report_file_path}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
            # Set subject
            subject = custom_subject or "Your Meeting Report"
            msg['Subject'] = subject
            
            # Create body
            body = custom_body or self._create_email_body(meeting_data)
            msg.attach(MIMEText(body, 'html', _charset='utf-8'))
            
            # Attach report file
            with open(report_file_path, 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype="pdf")
                
                # Get filename from path
                filename = os.path.basename(report_file_path)
                attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                
                msg.attach(attachment)
            
            # Connect to SMTP server and send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    def _create_email_body(self, meeting_data):
        """Create email body based on meeting data"""
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                }
                .container {
                    padding: 20px;
                    background-color: #f9f9f9;
                    border-radius: 5px;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }
                p {
                    margin-bottom: 15px;
                }
                .footer {
                    margin-top: 30px;
                    font-size: 12px;
                    color: #7f8c8d;
                    border-top: 1px solid #ecf0f1;
                    padding-top: 10px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Your Meeting Report</h1>
                <p>Thank you for using our meeting analysis service.</p>
                <p>We have processed your meeting and analyzed the content to provide you with a comprehensive report.</p>
                <p>You can find the detailed meeting report in the attached PDF file.</p>
                
                <p>Key features of this report include:</p>
                <ul>
                    <li>Meeting summary and key discussion points</li>
                    <li>Action items and decisions made</li>
                    <li>Participant analysis and speaking time</li>
                </ul>
                
                <p>If you have any questions or feedback, please let us know.</p>
                
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

def main():
    """
    Main function to send the meeting report via email.
    This script is intended to be called after the report has been generated.
    """
    parser = argparse.ArgumentParser(description='Send Meeting Report via Email')
    parser.add_argument('--recipient', type=str, required=True, help='Recipient email address')
    parser.add_argument('--report', type=str, required=True, help='Path to the report file')
    parser.add_argument('--data', type=str, help='Path to the meeting data JSON file')
    parser.add_argument('--subject', type=str, help='Custom email subject')
    parser.add_argument('--body', type=str, help='Custom email body')
    
    args = parser.parse_args()
    
    # Initialize the email integration with hardcoded credentials
    email_service = EmailIntegration(
        sender_email=SENDER_EMAIL,
        sender_password=SENDER_PASSWORD
    )
    
    # Extract meeting data if a data file is provided
    meeting_data = {}
    if args.data and os.path.exists(args.data):
        meeting_data = email_service.extract_meeting_data(args.data)
    
    # Send the report
    success = email_service.send_meeting_report(
        recipient_email=args.recipient,
        report_file_path=args.report,
        meeting_data=meeting_data,
        custom_subject=args.subject,
        custom_body=args.body
    )
    
    if success:
        print(f"Successfully sent meeting report to {args.recipient}")
        return 0
    else:
        print(f"Failed to send meeting report to {args.recipient}")
        return 1

if __name__ == "__main__":
    exit(main()) 