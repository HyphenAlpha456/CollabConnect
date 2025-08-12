
from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from uuid import uuid4
import random
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
load_dotenv()
app = Flask(__name__)
app.secret_key = "super_secret_key"  
EMAIL_USER = "agnimitra.sasaru99@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_email_otp(to_email, otp):
    subject = "🔐 Your OTP for Project Submission Verification"
    
  
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                        <tr>
                            <td style="background-color: #007BFF; padding: 20px; text-align: center; color: white; font-size: 24px; font-weight: bold;">
                                Project Submission Verification
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 30px; text-align: center; font-size: 16px; color: #333;">
                                <p>Dear User,</p>
                                <p>We received a request to verify your project submission. Please use the OTP below to complete the process:</p>
                                <p style="font-size: 32px; font-weight: bold; color: #007BFF; margin: 20px 0;">{otp}</p>
                                <p>This OTP is valid for <b>5 minutes</b>. Do not share it with anyone.</p>
                                <a href="#" style="display: inline-block; margin-top: 20px; padding: 12px 25px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Verify Now</a>
                            </td>
                        </tr>
                        <tr>
                            <td style="background-color: #f4f4f4; text-align: center; padding: 15px; font-size: 12px; color: #777;">
                                © 2025 Project Submission System. All rights reserved.
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email

   
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)


def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit-idea', methods=['GET', 'POST'])
def submit_idea():
    if request.method == 'POST':
       
        otp = random.randint(100000, 999999)

        
        session['pending_idea'] = {
            "title": request.form['title'],
            "description": request.form['description'],
            "tech": request.form['tech'],
            "email": request.form['email']
        }
        session['otp'] = str(otp)
        session['otp_time'] = time.time()  # Store current timestamp

       
        try:
            send_email_otp(request.form['email'], otp)
            flash("OTP sent to your email. Please verify within 5 minutes to submit your project.", "info")
        except Exception as e:
            flash(f"Error sending OTP: {e}", "danger")
            return redirect(url_for('submit_idea'))

        return redirect(url_for('verify_otp'))
    return render_template('submit_idea.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']

        
        if 'otp' not in session or 'otp_time' not in session:
            flash("OTP session expired. Please submit your idea again.", "danger")
            return redirect(url_for('submit_idea'))

        
        if time.time() - session['otp_time'] > 300:
            flash("OTP expired. Please submit your idea again.", "danger")
            session.pop('pending_idea', None)
            session.pop('otp', None)
            session.pop('otp_time', None)
            return redirect(url_for('submit_idea'))

      
        if entered_otp == session['otp']:
            ideas = load_json('data/ideas.json')
            ideas.append(session['pending_idea'])
            save_json(ideas, 'data/ideas.json')

           
            session.pop('pending_idea', None)
            session.pop('otp', None)
            session.pop('otp_time', None)

            flash("Project submitted successfully!", "success")
            return redirect(url_for('view_projects'))
        else:
            flash("Invalid OTP. Please try again.", "danger")

    return render_template('verify_otp.html')


@app.route('/resend-otp')
def resend_otp():
    if 'pending_idea' not in session:
        flash("Session expired. Please submit your idea again.", "danger")
        return redirect(url_for('submit_idea'))

    otp = random.randint(100000, 999999)
    session['otp'] = str(otp)
    session['otp_time'] = time.time()

    try:
        send_email_otp(session['pending_idea']['email'], otp)
        flash("A new OTP has been sent to your email.", "info")
    except Exception as e:
        flash(f"Error sending OTP: {e}", "danger")

    return redirect(url_for('verify_otp'))

@app.route('/projects')
def view_projects():
    ideas = load_json('data/ideas.json')
    return render_template('projects.html', ideas=ideas)

@app.route('/forum')
def forum():
    questions = load_json('data/forum.json')
    return render_template('forum.html', questions=questions)

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'POST':
        question = {
            "id": str(uuid4()),
            "title": request.form['title'],
            "description": request.form['description'],
            "replies": []
        }
        questions = load_json('data/forum.json')
        questions.append(question)
        save_json(questions, 'data/forum.json')
        return redirect(url_for('forum'))
    return render_template('ask.html')

@app.route('/question/<id>', methods=['GET', 'POST'])
def question(id):
    questions = load_json('data/forum.json')
    question = next((q for q in questions if q['id'] == id), None)

    if not question:
        return "Question not found", 404

    if request.method == 'POST':
        reply = request.form['reply']
        question['replies'].append(reply)
        save_json(questions, 'data/forum.json')
        return redirect(url_for('question', id=id))

    return render_template('question.html', question=question)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    os.makedirs('data', exist_ok=True)
    if not os.path.exists('data/ideas.json'):
        save_json([], 'data/ideas.json')
    if not os.path.exists('data/forum.json'):
        save_json([], 'data/forum.json')

    app.run(debug=True, host="0.0.0.0", port=port)
