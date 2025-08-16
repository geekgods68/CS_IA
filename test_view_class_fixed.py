#!/usr/bin/env python3

import sys
import os
from flask import Flask

# Add the current directory to the Python path
sys.path.insert(0, '/Users/advikpunugu/Desktop/ComputerScienceIA/CS_IA')

from routes.admin import admin_bp
from routes.auth import auth_bp

def test_view_class_route():
    """Test the view_class route with proper Flask setup"""
    app = Flask(__name__, 
                template_folder='/Users/advikpunugu/Desktop/ComputerScienceIA/CS_IA/templates',
                static_folder='/Users/advikpunugu/Desktop/ComputerScienceIA/CS_IA/static')
    app.secret_key = 'test-secret-key'
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'
            sess['username'] = 'admin'
        
        # Test the view_class route
        try:
            response = client.get('/admin/view_class/1')
            print(f'Status code: {response.status_code}')
            
            if response.status_code == 200:
                print("✅ view_class route works correctly!")
                print("Response contains class details without database errors.")
            else:
                print(f"❌ Error: Status code {response.status_code}")
                if response.status_code == 500:
                    print("Server error occurred.")
                
        except Exception as e:
            print(f"❌ Exception occurred: {e}")
            print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_view_class_route()
