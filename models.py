from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Campaign(db.Model):
    __tablename__ = 'campaign'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="Draft")
    emails_sent = db.Column(db.Integer, default=0)
    clicked = db.Column(db.Integer, default=0)
    accessed = db.Column(db.Integer, default=0)
    reported = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def update_success_rate(self):
        total = self.emails_sent
        if total > 0:
            self.success_rate = round(((self.clicked + self.accessed + self.reported) / total) * 100, 2)
        else:
            self.success_rate = 0.0

class CampaignAttempt(db.Model):
    __tablename__ = 'campaign_attempt'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    clicked = db.Column(db.Boolean, default=False)
    clicked_at = db.Column(db.DateTime, nullable=True)
    accessed = db.Column(db.Boolean, default=False)
    accessed_at = db.Column(db.DateTime, nullable=True)
    reported = db.Column(db.Boolean, default=False)
    reported_at = db.Column(db.DateTime, nullable=True)

    campaign = db.relationship('Campaign', backref=db.backref('attempts', lazy=True))
