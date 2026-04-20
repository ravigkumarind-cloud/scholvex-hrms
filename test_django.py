#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Setup Django
django.setup()

print("Django setup successful!")

# Try to import models
try:
    from employees.models_v2 import Department, Role, Employee
    print("Models imported successfully!")
except Exception as e:
    print(f"Error importing models: {e}")

# Try to run migrations
try:
    from django.core.management import execute_from_command_line
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate', '--verbosity=1'])
except Exception as e:
    print(f"Error running migrations: {e}")