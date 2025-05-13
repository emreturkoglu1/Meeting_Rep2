import os
import json
from datetime import datetime
from .email_bot import EmailBot

class EmailIntegration:
    def __init__(self, sender_email=None, sender_password=None):
        """
        Initialize the email integration service.
        
        Args:
            sender_email (str, optional): Sender email address
            sender_password (str, optional): Sender email password
        """
        self.email_bot = EmailBot(sender_email=sender_email, sender_password=sender_password)
    
    def extract_meeting_data(self, data_file_path):
        """
        Extract meeting data from a JSON file.
        
        Args:
            data_file_path (str): Path to the meeting data JSON file
            
        Returns:
            dict: Meeting data dictionary
        """
        try:
            with open(data_file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading meeting data: {e}")
            return {}
    
    def send_meeting_report(self, recipient_email, report_file_path, meeting_data=None, custom_subject=None, custom_body=None):
        """
        Send a meeting report via email.
        
        Args:
            recipient_email (str): Recipient's email address
            report_file_path (str): Path to the report file
            meeting_data (dict, optional): Meeting metadata
            custom_subject (str, optional): Custom email subject
            custom_body (str, optional): Custom email body
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Validate email address
        if not self.email_bot.validate_email(recipient_email):
            print(f"Invalid recipient email address: {recipient_email}")
            return False
        
        # Create subject and body based on meeting data if available
        subject = custom_subject
        body = custom_body
        
        if meeting_data and not (custom_subject and custom_body):
            meeting_date = meeting_data.get('date', datetime.now().strftime('%Y-%m-%d'))
            meeting_title = meeting_data.get('title', 'Meeting')
            
            if not subject:
                subject = f"Meeting Report: {meeting_title} - {meeting_date}"
            
            if not body:
                body = (
                    f"Hello,\n\n"
                    f"Please find attached the meeting report for {meeting_title} "
                    f"held on {meeting_date}.\n\n"
                    f"Thank you for using our Meeting Report Creator.\n\n"
                    f"Best regards,\nMeeting Report Creator Bot"
                )
        
        # Send the email using EmailBot
        return self.email_bot.send_report(
            recipient_email=recipient_email,
            report_file_path=report_file_path,
            subject=subject,
            body=body
        ) 