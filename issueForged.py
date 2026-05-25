#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
issueForged

A simple yet powerful Python utility that converts Markdown files, specifically 
outline or task lists, into Gitea/GitHub Issues, then onto Git Projects as needed.

Website: https://code.oldmanumby.com
"""

author = "B.A. Umberger (Old Man Umby)"
copyright = "Copyright 2026, B.A. Umberger"
credits = ["B.A. Umberger"]
license = "GPL-3.0"
version = "1.0.0"
maintainer = "B.A. Umberger"
status = "Production"

import re
import json
import subprocess
import os
from pathlib import Path
import configparser
import sys

# Configuration file
CONFIG_FILE = 'issueForged.conf'

def save_config(config):
    """Save configuration to file"""
    config_parser = configparser.ConfigParser()
    config_parser['DEFAULT'] = config
    with open(CONFIG_FILE, 'w') as f:
        config_parser.write(f)
    print(f"Configuration saved to {CONFIG_FILE}")

def load_config():
    """Load configuration from file or create default"""
    default_config = {
        'input_file': '_docs/my_markdown_file.md',
        'repo_api_url': 'https://git.oldmanumby.com/api/v1/repos/tabletop.ninja/grog.space/issues',
        'token': 'ce441ef64de4598b930fda7116afa7aa39be35a2',
        'section_pattern': '##',
        'ignore_patterns': '# Phase,# Revised Phase',
        'assignee': 'dev',
        'label_name': 'planned'
    }
    
    config_parser = configparser.ConfigParser()
    
    # If config file exists, read it
    if os.path.exists(CONFIG_FILE):
        config_parser.read(CONFIG_FILE)
        if 'DEFAULT' in config_parser:
            return dict(config_parser['DEFAULT'])
    
    # Otherwise return default
    return default_config

def read_file(file_path):
    """Read content from a file"""
    with open(file_path, 'r') as f:
        return f.read()

def preview_headers(file_path):
    """Preview the different header levels in the file"""
    content = read_file(file_path)
    lines = content.split('\n')
    
    header_patterns = {}
    for line in lines:
        if line.startswith('#'):
            header_level = 0
            for i, char in enumerate(line):
                if char == '#':
                    header_level += 1
                else:
                    break
            
            if header_level not in header_patterns:
                header_patterns[header_level] = []
            
            # Add the header to the list if it's not already there
            example = line.strip()
            if len(header_patterns[header_level]) < 3 and example not in header_patterns[header_level]:
                header_patterns[header_level].append(example)
    
    return header_patterns

def parse_sections(content, section_pattern, ignore_patterns=None):
    """Parse sections based on the provided pattern"""
    sections = {}
    current_section = None
    current_content = []
    
    lines = content.split('\n')
    
    # Convert ignore_patterns to a list if it's a string
    if ignore_patterns and isinstance(ignore_patterns, str):
        ignore_patterns = [p.strip() for p in ignore_patterns.split(',')]
    else:
        ignore_patterns = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # If we find a new section header
        if line.startswith(section_pattern + ' '):
            # If we were collecting a previous section, save it
            if current_section:
                # Clean up content: remove any trailing lines that match ignore patterns
                while current_content and any(current_content[-1].strip().startswith(pattern) for pattern in ignore_patterns):
                    current_content.pop()
                # Remove trailing empty lines
                while current_content and not current_content[-1].strip():
                    current_content.pop()
                    
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            current_section = line[len(section_pattern) + 1:].strip()  # Remove pattern and whitespace
            current_content = [line]  # Start with the header
        
        # If we're in a section, add content (but skip lines matching ignore_patterns)
        elif current_section and not any(line.strip().startswith(pattern) for pattern in ignore_patterns):
            current_content.append(line)
        
        i += 1
    
    # Don't forget the last section
    if current_section:
        # Same cleanup for the last section
        while current_content and any(current_content[-1].strip().startswith(pattern) for pattern in ignore_patterns):
            current_content.pop()
        while current_content and not current_content[-1].strip():
            current_content.pop()
            
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def get_label_id(repo_api_url, token, label_name):
    """Get label ID by name from Gitea API"""
    if not label_name:
        return None
        
    # Convert the issues URL to labels URL
    # From: https://git.oldmanumby.com/api/v1/repos/tabletop.ninja/grog.space/issues
    # To:   https://git.oldmanumby.com/api/v1/repos/tabletop.ninja/grog.space/labels
    labels_url = repo_api_url.replace('/issues', '/labels')
    
    # Use curl to get all labels
    cmd = [
        'curl',
        '-s',  # Silent mode
        '-X', 'GET',
        labels_url,
        '-H', 'accept: application/json',
        '-H', f'Authorization: token {token}'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        labels = json.loads(result.stdout)
        
        # Find the label by name (case insensitive)
        for label in labels:
            if label.get('name', '').lower() == label_name.lower():
                return label.get('id')
                
        # If we get here, the label wasn't found
        print(f"Warning: Label '{label_name}' not found in repository")
        return None
        
    except Exception as e:
        print(f"Error fetching labels: {e}")
        return None

def create_issue(title, body, config):
    """Create an issue in Gitea"""
    # Prepare the JSON payload
    payload = {
        "title": title,
        "body": body,
    }
    
    # Add assignee if specified
    if config.get('assignee'):
        payload["assignee"] = config['assignee']
    
    # Add labels if specified - use name to look up ID
    if config.get('label_name'):
        # Try to get the label ID from the API
        label_id = get_label_id(config['repo_api_url'], config['token'], config['label_name'])
        if label_id:
            payload["labels"] = [label_id]
            print(f"Using label: {config['label_name']} (ID: {label_id})")
        else:
            print(f"Warning: Label '{config['label_name']}' not found. Issue will be created without a label.")
    
    # Write payload to a temporary file to handle potential special characters
    with open('temp_payload.json', 'w') as f:
        json.dump(payload, f)
    
    # Use curl to create the issue
    cmd = [
        'curl',
        '-X', 'POST',
        config['repo_api_url'],
        '-H', 'accept: application/json',
        '-H', 'Content-Type: application/json',
        '-H', f'Authorization: token {config["token"]}',
        '-d', '@temp_payload.json'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Clean up
        Path('temp_payload.json').unlink()
        
        response = json.loads(result.stdout)
        if 'number' in response:
            print(f"Creating issue: {title} - Issue #{response['number']}")
        else:
            print(f"Created issue (no number returned): {title}")
            print("API Response:", response)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating issue: {e.stderr}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error parsing API response: {e}")
        print("Raw response:", result.stdout if 'result' in locals() else "No response")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        # Make sure we clean up the temporary file
        if Path('temp_payload.json').exists():
            Path('temp_payload.json').unlink()

def configure():
    """Configure the script settings"""
    config = load_config()
    
    print("\nEnter the markdown file path and name...")
    
    # Input file
    input_file = input(f"Markdown file path [{config['input_file']}]:\n> ").strip()
    if input_file:
        config['input_file'] = input_file
    
    # Verify file exists
    if not os.path.exists(config['input_file']):
        print(f"Error: File '{config['input_file']}' does not exist.")
        return None
    
    # Preview header levels in the file
    print("\nAnalyzing header levels in the file...")
    header_patterns = preview_headers(config['input_file'])
    
    if header_patterns:
        print("\nI found the following header levels in your file:")
        for level, examples in sorted(header_patterns.items()):
            header_marker = '#' * level
            print(f"{level}: {header_marker} (Found in file: {', '.join(examples[:2])})")
        
        # Get the section pattern
        print("\nWhich header levels do you wish to use as the issue titles? Everything else between these headers will be sent to the body of the issue. Higher header levels will be ignored...")
        header_level = input(f"Desired header level (1-6) [header 2 is default]:\n> ").strip()
        
        if header_level and header_level.isdigit() and 1 <= int(header_level) <= 6:
            config['section_pattern'] = '#' * int(header_level)
        
        print(f"\n...I'm now using headers {header_level or '2'} ({config['section_pattern']}) for issue titles and added this to the config.")
    else:
        print("\nNo headers found in the file. Using default pattern.")
    
    # Repo API URL
    print("\nEnter the complete URL that points directly to the Issues API Endpoint for your specific repository, not just the base URL of the Git service. This endpoint is where POST requests will be sent to create new issues...")
    repo_api_url = input(f"Repository API URL:\n> ").strip()
    if repo_api_url:
        config['repo_api_url'] = repo_api_url
    
    # Token
    print("\nEnter the complete API Token for your Git/repo service...")
    token = input(f"API Token (press ENTER to keep existing config):\n> ").strip()
    if token:
        config['token'] = token
    
    # Ignore patterns
    print("\nIf you wish for issueForged to ignore specific headers based on patterns, enter those below...")
    ignore_patterns = input(f"Desired header patterns to ignore (comma-separated) [{config.get('ignore_patterns', '# My_Sample_Header,# Another_Ignored_Header')}]:\n> ").strip()
    if ignore_patterns:
        config['ignore_patterns'] = ignore_patterns
    
    # Additional issue parameters
    print("\nEnter any additional issue parameters...")
    
    # Assignee
    assignee = input(f"Issue Assignee:\n> ").strip()
    if assignee:
        config['assignee'] = assignee
    
    # Show available labels from the repository
    print("\nFetching available labels from repository...")
    try:
        labels_url = config['repo_api_url'].replace('/issues', '/labels')
        cmd = [
            'curl',
            '-s',  # Silent mode
            '-X', 'GET',
            labels_url,
            '-H', 'accept: application/json',
            '-H', f'Authorization: token {config["token"]}'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        labels = json.loads(result.stdout)
        
        print("\nAvailable labels in repository:")
        for label in labels:
            print(f"- {label.get('name')} ({label.get('description') or 'No description'})")
    except Exception as e:
        print(f"Could not fetch labels: {e}")
    
    # Label name
    label_name = input(f"\nLabel Name [current: {config.get('label_name', '')}]:\n> ").strip()
    if label_name:
        config['label_name'] = label_name
    
    # Remove label_id from config if it exists (we'll look it up dynamically)
    if 'label_id' in config:
        del config['label_id']
    
    # Save configuration
    save_config(config)
    
    return config

def main():
    print("::: issueForged :::")
    print("\nThis simple Python script converts the headers (#, ##, ###, etc.) in a GitHub-flavored markdown file into Gitea/GitHub issues. If this is your first time using issueForged, your selected options will create a config file for future use: Option 1 below; otherwise, choose Option 2...")
    
    print("\nConfig Options:")
    print("1. Use existing configuration")
    print("2. Select options manually")
    print("3. Exit")
    
    choice = input("\nEnter the config option (1-3):\n> ")
    
    config = None
    if choice == "1":
        config = load_config()
        
        # Verify that required settings are present
        if not os.path.exists(config['input_file']):
            print(f"Error: Markdown file '{config['input_file']}' not found.")
            print("Please reconfigure your settings.")
            return
    elif choice == "2":
        config = configure()
        if not config:
            return
    else:
        print("Exiting...")
        return
    
    print(f"\nReading task list from: {config['input_file']}...")
    content = read_file(config['input_file'])
    
    print(f"Parsing sections using pattern: {config['section_pattern']}...")
    sections = parse_sections(content, config['section_pattern'], config.get('ignore_patterns'))
    
    section_titles = list(sections.keys())
    section_count = len(section_titles)
    print(f"Found {section_count} sections")
    
    if section_count == 0:
        print(f"No sections found with pattern '{config['section_pattern']}'. Please check your section pattern.")
        return
    
    print("\nHow would you like to proceed?")
    print("1. TEST MODE: Create only the 1st issue to verify process")
    print("2. FULL MODE: Create all issues for all headers")
    print("3. FINIKY MODE: Choose which header/issues to create")
    print("4. Exit")
    
    mode_choice = input("\nEnter your choice (1-4):\n> ")
    
    if mode_choice == "1":
        # Test mode - create only the first issue
        print("\nTEST MODE: Will only create the 1st issue...")
        
        title = section_titles[0]
        body = sections[title]
        
        print(f"\n{title}")
        print("\n" + body)
        
        response = input("\nCreate this issue? (y/n):\n> ")
        if response.lower() != 'y':
            print("Aborted")
            return
        
        create_issue(title, body, config)
        print("\nTest issue created. Please verify the content and formatting.")
        
    elif mode_choice == "2":
        # Full mode - create all issues
        print("\nCreating all issues...")
        
        success_count = 0
        for title in section_titles:
            body = sections[title]
            
            if create_issue(title, body, config):
                success_count += 1
            else:
                print(f"Failed to create issue: {title}")
            
            # Ask to continue every 2 issues
            if success_count % 2 == 0 and success_count < section_count:
                response = input(f"\nCreated {success_count} of {section_count} issues. Continue? (y/n):\n> ")
                if response.lower() != 'y':
                    print("Stopped by user")
                    break
        
        print(f"\nCompleted: Created {success_count} of {section_count} issues")
        
    elif mode_choice == "3":
        # Selective mode - choose which issues to create
        print("\nFINIKY MODE available headers to issues:")
        
        for i, title in enumerate(section_titles, 1):
            print(f"{i}. {title}")
        
        selections = input("\nEnter headers to convert to issues (comma-separated, e.g. 1,3):\n> ")
        try:
            indices = [int(idx.strip()) - 1 for idx in selections.split(',')]
            selected_titles = [section_titles[idx] for idx in indices if 0 <= idx < len(section_titles)]
            
            if not selected_titles:
                print("No valid sections selected.")
                return
            
            response = input(f"\nI'm ready to create issues. Proceed? (y/n):\n> ")
            if response.lower() != 'y':
                print("Aborted")
                return
            
            success_count = 0
            for title in selected_titles:
                body = sections[title]
                
                if create_issue(title, body, config):
                    success_count += 1
                else:
                    print(f"Failed to create issue: {title}")
            
            print(f"\nCompleted: Created {success_count} of {len(selected_titles)} issues")
            
        except (ValueError, IndexError) as e:
            print(f"Error processing selections: {e}")
            return
    else:
        print("Exiting...")
        return

if __name__ == '__main__':
    main()