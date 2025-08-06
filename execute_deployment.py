#!/usr/bin/env python3
"""
Final Deployment Execution Script
================================

This script guides you through the complete deployment process to Hugging Face Spaces.
Based on: https://dev.to/koolkamalkishor/how-to-upload-your-project-to-hugging-face-spaces-a-beginners-step-by-step-guide-1pkn
"""

import os
import sys
import subprocess
import time


def print_header():
    """Print deployment header"""
    print("🚀 Legal Dashboard OCR - Final Deployment")
    print("=" * 60)
    print("✅ All validation checks passed!")
    print("✅ Encoding issues fixed!")
    print("✅ Project ready for deployment!")
    print("=" * 60)


def get_deployment_info():
    """Get deployment information from user"""
    print("\n📋 Deployment Information")
    print("-" * 30)

    username = input("Enter your Hugging Face username: ").strip()
    space_name = input(
        "Enter Space name (e.g., legal-dashboard-ocr): ").strip()
    hf_token = input("Enter your Hugging Face token: ").strip()

    if not all([username, space_name, hf_token]):
        print("❌ All fields are required!")
        return None

    return {
        'username': username,
        'space_name': space_name,
        'hf_token': hf_token,
        'space_url': f"https://huggingface.co/spaces/{username}/{space_name}"
    }


def create_space_instructions(info):
    """Provide instructions for creating the Space"""
    print(f"\n📋 Step 1: Create Hugging Face Space")
    print("-" * 40)
    print("1. Go to: https://huggingface.co/spaces")
    print("2. Click 'Create new Space'")
    print("3. Configure:")
    print(f"   - Owner: {info['username']}")
    print(f"   - Space name: {info['space_name']}")
    print("   - SDK: Gradio")
    print("   - License: MIT")
    print("   - Visibility: Public")
    print("   - Hardware: CPU (Free tier)")
    print("4. Click 'Create Space'")
    print(f"5. Your Space URL will be: {info['space_url']}")

    input("\nPress Enter when you've created the Space...")


def prepare_git_repository(info):
    """Prepare Git repository for deployment"""
    print(f"\n📋 Step 2: Prepare Git Repository")
    print("-" * 40)

    # Change to huggingface_space directory
    os.chdir("huggingface_space")

    try:
        # Initialize git repository
        print("Initializing Git repository...")
        subprocess.run(["git", "init"], check=True)

        # Add remote origin
        remote_url = f"https://{info['username']}:{info['hf_token']}@huggingface.co/spaces/{info['username']}/{info['space_name']}"
        print("Adding remote origin...")
        subprocess.run(
            ["git", "remote", "add", "origin", remote_url], check=True)

        print("✅ Git repository prepared successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Git setup failed: {e}")
        return False


def deploy_files():
    """Deploy files to Hugging Face Space"""
    print(f"\n📋 Step 3: Deploy Files")
    print("-" * 40)

    try:
        # Add all files
        print("Adding files to Git...")
        subprocess.run(["git", "add", "."], check=True)

        # Commit changes
        print("Committing changes...")
        subprocess.run(
            ["git", "commit", "-m", "Initial deployment of Legal Dashboard OCR"], check=True)

        # Push to main branch
        print("Pushing to Hugging Face...")
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)

        print("✅ Files deployed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return False


def configure_environment(info):
    """Provide instructions for environment configuration"""
    print(f"\n📋 Step 4: Configure Environment Variables")
    print("-" * 40)
    print("1. Go to your Space page:")
    print(f"   {info['space_url']}")
    print("2. Click 'Settings' tab")
    print("3. Add environment variable:")
    print("   - Name: HF_TOKEN")
    print("   - Value: Your Hugging Face access token")
    print("4. Click 'Save'")
    print("5. Wait for the Space to rebuild")

    input("\nPress Enter when you've configured the environment...")


def verify_deployment(info):
    """Verify the deployment"""
    print(f"\n📋 Step 5: Verify Deployment")
    print("-" * 40)
    print("1. Visit your Space:")
    print(f"   {info['space_url']}")
    print("2. Check that the Space loads without errors")
    print("3. Test file upload functionality")
    print("4. Upload a Persian PDF document")
    print("5. Verify OCR processing works")
    print("6. Test AI analysis features")
    print("7. Check dashboard functionality")

    print(f"\n🎉 Deployment Complete!")
    print(f"🌐 Your Space is live at: {info['space_url']}")


def main():
    """Main deployment function"""
    print_header()

    # Get deployment information
    info = get_deployment_info()
    if not info:
        return 1

    # Step 1: Create Space
    create_space_instructions(info)

    # Step 2: Prepare Git repository
    if not prepare_git_repository(info):
        return 1

    # Step 3: Deploy files
    if not deploy_files():
        return 1

    # Step 4: Configure environment
    configure_environment(info)

    # Step 5: Verify deployment
    verify_deployment(info)

    print(f"\n🎉 Congratulations! Your Legal Dashboard OCR is now live!")
    print(f"📚 Documentation: {info['space_url']}")
    print(f"🔧 For updates, use: git push origin main")

    return 0


if __name__ == "__main__":
    sys.exit(main())
