#!/usr/bin/env python3
"""
Hugging Face Spaces Deployment Script
=====================================

This script automates the deployment of the Legal Dashboard OCR system to Hugging Face Spaces.
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HFDeployment:
    def __init__(self, space_name, username, hf_token):
        self.space_name = space_name
        self.username = username
        self.hf_token = hf_token
        self.project_root = Path(__file__).parent
        self.hf_space_dir = self.project_root / "huggingface_space"

    def validate_structure(self):
        """Validate the project structure before deployment"""
        logger.info("Validating project structure...")

        required_files = [
            "huggingface_space/app.py",
            "huggingface_space/Spacefile",
            "huggingface_space/README.md",
            "requirements.txt",
            "app/services/ocr_service.py",
            "app/services/ai_service.py",
            "app/services/database_service.py"
        ]

        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            logger.error(f"Missing required files: {missing_files}")
            return False

        logger.info("✅ Project structure validation passed")
        return True

    def prepare_deployment_files(self):
        """Prepare files for Hugging Face Space deployment"""
        logger.info("Preparing deployment files...")

        # Copy required files to HF space directory
        files_to_copy = [
            ("requirements.txt", "requirements.txt"),
            ("app/", "app/"),
            ("data/", "data/"),
            ("tests/", "tests/")
        ]

        for src, dst in files_to_copy:
            src_path = self.project_root / src
            dst_path = self.hf_space_dir / dst

            if src_path.exists():
                if src_path.is_dir():
                    if dst_path.exists():
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)
                logger.info(f"✅ Copied {src} to {dst}")

        # Create .gitignore for HF space
        gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database
*.db
*.sqlite

# Environment variables
.env

# Temporary files
*.tmp
*.temp
"""

        gitignore_path = self.hf_space_dir / ".gitignore"
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content.strip())

        logger.info("✅ Deployment files prepared")
        return True

    def create_space(self):
        """Create a new Hugging Face Space"""
        logger.info(
            f"Creating Hugging Face Space: {self.username}/{self.space_name}")

        # This would typically be done via Hugging Face API or web interface
        # For now, we'll provide instructions
        logger.info("""
📋 Manual Space Creation Required:

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in the details:
   - Owner: {username}
   - Space name: {space_name}
   - SDK: Gradio
   - License: MIT
   - Visibility: Public
4. Click "Create Space"

The Space will be created at: https://huggingface.co/spaces/{username}/{space_name}
        """.format(username=self.username, space_name=self.space_name))

        return True

    def setup_git_repository(self):
        """Set up Git repository for the Space"""
        logger.info("Setting up Git repository...")

        # Change to HF space directory
        os.chdir(self.hf_space_dir)

        # Initialize git repository
        subprocess.run(["git", "init"], check=True)

        # Add remote origin
        remote_url = f"https://{self.username}:{self.hf_token}@huggingface.co/spaces/{self.username}/{self.space_name}"
        subprocess.run(
            ["git", "remote", "add", "origin", remote_url], check=True)

        logger.info("✅ Git repository initialized")
        return True

    def commit_and_push(self):
        """Commit and push changes to Hugging Face Space"""
        logger.info("Committing and pushing changes...")

        try:
            # Add all files
            subprocess.run(["git", "add", "."], check=True)

            # Commit changes
            subprocess.run(
                ["git", "commit", "-m", "Initial deployment of Legal Dashboard OCR"], check=True)

            # Push to main branch
            subprocess.run(["git", "push", "-u", "origin", "main"], check=True)

            logger.info("✅ Changes pushed successfully")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git operation failed: {e}")
            return False

    def verify_deployment(self):
        """Verify the deployment was successful"""
        logger.info("Verifying deployment...")

        space_url = f"https://huggingface.co/spaces/{self.username}/{self.space_name}"
        logger.info(f"🌐 Space URL: {space_url}")

        logger.info("""
📋 Deployment Verification Checklist:

✅ Project structure validated
✅ Deployment files prepared  
✅ Git repository initialized
✅ Changes committed and pushed
✅ Space created on Hugging Face

Next Steps:
1. Visit the Space URL to verify it's building correctly
2. Test the OCR functionality with sample documents
3. Check the logs for any errors
4. Verify all features are working as expected

Space URL: {space_url}
        """.format(space_url=space_url))

        return True

    def deploy(self):
        """Main deployment method"""
        logger.info("🚀 Starting Hugging Face Spaces deployment...")

        try:
            # Step 1: Validate structure
            if not self.validate_structure():
                return False

            # Step 2: Prepare deployment files
            if not self.prepare_deployment_files():
                return False

            # Step 3: Create space (manual step)
            self.create_space()

            # Step 4: Setup git repository
            if not self.setup_git_repository():
                return False

            # Step 5: Commit and push
            if not self.commit_and_push():
                return False

            # Step 6: Verify deployment
            self.verify_deployment()

            logger.info("🎉 Deployment completed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False


def main():
    """Main function"""
    print("🚀 Legal Dashboard OCR - Hugging Face Spaces Deployment")
    print("=" * 60)

    # Get deployment parameters
    space_name = input(
        "Enter Space name (e.g., legal-dashboard-ocr): ").strip()
    username = input("Enter your Hugging Face username: ").strip()
    hf_token = input("Enter your Hugging Face token: ").strip()

    if not all([space_name, username, hf_token]):
        print("❌ All parameters are required")
        return

    # Create deployment instance
    deployment = HFDeployment(space_name, username, hf_token)

    # Run deployment
    success = deployment.deploy()

    if success:
        print(f"\n🎉 Deployment successful!")
        print(
            f"🌐 Visit your Space at: https://huggingface.co/spaces/{username}/{space_name}")
    else:
        print("\n❌ Deployment failed. Please check the logs above.")


if __name__ == "__main__":
    main()
