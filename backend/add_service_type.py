"""
Add service_type field to all plans in JSON
"""
import json

# Load plans
with open('real_plans.json', 'r') as f:
    plans = json.load(f)

# Add service_type to each plan
for plan in plans:
    plan['service_type'] = 'Residential'

# Save back
with open('real_plans.json', 'w') as f:
    json.dump(plans, f, indent=2)

print(f"Added service_type='Residential' to {len(plans)} plans")
