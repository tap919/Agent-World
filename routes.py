import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from .extensions import db, login_manager
from .models import User, UserAgent, AgentTemplate, StartupProject, WorkOrder, GuildFund
from .seeders import seed_agent_templates, seed_talent_seats
from .bizready import _rap, _module_cash_and_fees, assign_seats_for_roles, distribute_payouts

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
bizready_bp = Blueprint('bizready', __name__, url_prefix='/bizready')
api_bp = Blueprint('api', __name__, url_prefix='/api')

@main_bp.route('/')
def index():
    seed_agent_templates(); seed_talent_seats()
    tiers = {
        'free': {'name':'Starter','max_agents':1,'price':0,'popular':False,'features':['1 Active AI Agent','Community Templates Library','Email Support (48hr)','Basic Analytics Dashboard','Monthly Usage Reports'],'cta':'Start Free'},
        'basic': {'name':'Professional','max_agents':3,'price':29,'popular':False,'features':['3 Concurrent AI Agents','Premium Template Access','Priority Support (12hr)','Advanced Analytics & Insights','Custom Agent Configuration','API Access (10K calls/month)'],'cta':'Go Pro'},
        'pro': {'name':'Business','max_agents':10,'price':99,'popular':True,'features':['10 Concurrent AI Agents','All Premium Features','Priority Support (4hr)','Custom Agent Development','White-label Options','API Access (100K calls/month)','Dedicated Account Manager','Advanced Security & Compliance'],'cta':'Scale Up'},
        'enterprise': {'name':'Enterprise','max_agents':999,'price':299,'popular':False,'features':['Unlimited AI Agents','Custom Infrastructure','Dedicated Support Team','Custom SLA Guarantees','On-premise Deployment','Unlimited API Access','Custom Integration Services','Executive Business Reviews'],'cta':'Contact Sales'}
    }
    templates = AgentTemplate.query.filter_by(is_public=True).order_by(AgentTemplate.popularity_score.desc()).limit(6).all()
    return render_template('index.html', tiers=tiers, templates=templates)

@main_bp.route('/marketplace')
def marketplace():
    templates = AgentTemplate.query.filter_by(is_public=True).order_by(AgentTemplate.popularity_score.desc()).all()
    categories = [c[0] for c in db.session.query(AgentTemplate.category).distinct().all()]
    return render_template('marketplace.html', templates=templates, categories=categories)

@main_bp.route('/pricing')
def pricing():
    return render_template('pricing.html')

@auth_bp.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        company = request.form.get('company')
        tier = request.form.get('tier', 'free')
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error'); return redirect(url_for('auth.signup'))
        user = User(email=email, password=generate_password_hash(password), full_name=full_name, company=company, subscription_tier=tier)
        db.session.add(user); db.session.commit(); login_user(user)
        flash('Account created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email'); password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user); user.last_login = datetime.utcnow(); db.session.commit()
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user(); return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_agents = UserAgent.query.filter_by(user_id=current_user.id).all()
    available_templates = AgentTemplate.query.filter_by(is_public=True).limit(6).all()
    projects = StartupProject.query.filter_by(client_user_id=current_user.id).all()
    stats = {'total_executions': sum(a.total_executions for a in user_agents), 'active_agents': len([a for a in user_agents if a.is_active]), 'projects': len(projects)}
    tier_info = {'free':1,'basic':3,'pro':10,'enterprise':999}.get(current_user.subscription_tier,1)
    return render_template('dashboard.html', user_agents=user_agents, templates=available_templates, tier_info=tier_info, stats=stats, projects=projects)

