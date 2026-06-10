"""
Quick setup wizard for local development or production deployment.

Usage:
    python scripts/setup_wizard.py
"""

import sys
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def print_header(text: str):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_step(num: int, text: str):
    print(f"\n[{num}] {text}")


def create_env_file():
    """Create .env file from example."""
    env_file = ROOT / ".env"
    env_example = ROOT / ".env.example"
    
    if env_file.exists():
        response = input("\n.env already exists. Overwrite? (y/n): ").lower()
        if response != 'y':
            return
    
    if env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✓ Created .env from .env.example")
    else:
        print("! .env.example not found")


def setup_venv():
    """Create Python virtual environment."""
    venv_path = ROOT / ".venv"
    
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return
    
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
    print("✓ Virtual environment created")
    
    # Show activation command
    if sys.platform == "win32":
        print(f"\nActivate with: .venv\\Scripts\\activate")
    else:
        print(f"\nActivate with: source .venv/bin/activate")


def install_dependencies():
    """Install Python dependencies."""
    print("\nInstalling dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(ROOT / "requirements.txt")], check=True)
    print("✓ Dependencies installed")


def choose_database():
    """Guide user to choose database setup."""
    print_header("DATABASE SETUP")
    
    print("""
Choose your database:

1. SQLite (Local - Default, no setup needed)
   - Best for: Development
   - No Docker needed
   - Data stored in data/app_reviews.db

2. PostgreSQL Local (Docker required)
   - Best for: Local testing with production-like DB
   - Run: docker-compose -f docker-compose.staging.yml up
   - Database will auto-create

3. PostgreSQL Managed (Neon - Recommended for Production)
   - Best for: Production, free tier available
   - Sign up: https://neon.tech
   - Copy connection string from project dashboard
   - Add to .env as DATABASE_URL

4. PostgreSQL Managed (Supabase)
   - Best for: Production + auth/other features
   - Sign up: https://supabase.com
   - Copy connection string from project settings

5. Skip for now (use default SQLite)
    """)
    
    choice = input("Choose (1-5): ").strip()
    
    if choice == "1":
        print("✓ SQLite selected (no additional setup needed)")
        return "sqlite"
    
    elif choice == "2":
        print("\nFor local PostgreSQL with Docker:")
        print("  1. Install Docker: https://www.docker.com/products/docker-desktop")
        print("  2. Run: docker-compose -f docker-compose.staging.yml up")
        print("✓ Docker Compose setup selected")
        return "docker"
    
    elif choice == "3":
        print("\nFor Neon PostgreSQL:")
        print("  1. Sign up at https://neon.tech")
        print("  2. Create a project and database")
        print("  3. Copy the connection string")
        print("  4. Add to .env: DATABASE_URL=<connection-string>")
        print("✓ Neon setup selected")
        return "neon"
    
    elif choice == "4":
        print("\nFor Supabase PostgreSQL:")
        print("  1. Sign up at https://supabase.com")
        print("  2. Create a new project")
        print("  3. Get connection string from project settings")
        print("  4. Add to .env: DATABASE_URL=<connection-string>")
        print("✓ Supabase setup selected")
        return "supabase"
    
    else:
        print("✓ Using default SQLite")
        return "sqlite"


def init_database():
    """Initialize database tables."""
    print("\nInitializing database...")
    
    try:
        sys.path.insert(0, str(ROOT))
        from src.review_store import init_store
        
        init_store()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"! Error initializing database: {e}")
        print("  You can run manually later: python scripts/init_db.py setup")


def run_tests():
    """Run basic tests."""
    response = input("\nRun tests? (y/n): ").lower()
    
    if response == 'y':
        print("Running tests...")
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], cwd=ROOT)


def show_next_steps():
    """Show what to do next."""
    print_header("SETUP COMPLETE! NEXT STEPS")
    
    print("""
1. View Recent Reviews:
   python scripts/view_reviews.py

2. View Database Status:
   python scripts/init_db.py health

3. Start the App:
   streamlit run dashboard/app.py

4. Submit a Test Review:
   - Open http://localhost:8501 in browser
   - Go to "Reviews & Deploy" tab
   - Fill in the form and submit

5. View/Export Reviews:
   - Via Dashboard: Download button in Reviews tab
   - Via CLI: python scripts/view_reviews.py --all

6. Production Deployment:
   - See DOCKER_POSTGRES_GUIDE.md for detailed instructions
   - See DEPLOYMENT.md for recommended paths

For more information:
   - README.md - Project overview
   - DOCKER_POSTGRES_GUIDE.md - Docker & PostgreSQL integration
   - DEPLOYMENT.md - Production deployment options
   - PRODUCTION_ARCHITECTURE.md - Architecture decisions
    """)


def main():
    print_header("DEVICE STORAGE FORECASTER - SETUP WIZARD")
    
    # Step 1: Environment
    print_step(1, "Setting up environment...")
    create_env_file()
    
    # Step 2: Virtual environment
    print_step(2, "Setting up Python environment...")
    setup_venv()
    
    # Step 3: Dependencies
    print_step(3, "Installing dependencies...")
    install_dependencies()
    
    # Step 4: Database
    print_step(4, "Choosing database...")
    db_choice = choose_database()
    
    # Step 5: Initialize database
    print_step(5, "Initializing database...")
    try:
        init_database()
    except Exception as e:
        print(f"Note: Database initialization can be done later")
    
    # Step 6: Tests (optional)
    print_step(6, "Testing (optional)...")
    try:
        run_tests()
    except:
        pass
    
    # Show next steps
    show_next_steps()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
