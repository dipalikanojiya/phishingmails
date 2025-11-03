from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from models import db, Campaign, CampaignAttempt

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phishaware.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ---------- HOME / DASHBOARD ----------
@app.route('/')
def index():
    campaigns = Campaign.query.all()
    return render_template('index.html', campaigns=campaigns)

# ---------- CREATE NEW CAMPAIGN ----------
@app.route('/create_campaign', methods=['POST'])
def create_campaign():
    name = request.form['name']
    subject = request.form.get('subject', '')
    message = request.form.get('message', '')
    campaign = Campaign(name=name, subject=subject, message=message, status='Active')
    db.session.add(campaign)
    db.session.commit()
    return redirect(url_for('index'))

# ---------- SEND EMAILS ----------
@app.route('/send_emails/<int:campaign_id>', methods=['POST'])
def send_emails(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    emails = [e.strip() for e in request.form['emails'].split(',') if e.strip()]
    for email in emails:
        attempt = CampaignAttempt(campaign_id=campaign.id, email=email)
        db.session.add(attempt)
    campaign.emails_sent += len(emails)
    db.session.commit()
    return redirect(url_for('index'))

# ---------- TRACK CLICK ----------
@app.route('/track/<int:campaign_id>/<email>')
def track_click(campaign_id, email):
    attempt = CampaignAttempt.query.filter_by(campaign_id=campaign_id, email=email).first()
    if attempt and not attempt.clicked:
        attempt.clicked = True
        attempt.clicked_at = datetime.utcnow()
        attempt.campaign.clicked += 1
        attempt.campaign.update_success_rate()
        db.session.commit()
    return redirect(url_for('landing_sim', email=email, cid=campaign_id))

# ---------- TRACK ACCESS ----------
@app.route('/access/<int:campaign_id>/<email>')
def access_email(campaign_id, email):
    attempt = CampaignAttempt.query.filter_by(campaign_id=campaign_id, email=email).first()
    if attempt and not attempt.accessed:
        attempt.accessed = True
        attempt.accessed_at = datetime.utcnow()
        attempt.campaign.accessed += 1
        attempt.campaign.update_success_rate()
        db.session.commit()
    return jsonify({"message": "Accessed recorded"})

# ---------- TRACK REPORT ----------
@app.route('/report/<int:campaign_id>/<email>')
def report_email(campaign_id, email):
    attempt = CampaignAttempt.query.filter_by(campaign_id=campaign_id, email=email).first()
    if attempt and not attempt.reported:
        attempt.reported = True
        attempt.reported_at = datetime.utcnow()
        attempt.campaign.reported += 1
        attempt.campaign.update_success_rate()
        db.session.commit()
    return jsonify({"message": "Reported successfully"})

# ---------- CAMPAIGN DETAILS ----------
@app.route('/campaign/<int:campaign_id>')
def campaign_details(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    attempts = CampaignAttempt.query.filter_by(campaign_id=campaign_id).all()
    return render_template('campaign.html', campaign=campaign, attempts=attempts)

# ---------- REPORTS PAGE ----------
@app.route('/report')
def report():
    campaigns = Campaign.query.all()
    for c in campaigns:
        c.clicked_count = CampaignAttempt.query.filter_by(campaign_id=c.id, clicked=True).count()
        c.submitted_count = CampaignAttempt.query.filter_by(campaign_id=c.id, submitted=True).count()
        c.reported_count = CampaignAttempt.query.filter_by(campaign_id=c.id, reported=True).count()

        total_actions = (c.clicked_count or 0) + (c.submitted_count or 0) + (c.reported_count or 0)
        c.success_rate = round((total_actions / c.emails_sent) * 100, 2) if c.emails_sent else 0

    return render_template('report.html', campaigns=campaigns)

'''
@app.route('/report')
def reports():
    campaigns = Campaign.query.all()
    return render_template('report.html', campaigns=campaigns)
'''
# ---------- LANDING SIMULATION ----------
@app.route('/landing_sim')
def landing_sim():
    email = request.args.get('email')
    cid = request.args.get('cid')
    return render_template('landing_sim.html', email=email, cid=cid)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
