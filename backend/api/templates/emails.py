def get_verification_email_template(user, verification_url):
    return f"""
    <html>
        <!-- Previous HTML template -->
    </html>
    """

def get_password_reset_email_template(user, reset_url):
    return f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Reset Your Password</h2>
                </div>
                <div class="content">
                    <h3>Hello {user.first_name or 'there'}!</h3>
                    <p>We received a request to reset your JengaFunds account password.</p>
                    <p>Click the button below to set a new password:</p>
                    
                    <center>
                        <a href="{reset_url}" class="button" style="color: white;">
                            Reset Password
                        </a>
                    </center>
                    
                    <p>If the button doesn't work, copy and paste this link:</p>
                    <p style="background-color: #eee; padding: 10px; border-radius: 5px;">{reset_url}</p>
                    
                    <p>This link will expire in 24 hours for security reasons.</p>
                    <p>If you didn't request a password reset, you can safely ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© {datetime.now().year} JengaFunds. All rights reserved.</p>
                </div>
            </div>
        </body>
    </html>
    """