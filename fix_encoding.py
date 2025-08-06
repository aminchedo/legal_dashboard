#!/usr/bin/env python3
"""
Encoding Fix Script for Legal Dashboard OCR
==========================================

This script fixes Unicode encoding issues that can occur on Windows systems.
Based on solutions from: https://docs.appseed.us/content/how-to-fix/unicodedecodeerror-charmap-codec-cant-decode-byte-0x9d/
"""

import os
import sys
import codecs


def fix_file_encoding(file_path, target_encoding='utf-8'):
    """Fix encoding issues in a file"""
    try:
        # Try to read with different encodings
        encodings_to_try = ['utf-8', 'utf-8-sig',
                            'cp1252', 'latin-1', 'iso-8859-1']

        content = None
        used_encoding = None

        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    used_encoding = encoding
                    print(
                        f"✅ Successfully read {file_path} with {encoding} encoding")
                    break
            except UnicodeDecodeError:
                continue

        if content is None:
            print(f"❌ Could not read {file_path} with any encoding")
            return False

        # Write back with UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Fixed encoding for {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def fix_project_encoding():
    """Fix encoding issues in the entire project"""
    print("🔧 Fixing encoding issues in Legal Dashboard OCR project...")

    # Files that might have encoding issues
    files_to_fix = [
        "huggingface_space/app.py",
        "huggingface_space/README.md",
        "requirements.txt",
        "README.md",
        "DEPLOYMENT_INSTRUCTIONS.md",
        "FINAL_DEPLOYMENT_INSTRUCTIONS.md",
        "DEPLOYMENT_SUMMARY.md"
    ]

    fixed_count = 0
    total_files = len(files_to_fix)

    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_file_encoding(file_path):
                fixed_count += 1
        else:
            print(f"⚠️ File not found: {file_path}")

    print(f"\n📊 Encoding Fix Results:")
    print(f"✅ Fixed: {fixed_count}/{total_files} files")

    return fixed_count == total_files


def set_environment_encoding():
    """Set environment variables for proper encoding"""
    print("\n🔧 Setting environment variables for encoding...")

    # Set UTF-8 environment variable for Windows
    os.environ['PYTHONUTF8'] = '1'

    # For Windows CMD
    print("For Windows CMD, run: set PYTHONUTF8=1")

    # For PowerShell
    print("For PowerShell, run: $env:PYTHONUTF8=1")

    print("✅ Environment encoding variables set")


def main():
    """Main function to fix encoding issues"""
    print("🚀 Legal Dashboard OCR - Encoding Fix")
    print("=" * 50)

    # Fix file encodings
    files_ok = fix_project_encoding()

    # Set environment encoding
    set_environment_encoding()

    print("\n" + "=" * 50)
    if files_ok:
        print("🎉 All encoding issues fixed!")
        print("✅ Project is ready for deployment")
        return 0
    else:
        print("⚠️ Some encoding issues remain")
        print("Please check the files manually")
        return 1


if __name__ == "__main__":
    sys.exit(main())
