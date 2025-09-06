#!/usr/bin/env python3
"""
Environment Setup Script for Genesis Crew
This script helps you set up your .env file with the required API keys.
"""

import os
import sys

def create_env_file():
    """Create a .env file with user input"""
    print("🚀 Genesis Crew Environment Setup")
    print("=" * 40)
    print("This script will help you set up your .env file with the required API keys.")
    print()
    
    # Check if .env already exists
    if os.path.exists('.env'):
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Setup cancelled.")
            return False
    
    # Collect API keys
    print("Please provide the following information:")
    print()
    
    openai_key = input("🔑 OpenAI API Key (required): ").strip()
    if not openai_key:
        print("❌ OpenAI API Key is required!")
        return False
    
    print()
    print("Optional configurations (press Enter to skip):")
    
    langsmith_key = input("🔍 LangSmith API Key (optional): ").strip()
    langsmith_project = input("📊 LangSmith Project Name (optional): ").strip() or "genesis-crew"
    supabase_url = input("🗄️  Supabase URL (optional): ").strip()
    supabase_key = input("🔐 Supabase Anon Key (optional): ").strip()
    
    # Create .env content
    env_content = f"""# OpenAI Configuration
OPENAI_API_KEY={openai_key}

# LangSmith Configuration (Optional - for observability)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY={langsmith_key}
LANGCHAIN_PROJECT={langsmith_project}

# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print()
        print("✅ .env file created successfully!")
        print()
        print("📋 Configuration Summary:")
        print(f"   - OpenAI API Key: {'✅ Set' if openai_key else '❌ Not set'}")
        print(f"   - LangSmith API Key: {'✅ Set' if langsmith_key else '❌ Not set'}")
        print(f"   - LangSmith Project: {langsmith_project}")
        print(f"   - Supabase URL: {'✅ Set' if supabase_url else '❌ Not set'}")
        print(f"   - Supabase Key: {'✅ Set' if supabase_key else '❌ Not set'}")
        print()
        print("🎉 Setup complete! You can now run: python genesis_crew_main.py")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    """Main function"""
    try:
        success = create_env_file()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
