from datetime import datetime
from flask_login import UserMixin
from .extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    company = db.Column(db.String(100))
    subscription_tier = db.Column(db.String(20), default='free')
    stripe_customer_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    agents = db.relationship('UserAgent', backref='user', lazy=True)
    projects = db.relationship('StartupProject', backref='client', lazy=True)

class UserAgent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    agent_type = db.Column(db.String(50))
    agent_name = db.Column(db.String(100))
    agent_config = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    total_executions = db.Column(db.Integer, default=0)
    last_executed = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AgentTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='🤖')
    price_credits = db.Column(db.Integer, default=1)
    config_template = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    popularity_score = db.Column(db.Integer, default=0)

class TalentSeat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))
    operator_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    cycle_start = db.Column(db.DateTime, default=datetime.utcnow)
    cycle_end = db.Column(db.DateTime)
    earned_in_cycle = db.Column(db.Integer, default=0)
    profit_clear_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

class GuildFund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inflow_cents = db.Column(db.Integer, default=0)
    outflow_cents = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    memo = db.Column(db.String(200))

class StartupProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(120))
    sector = db.Column(db.String(50), default='standard')
    score = db.Column(db.Integer, default=70)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    work_orders = db.relationship('WorkOrder', backref='project', lazy=True)

class WorkOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('startup_project.id'))
    item_type = db.Column(db.String(10))
    status = db.Column(db.String(20), default='pending')
    gross_cents = db.Column(db.Integer)
    module_cash_cents = db.Column(db.Integer)
    platform_fee_cents = db.Column(db.Integer)
    net_cents = db.Column(db.Integer)
    rap_json = db.Column(db.Text)
    assigned_roles_json = db.Column(db.Text)
    accepted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OperatorEarning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seat_id = db.Column(db.Integer, db.ForeignKey('talent_seat.id'))
    workorder_id = db.Column(db.Integer, db.ForeignKey('work_order.id'))
    role = db.Column(db.String(20))
    cash_cents = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
