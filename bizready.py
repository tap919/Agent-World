import json
from datetime import datetime
from .models import WorkOrder, GuildFund, TalentSeat, OperatorEarning
from .extensions import db

BIZREADY = {
    "ENTRY_PRICE": 2500,
    "CAPACITY_SKIM": 500,
    "DIY_MODULE_CASH": 2000,
    "MICRO_PRICE": 1000,
    "MINI_PRICE": 3000,
    "SEAT_COST": 3000,
    "PLATFORM_FEE": 0.25,
    "PRE_SPLIT": 0.70,
    "POST_SPLIT": 0.85,
    "CYCLE_DAYS": 60,
    "RAP_DIY": {"PM":0.10,"Design":0.20,"FE":0.20,"Growth":0.40,"QA":0.10},
    "RAP_MICRO": {"PM":0.05,"Design":0.10,"FE":0.40,"BE":0.20,"Growth":0.20,"QA":0.05},
    "RAP_MINI": {"PM":0.14,"Design":0.16,"FE":0.38,"BE":0.27,"QA":0.05},
}

def _rap(item_type: str):
    if item_type == "DIY": return BIZREADY["RAP_DIY"]
    if item_type == "MICRO": return BIZREADY["RAP_MICRO"]
    return BIZREADY["RAP_MINI"]

def _module_cash_and_fees(item_type: str, gross_cents: int):
    if item_type == "DIY":
        module_cash = int(BIZREADY["DIY_MODULE_CASH"] * 100)
    else:
        module_cash = gross_cents
    platform_fee = int(module_cash * BIZREADY["PLATFORM_FEE"])
    net = module_cash - platform_fee
    return module_cash, platform_fee, net

def _split_for_seat(seat: TalentSeat):
    return BIZREADY["POST_SPLIT"] if seat.profit_clear_at else BIZREADY["PRE_SPLIT"]

def assign_seats_for_roles(roles_needed: list) -> dict:
    mapping = {}
    for role in roles_needed:
        q = TalentSeat.query.filter_by(role=role, is_active=True).order_by(TalentSeat.earned_in_cycle.asc()).first()
        if q:
            mapping.setdefault(role, []).append(q.id)
    return mapping

def distribute_payouts(workorder: WorkOrder):
    rap = json.loads(workorder.rap_json)
    assigned = json.loads(workorder.assigned_roles_json or "{}")
    net = workorder.net_cents
    for role, weight in rap.items():
        role_cash = int(net * weight)
        for seat_id in assigned.get(role, []):
            seat = TalentSeat.query.get(seat_id)
            if not seat:
                continue
            split = _split_for_seat(seat)
            to_talent = int(role_cash * split)
            db.session.add(OperatorEarning(seat_id=seat.id, workorder_id=workorder.id, role=role, cash_cents=to_talent))
            seat.earned_in_cycle = (seat.earned_in_cycle or 0) + to_talent
            if (not seat.profit_clear_at) and seat.earned_in_cycle >= BIZREADY["SEAT_COST"] * 100:
                seat.profit_clear_at = datetime.utcnow()
            db.session.add(seat)
    db.session.commit()
