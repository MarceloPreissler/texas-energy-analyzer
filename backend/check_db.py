import sqlite3

conn = sqlite3.connect('plans.db')
cursor = conn.cursor()

# Total counts
cursor.execute('SELECT COUNT(*) FROM plans')
total_plans = cursor.fetchone()[0]
print(f'Total plans in database: {total_plans}')

cursor.execute('SELECT COUNT(*) FROM providers')
total_providers = cursor.fetchone()[0]
print(f'Total providers in database: {total_providers}')

# Plans by service type
cursor.execute('SELECT service_type, COUNT(*) FROM plans GROUP BY service_type')
print('\nPlans by service type:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

# Sample plans
cursor.execute('SELECT plan_name, service_type, zip_code, rate_1000_cents FROM plans LIMIT 5')
print('\nSample plans:')
for row in cursor.fetchall():
    print(f'  Plan: {row[0]}, Service: {row[1]}, Zip: {row[2]}, Rate: {row[3]}')

conn.close()
