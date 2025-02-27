import random
import pandas as pd
import os
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dictionary import (
    negativeWordsInRoman, apologiseComments, happyComments, greetingsList,
    namingDict, positiveWordsInRoman, neutralWordsInRoman, neutralComments
)
import openai

# Set your OpenAI API key
openai.api_key = "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"


EMAIL = 'easypaisa@blinkitech.com'
PASSWORD = 'Telenor@123'
IMAP_SERVER = 'mail.blinkitech.com'
IMAP_PORT = 993
SMTP_SERVER = 'mail.blinkitech.com'
SMTP_PORT = 465

EXCEL_FILE = "feedback.xlsx"


def preprocessComment(comment):
    """Classify comment sentiment as positive, negative, or neutral."""
    comment = comment.lower()
    found=False
    print(comment)
   
    for word in negativeWordsInRoman:
        if word in comment:
            found=True
            print(found)
            return "negative"

    for word in positiveWordsInRoman:
        if word in comment:
            found=True
            print(found)
            return "positive"
    print(found)
    if found==False:
        return "neutral"  # Default to neutral if no match found


def generateResponse(name, category='x'):
    
    """Generate a bot response based on sentiment category."""
    temp = name.lower()
    
    if temp in namingDict or len(temp) > 30:
        name = "Valuable Customer"

    greetings = random.choice(greetingsList)

    if category == "negative":
        response = random.choice(apologiseComments)
    elif category == "positive":
        response = random.choice(happyComments)
    elif category == "neutral":
        response = random.choice(neutralComments)

   
    return f"{response}"


def save_to_excel(name, comment, bot_response):
    
    try:
        """Save user feedback to an Excel sheet."""
        # Check if file exists and get the last serial number
        if os.path.exists(EXCEL_FILE):
            existing_df = pd.read_excel(EXCEL_FILE)
            last_sr_no = existing_df["Sr No"].iloc[-1] if not existing_df.empty else 0
        else:
            existing_df = pd.DataFrame(columns=["Sr No", "Name", "User Comment", "Bot Response"])
            last_sr_no = 0

        # Create new row with incremented Sr No
        new_row = {
            "Sr No": last_sr_no + 1,
            "Name": name,
            "User Comment": comment,
            "Bot Response": bot_response
        }
        # Append to DataFrame
        updated_df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)
        # Save to Excel
        updated_df.to_excel(EXCEL_FILE, index=False)
        # Check if 5 rows are completed, then send email
        if len(updated_df) % 50 == 0:
            send_email_with_attachment(updated_df)
    except Exception as e:
        print(e)
    

def send_email_with_attachment(df):
    """Send the feedback file via email and then clear the file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"feedback_{timestamp}.xlsx"
    df.to_excel(file_name, index=False)

    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = EMAIL  # Send to yourself or specify recipient
    msg['Subject'] = "Feedback Report"

    with open(file_name, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={file_name}')
        msg.attach(part)

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, EMAIL, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

    os.remove(file_name)  # Remove the temporary file

    # **Clear the feedback file**
    empty_df = pd.DataFrame(columns=["Sr No", "Name", "User Comment", "Bot Response"])
    empty_df.to_excel(EXCEL_FILE, index=False)
    print("Feedback file cleared.")

def analyze_comment_and_reply(comment: str) -> str:
    """
    Analyzes a Facebook comment and generates a gentle, human-like response 
    as an Easypaisa agent, handling different comment types appropriately.
    """
    prompt = f"""
    You are an Easypaisa customer support agent. Your task is to reply to Facebook comments in a polite and professional manner.
    - If the comment is positive, express gratitude and appreciation.
    - If it's a complaint, apologize and ask the user to inbox for further assistance.
    - If it's a suggestion, acknowledge and thank them for their input.
    - If it's neutral, acknowledge it politely.
    - If it's an advertisement, handle it professionally.
    - Always reply in the same language as the comment (English, Roman Urdu, or Urdu,sindi, punjabi).
    - Use emojis appropriately to make the reply engaging and friendly.
    - If a customer make any sort of complaint, firstly provide a relevant step-by-step procedure before asking them to inbox for further details.
    
    Example Comments & Replies:
    1. Comment: "Easypaisa is awesome!" → Reply: "Thank you! 😊 Your support means the world to us. 💚"
    2. Comment: "Service is too slow 😡" → Reply: "We understand your concern. Apologies for the inconvenience! Please inbox us with more details so we can assist you. 🙏"
    3. Comment: "You should add more security features." → Reply: "Great suggestion! We are always working on improving our services. Thanks for your valuable input! 😊"
    4. Comment: "Check out my page for great offers!" → Reply: "Please keep the comments relevant to Easypaisa. Thanks! 👍"
    5. Comment: "I want to change my Easypaisa account number." → Reply: "To change your Easypaisa account number, you need to visit the nearest Easypaisa retailer or Telenor Microfinance Bank branch with your original CNIC. If you need more details, please inbox us, and we'd be happy to assist you further! 😊📩"
    
    Now, reply to this comment:
    "{comment}"
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use GPT-4 or GPT-3.5 depending on availability
            messages=[{"role": "system", "content": "You are a friendly Easypaisa support agent."},
                      {"role": "user", "content": prompt}],
            max_tokens=500
        )
        reply = response["choices"][0]["message"]["content"].strip()
        return reply
    except Exception as e:
        return "We apologize for the inconvenience. Please try again later or inbox us for further assistance. 🙏"
    
def clean_comment(s):
    # Remove all occurrences of double quotes
    s = s.replace('"', '').replace(':', '')
    
    # Remove "Reply" or "reply" if it's at the start
    if s.lower().startswith("reply"):
        s = s[5:].lstrip()  # Remove "Reply"/"reply" and leading spaces

    return s

def getResponse(name, comment):
    '''
    """Process user comment and generate a response."""
    print("COMMENT", comment)
    category = preprocessComment(comment)
    print("CATEGORY", category)
    finalResponse = generateResponse(name, category)
    '''
    finalResponse = analyze_comment_and_reply(comment)
    finalResponse = clean_comment(finalResponse)
    # Store feedback in Excel
    save_to_excel(name, comment, finalResponse)
    return finalResponse