@main_bp.route('/deploy-agent', methods=['POST'])
@login_required
def deploy_agent():
    data = request.get_json(force=True)
    template_id = data.get('template_id'); agent_name = data.get('agent_name','My Agent')
    current_agent_count = UserAgent.query.filter_by(user_id=current_user.id, is_active=True).count()
    max_agents = {'free':1,'basic':3,'pro':10,'enterprise':999}.get(current_user.subscription_tier,1)
    if current_agent_count >= max_agents: return jsonify({'error':'Agent limit reached. Upgrade to deploy more agents.'}), 400
    template = AgentTemplate.query.get(template_id)
    if not template: return jsonify({'error':'Template not found'}), 404
    new_agent = UserAgent(user_id=current_user.id, agent_type=template.name, agent_name=agent_name, agent_config=template.config_template)
    db.session.add(new_agent); template.popularity_score = (template.popularity_score or 0) + 1; db.session.commit()
    return jsonify({'message':'Agent deployed successfully','agent_id':new_agent.id})

@api_bp.route('/agent/<int:agent_id>/execute', methods=['POST'])
@login_required
def execute_agent(agent_id):
    user_agent = UserAgent.query.filter_by(id=agent_id, user_id=current_user.id).first()
    if not user_agent: return jsonify({'error':'Agent not found'}), 404
    input_data = (request.json or {}).get('input')
    user_agent.total_executions += 1; user_agent.last_executed = datetime.utcnow(); db.session.commit()
    return jsonify({'result': {'agent_id':user_agent.id,'agent_name':user_agent.agent_name,'input_processed':input_data,'output':f"Processed by {user_agent.agent_type}",'timestamp':datetime.utcnow().isoformat()}})

@bizready_bp.route('')
def bizready_landing():
    return render_template('bizready.html')

@bizready_bp.route('/start', methods=['POST'])
@login_required
def bizready_start():
    data = request.json or {}; name = data.get('name','My Project'); sector = data.get('sector','standard')
    project = StartupProject(client_user_id=current_user.id, name=name, sector=sector); db.session.add(project); db.session.commit()
    db.session.add(GuildFund(inflow_cents=500*100, memo=f"Skim for project {project.id}"))
    gross_cents = 2500 * 100; module_cash, platform_fee, net = _module_cash_and_fees("DIY", gross_cents)
    wo = WorkOrder(project_id=project.id, item_type="DIY", status="in_progress", gross_cents=gross_cents, module_cash_cents=module_cash, platform_fee_cents=platform_fee, net_cents=net, rap_json=json.dumps(_rap("DIY")), assigned_roles_json=json.dumps(assign_seats_for_roles(list(_rap("DIY").keys()))))
    db.session.add(wo); db.session.commit()
    return jsonify({'project_id': project.id, 'workorder_id': wo.id, 'message': 'BizReady DIY project started successfully'})

@bizready_bp.route('/add-item', methods=['POST'])
@login_required
def bizready_add_item():
    data = request.json or {}; project_id = data.get('project_id'); item_type = data.get('item_type')
    if item_type not in ("MICRO", "MINI"): return jsonify({'error':'Invalid item type'}), 400
    project = StartupProject.query.filter_by(id=project_id, client_user_id=current_user.id).first()
    if not project: return jsonify({'error':'Project not found'}), 404
    price = 1000 if item_type == "MICRO" else 3000; gross_cents = price * 100
    module_cash, platform_fee, net = _module_cash_and_fees(item_type, gross_cents); rap = _rap(item_type)
    wo = WorkOrder(project_id=project.id, item_type=item_type, status="in_progress", gross_cents=gross_cents, module_cash_cents=module_cash, platform_fee_cents=platform_fee, net_cents=net, rap_json=json.dumps(rap), assigned_roles_json=json.dumps(assign_seats_for_roles(list(rap.keys()))))
    db.session.add(wo); db.session.commit()
    return jsonify({'workorder_id': wo.id, 'message': f'{item_type} module queued successfully'})

@bizready_bp.route('/accept/<int:wo_id>', methods=['POST'])
@login_required
def bizready_accept(wo_id):
    wo = WorkOrder.query.get(wo_id)
    if not wo: return jsonify({'error':'Work order not found'}), 404
    wo.status = "accepted"; wo.accepted_at = datetime.utcnow(); db.session.add(wo); db.session.commit()
    distribute_payouts(wo); return jsonify({'message':'Work order accepted and payouts distributed'})
