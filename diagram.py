#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wokwi Diagram.json Extractor
============================
Script to download ZIP from Wokwi and extract only diagram.json file to current directory
"""

import requests
import os
import zipfile
import tempfile
import json

# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def read_url_from_file():
    """Read URL from url.txt file or specified file"""
    # Check environment variable first
    url_file = os.environ.get('WOKWI_URL_FILE', 'url.txt')
    
    try:
        with open(url_file, "r", encoding="utf-8") as f:
            url = f.read().strip()
            if url.startswith("https://wokwi.com/projects/"):
                return url
            else:
                print(f"{Colors.RED}ERROR: Invalid URL in url.txt file{Colors.RESET}")
                return None
    except FileNotFoundError:
        print(f"{Colors.RED}ERROR: url.txt file not found{Colors.RESET}")
        return None
    except Exception as e:
        print(f"{Colors.RED}ERROR: Error reading url.txt file: {e}{Colors.RESET}")
        return None

def download_and_extract_diagram(project_url):
    """
    Download ZIP and extract only diagram.json to current directory
    
    Args:
        project_url (str): Wokwi project URL
    
    Returns:
        bool: True if successful, False if failed
    """
    try:
        # Extract project ID from URL
        project_id = project_url.split('/')[-1]
        # Possible endpoints to download ZIP
        zip_endpoints = [
            f"https://wokwi.com/api/projects/{project_id}/zip",
            f"https://wokwi.com/projects/{project_id}/zip", 
            f"https://wokwi.com/projects/{project_id}/download",
            f"https://wokwi.com/api/projects/{project_id}/export/zip"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/zip, application/octet-stream, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': project_url
        }
        
        print(f"{Colors.BLUE}Downloading ZIP file...{Colors.RESET}")
        
        for endpoint in zip_endpoints:
            try:
                response = requests.get(endpoint, headers=headers, stream=True, timeout=30)
                
                if response.status_code == 200:
                    # Check content-type
                    content_type = response.headers.get('content-type', '').lower()
                    if 'zip' in content_type or 'octet-stream' in content_type:
                        # Create temporary file for ZIP
                        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    temp_zip.write(chunk)
                            temp_zip_path = temp_zip.name
                        
                        # Extract only diagram.json
                        try:
                            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                                file_list = zip_ref.namelist()
                                
                                # Find diagram.json file
                                diagram_files = [f for f in file_list if f.endswith('diagram.json')]
                                
                                if diagram_files:
                                    diagram_file = diagram_files[0]  # Take the first file
                                    
                                    # Extract diagram.json to current directory
                                    with zip_ref.open(diagram_file) as source:
                                        diagram_content = source.read()
                                        
                                        # Save to current directory
                                        output_path = "diagram.json"
                                        with open(output_path, 'wb') as target:
                                            target.write(diagram_content)
                                        
                                        print(f"{Colors.GREEN}✓ Successfully extracted diagram.json!{Colors.RESET}")
                                        
                                        # Clean up temporary file
                                        try:
                                            os.unlink(temp_zip_path)
                                        except:
                                            pass
                                        return True
                                else:
                                    print(f"{Colors.YELLOW}⚠ diagram.json file not found in ZIP{Colors.RESET}")
                                        
                        except zipfile.BadZipFile:
                            print(f"{Colors.RED}ERROR: Downloaded file is not a valid ZIP{Colors.RESET}")
                        except Exception as e:
                            print(f"{Colors.RED}ERROR during extraction: {e}{Colors.RESET}")
                        finally:
                            # Clean up temporary file
                            try:
                                if os.path.exists(temp_zip_path):
                                    os.unlink(temp_zip_path)
                            except:
                                pass
                                
            except requests.exceptions.RequestException:
                continue
                
        return False
        
    except Exception as e:
        print(f"{Colors.RED}ERROR: {e}{Colors.RESET}")
        return False

def main():
    print("=" * 60)
    print("Wokwi Diagram.json Extractor")
    print("=" * 60)
    
    # Read URL from file
    project_url = read_url_from_file()
    
    if not project_url:
        project_url = "https://wokwi.com/projects/443059386202798081"
    
    # Download and extract diagram.json only
    success = download_and_extract_diagram(project_url)
    
    if success:
        print(f"\n{Colors.GREEN}Completed{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}❌ FAILED{Colors.RESET}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())