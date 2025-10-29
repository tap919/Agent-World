
# OpsBot Agent

**Role**: Task routing, scheduling, readiness enforcement

**Shared Functions**:
- Readiness Gate
- Task Router
- Report Generator

**Triggers**:
- Daily at 7am and 7pm
- After scoring updates

**Inputs**:
- Flow-to-Fruition Protocol
- Task list templates

**Outputs**:
- Daily task list
- GO/NO-GO decisions
- Slack summaries

**Logic Flow**:
1. Check readiness scores
2. Route tasks based on thresholds
3. Generate summary report
4. Export to Slack and OneDrive
