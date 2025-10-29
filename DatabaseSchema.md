
# Agent World Database Schema

## Tables:
- Users: id, name, email, role, created_at
- Agents: id, name, type, tools, formulas, price, owner_id
- Resellers: id, name, discount_code, usage_count, revenue_generated
- Transactions: id, user_id, agent_id, amount, timestamp
- Manifests: id, agent_id, manifest_data, validated
