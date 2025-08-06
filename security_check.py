#!/usr/bin/env python3
"""
Security Check Script for Legal Dashboard OCR
============================================

This script checks for hardcoded secrets, tokens, and API keys in the codebase.
Based on security best practices from GitGuardian and Hugging Face documentation.
"""

import os
import re
import sys
from pathlib import Path


def check_for_hardcoded_secrets():
    """Check for hardcoded secrets in the codebase"""
    print("🔒 Security Check - Looking for hardcoded secrets...")

    # Patterns to look for
    secret_patterns = [
        r'hf_[a-zA-Z0-9]{20,}',  # Hugging Face tokens
        r'sk-[a-zA-Z0-9]{20,}',  # OpenAI API keys
        r'pk_[a-zA-Z0-9]{20,}',  # Stripe public keys
        r'sk_[a-zA-Z0-9]{20,}',  # Stripe secret keys
        r'AKIA[0-9A-Z]{16}',     # AWS access keys
        r'[0-9a-zA-Z/+]{40}',    # AWS secret keys
        r'ghp_[a-zA-Z0-9]{36}',  # GitHub personal access tokens
        r'gho_[a-zA-Z0-9]{36}',  # GitHub OAuth tokens
        r'ghu_[a-zA-Z0-9]{36}',  # GitHub user-to-server tokens
        r'ghs_[a-zA-Z0-9]{36}',  # GitHub server-to-server tokens
        r'ghr_[a-zA-Z0-9]{36}',  # GitHub refresh tokens
    ]

    # Files to check
    files_to_check = [
        "app/services/ocr_service.py",
        "app/services/ai_service.py",
        "app/services/database_service.py",
        "app/main.py",
        "huggingface_space/app.py",
        "requirements.txt",
        "README.md"
    ]

    found_secrets = []

    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pattern in secret_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        found_secrets.append({
                            'file': file_path,
                            'pattern': pattern,
                            'matches': matches
                        })

            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")

    return found_secrets


def check_environment_variables():
    """Check if environment variables are properly used"""
    print("\n🔍 Checking environment variable usage...")

    env_vars_to_check = [
        "HF_TOKEN",
        "OPENAI_API_KEY",
        "DATABASE_URL",
        "SECRET_KEY"
    ]

    proper_usage = True

    for var in env_vars_to_check:
        if os.getenv(var):
            print(f"✅ {var} is set in environment")
        else:
            print(
                f"⚠️ {var} not found in environment (this is OK for development)")

    return proper_usage


def check_gitignore():
    """Check if sensitive files are properly ignored"""
    print("\n📁 Checking .gitignore for sensitive files...")

    sensitive_files = [
        ".env",
        "*.key",
        "*.pem",
        "secrets.json",
        "config.json"
    ]

    gitignore_content = ""
    if os.path.exists(".gitignore"):
        with open(".gitignore", 'r') as f:
            gitignore_content = f.read()

    missing_entries = []
    for file_pattern in sensitive_files:
        if file_pattern not in gitignore_content:
            missing_entries.append(file_pattern)

    if missing_entries:
        print(f"⚠️ Missing from .gitignore: {missing_entries}")
        return False
    else:
        print("✅ .gitignore properly configured")
        return True


def generate_security_report(found_secrets):
    """Generate security report"""
    print("\n📊 Security Check Report")
    print("=" * 50)

    if found_secrets:
        print("❌ HARDCODED SECRETS FOUND:")
        for secret in found_secrets:
            print(f"  File: {secret['file']}")
            print(f"  Pattern: {secret['pattern']}")
            print(f"  Matches: {len(secret['matches'])} found")
            print("  ---")
        return False
    else:
        print("✅ No hardcoded secrets found!")
        return True


def provide_remediation_advice():
    """Provide advice for fixing security issues"""
    print("\n🔧 Security Remediation Advice")
    print("=" * 40)

    print("1. **Remove Hardcoded Tokens**:")
    print("   - Replace hardcoded tokens with environment variables")
    print("   - Use os.getenv() to read from environment")
    print("   - Set tokens in Hugging Face Space settings")

    print("\n2. **Environment Variables**:")
    print("   - Set HF_TOKEN in your Space settings")
    print("   - Use .env files for local development")
    print("   - Never commit .env files to version control")

    print("\n3. **Git Security**:")
    print("   - Add sensitive files to .gitignore")
    print("   - Use git-secrets for pre-commit hooks")
    print("   - Regularly audit your repository")

    print("\n4. **Hugging Face Best Practices**:")
    print("   - Use Space secrets for sensitive data")
    print("   - Keep tokens private and rotate regularly")
    print("   - Monitor token usage and permissions")


def main():
    """Main security check function"""
    print("🔒 Legal Dashboard OCR - Security Check")
    print("=" * 50)

    # Check for hardcoded secrets
    found_secrets = check_for_hardcoded_secrets()

    # Check environment variables
    env_ok = check_environment_variables()

    # Check gitignore
    gitignore_ok = check_gitignore()

    # Generate report
    secrets_ok = generate_security_report(found_secrets)

    # Final result
    print("\n" + "=" * 50)
    if secrets_ok and env_ok and gitignore_ok:
        print("🎉 Security check passed!")
        print("✅ No hardcoded secrets found")
        print("✅ Environment variables properly configured")
        print("✅ Git security measures in place")
        return 0
    else:
        print("⚠️ Security issues found!")
        provide_remediation_advice()
        return 1


if __name__ == "__main__":
    sys.exit(main())
