#!/usr/bin/env python3
"""
Setup script for the Ecommerce Audit Logs application.
This script automates the installation and initialization process.
"""

import os
import sys
import subprocess
import shutil

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = ".env"
    if not os.path.exists(env_file):
        print("📝 Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("""# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration
DATABASE_URL=sqlite:///audit_logs.db

# Security
BCRYPT_LOG_ROUNDS=12
""")
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🚀 Setting up Ecommerce Audit Logs Application")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment if it doesn't exist
    venv_dir = "venv"
    if not os.path.exists(venv_dir):
        print("📦 Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv {venv_dir}", "Creating virtual environment"):
            sys.exit(1)
    
    # Determine the correct pip and python paths
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(venv_dir, "Scripts", "pip")
        python_path = os.path.join(venv_dir, "Scripts", "python")
    else:  # Unix/Linux/macOS
        pip_path = os.path.join(venv_dir, "bin", "pip")
        python_path = os.path.join(venv_dir, "bin", "python")
    
    # Install dependencies
    if not run_command(f"{pip_path} install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Initialize database
    print("🗄️  Initializing database...")
    if not run_command(f"{python_path} init_db.py", "Initializing database"):
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    print("2. Run the application:")
    print("   python app.py")
    print("3. Open your browser and go to:")
    print("   http://localhost:5000")
    print("\nSample credentials (if you created sample data):")
    print("   Owner: owner@sample-store.com / owner123")
    print("   Admin: admin@sample-store.com / admin123")
    print("   Analyst: analyst@sample-store.com / analyst123")
    print("   Content Creator: creator@sample-store.com / creator123")
    print("\nAPI Documentation:")
    print("   http://localhost:5000/")
    print("   http://localhost:5000/audit-logs (web interface)")

if __name__ == "__main__":
    main() 