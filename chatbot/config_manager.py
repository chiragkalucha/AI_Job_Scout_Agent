# chatbot/config_manager.py - Manages .env configuration

import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(PROJECT_ROOT, 'config', '.env')

class ConfigManager:
    """Manages .env file updates"""
    
    @staticmethod
    def get_value(key, default=''):
        """Get value from .env"""
        
        try:
            with open(ENV_PATH, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        if '=' in line:
                            k, v = line.split('=', 1)
                            if k.strip() == key:
                                return v.strip()
        except FileNotFoundError:
            pass
        
        return default
    
    @staticmethod
    def set_value(key, value):
        """Set value in .env"""
        
        try:
            # Read all lines
            if os.path.exists(ENV_PATH):
                with open(ENV_PATH, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # Update or add key
            updated = False
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        k, _ = line.split('=', 1)
                        if k.strip() == key:
                            lines[i] = f'{key}={value}\n'
                            updated = True
                            break
            
            if not updated:
                lines.append(f'{key}={value}\n')
            
            # Write back
            os.makedirs(os.path.dirname(ENV_PATH), exist_ok=True)
            with open(ENV_PATH, 'w') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
    
    @staticmethod
    def get_roles():
        """Get job roles as list"""
        
        roles_str = ConfigManager.get_value('JOB_ROLES', 'Data Analyst')
        return [r.strip() for r in roles_str.split(',') if r.strip()]
    
    @staticmethod
    def set_roles(roles_list):
        """Set job roles from list"""
        
        roles_str = ', '.join(roles_list)
        return ConfigManager.set_value('JOB_ROLES', roles_str)
    
    @staticmethod
    def add_role(role):
        """Add a role to existing list"""
        
        current = ConfigManager.get_roles()
        
        if role not in current:
            current.append(role)
            return ConfigManager.set_roles(current)
        
        return False  # Already exists
    
    @staticmethod
    def remove_role(role):
        """Remove a role from list"""
        
        current = ConfigManager.get_roles()
        
        if role in current:
            current.remove(role)
            return ConfigManager.set_roles(current)
        
        return False  # Doesn't exist
    
    @staticmethod
    def get_salary():
        """Get minimum salary"""
        
        return int(ConfigManager.get_value('MIN_SALARY_LPA', '15'))
    
    @staticmethod
    def set_salary(salary):
        """Set minimum salary"""
        
        return ConfigManager.set_value('MIN_SALARY_LPA', str(salary))


# Test
if __name__ == "__main__":
    config = ConfigManager()
    
    print("Current Settings:")
    print(f"  Salary: {config.get_salary()} LPA")
    print(f"  Roles: {config.get_roles()}")
    
    print("\nTesting updates...")
    config.set_salary(20)
    config.add_role("Data Scientist")
    
    print("\nUpdated Settings:")
    print(f"  Salary: {config.get_salary()} LPA")
    print(f"  Roles: {config.get_roles()}")