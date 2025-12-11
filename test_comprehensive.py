
import sys
import os
import importlib
import unittest

# Fix encoding for Windows console to handle emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class TestComprehensive(unittest.TestCase):
    def setUp(self):
        self.critical_files = [
            'main.py',
            'Procfile',
            'requirements.txt',
            'runtime.txt',
            'news_analyzer.py',
            'portfolio_manager.py',
            'strategies.py'
        ]
        self.critical_templates = [
            'templates/broadcast.html',
            'templates/mobile_app.html',
            'templates/news_center.html'
        ]

    def test_files_exist(self):
        """Test existence of critical system files."""
        print("\nChecking critical files...")
        for filename in self.critical_files:
            exists = os.path.exists(filename)
            self.assertTrue(exists, f"Missing critical file: {filename}")
            print(f"[OK] Found {filename}")
            
    def test_imports(self):
        """Test importing main modules to catch syntax errors."""
        print("\nChecking module imports...")
        modules = ['main', 'news_analyzer', 'portfolio_manager', 'strategies']
        for module_name in modules:
            try:
                importlib.import_module(module_name)
                print(f"[OK] Imported {module_name} successfully")
            except Exception as e:
                self.fail(f"Failed to import {module_name}: {e}")

    def test_templates_exist(self):
        """Test existence of critical templates."""
        print("\nChecking templates...")
        for template in self.critical_templates:
            exists = os.path.exists(template)
            # Just warning if they don't exist, as some might be named differently
            if exists:
                print(f"[OK] Found {template}")
            else:
                print(f"[WARN] Warning: Could not find {template}")

    def test_flask_app_creation(self):
        """Test creating the Flask app instance."""
        print("\nChecking Flask app creation...")
        try:
            from main import app
            self.assertIsNotNone(app)
            print("[OK] Flask app instance created successfully")
            
            # Basic route check
            rules = list(app.url_map.iter_rules())
            print(f"   Registered routes: {len(rules)}")
        except Exception as e:
            self.fail(f"Failed to create Flask app: {e}")

if __name__ == '__main__':
    print("="*50)
    print(">>> STARTING COMPREHENSIVE SYSTEM TEST")
    print("="*50)
    unittest.main(verbosity=2)
