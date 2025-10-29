import json
from datetime import datetime, timedelta
from .extensions import db
from .models import AgentTemplate, TalentSeat

BIZREADY = {"CYCLE_DAYS": 60}

def seed_agent_templates():
    default_templates = [
        {'name':'Biotech Research Assistant','category':'biotech','icon':'🧬','description':'AI-powered research assistant for biotechnology and life sciences','config':json.dumps({'endpoints':['research_query','data_sources'],'capabilities':['data_collection','analysis','report_generation']})},
        {'name':'Music Composition Agent','category':'music','icon':'🎵','description':'Creative AI for music composition, analysis, and trend prediction','config':json.dumps({'endpoints':['genre','mood','instrumentation'],'capabilities':['melody_generation','harmony_analysis','trend_prediction']})},
        {'name':'Game Narrative Designer','category':'gaming','icon':'🎮','description':'AI game writer and narrative designer for immersive experiences','config':json.dumps({'endpoints':['story_premise','character_types','plot_complexity'],'capabilities':['dialogue_generation','quest_design','world_building']})},
        {'name':'Data Analytics Pro','category':'analytics','icon':'📊','description':'Advanced data analysis, visualization, and predictive modeling','config':json.dumps({'endpoints':['dataset','analysis_type','output_format'],'capabilities':['statistical_analysis','ml_modeling','dashboard_creation']})},
        {'name':'Content Marketing Writer','category':'marketing','icon':'✍️','description':'AI content creator for marketing campaigns and brand storytelling','config':json.dumps({'endpoints':['topic','tone','target_audience'],'capabilities':['blog_writing','social_media','seo_optimization']})},
        {'name':'Customer Support Bot','category':'support','icon':'💬','description':'Intelligent customer support automation with natural language understanding','config':json.dumps({'endpoints':['customer_query','context','escalation_rules'],'capabilities':['query_understanding','solution_recommendation','ticket_routing']})},
        {'name':'Code Review Assistant','category':'development','icon':'💻','description':'AI-powered code review, optimization, and best practices enforcement','config':json.dumps({'endpoints':['code_snippet','language','review_focus'],'capabilities':['bug_detection','performance_analysis','best_practices']})},
        {'name':'Financial Analyst','category':'finance','icon':'💰','description':'AI financial modeling, analysis, and investment recommendations','config':json.dumps({'endpoints':['financial_data','analysis_period','risk_tolerance'],'capabilities':['trend_analysis','risk_assessment','investment_recommendations']})},
        {'name':'Legal Document Analyzer','category':'legal','icon':'⚖️','description':'AI for legal document review, compliance checking, and risk assessment','config':json.dumps({'endpoints':['document_text','legal_jurisdiction','analysis_type'],'capabilities':['contract_review','compliance_checking','risk_identification']})},
        {'name':'Healthcare Diagnostic Assistant','category':'healthcare','icon':'🏥','description':'AI assistant for healthcare diagnostics and treatment recommendations','config':json.dumps({'endpoints':['symptoms','patient_history','test_results'],'capabilities':['symptom_analysis','condition_prediction','treatment_recommendations']})},
    ]
    for t in default_templates:
        if not AgentTemplate.query.filter_by(name=t['name']).first():
            db.session.add(AgentTemplate(
                name=t['name'], category=t['category'], icon=t['icon'],
                description=t['description'], config_template=t['config']
            ))
    db.session.commit()

def seed_talent_seats():
    needed = [("FE", 2), ("BE", 2), ("Design", 2), ("Growth", 2), ("PM", 1), ("QA", 1)]
    for role, n in needed:
        existing = TalentSeat.query.filter_by(role=role, is_active=True).count()
        for _ in range(max(0, n - existing)):
            seat = TalentSeat(role=role, cycle_start=datetime.utcnow(), cycle_end=datetime.utcnow() + timedelta(days=BIZREADY["CYCLE_DAYS"]))
            db.session.add(seat)
    db.session.commit()
