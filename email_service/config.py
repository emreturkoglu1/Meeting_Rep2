import os

# Email service configuration
EMAIL_CONFIG = {
    # Default SMTP settings
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": 465,
    
    # Output directories
    "REPORT_OUTPUT_DIR": os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports"),
}

# Ensure the reports directory exists
os.makedirs(EMAIL_CONFIG["REPORT_OUTPUT_DIR"], exist_ok=True) 