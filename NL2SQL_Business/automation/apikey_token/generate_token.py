#!/usr/bin/env python3
"""
Script to generate Agent Behavior file for watsonx.data Bootcamp

Usage:
    python generate_token.py --env-file ../../../../student_creds/env.txt 
"""

import subprocess
import argparse
import os

def read_configuration(file_path):
    """
    Reads the configuration file and extracts the environment variables username and API key.
    Handles formats like: WXD_USER="username"
    """
    username = ""
    api_key = ""
    
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Look for the target variables
                if "WXD_USER=" in line:
                    # 1. split('=')[1] gets the right side of the equals sign
                    # 2. strip() removes newline characters and spaces
                    # 3. strip('"\'') removes double and single quotes
                    username = line.split('=')[1].strip().strip('"\'')
                elif "WXD_API_KEY=" in line:
                    api_key = line.split('=')[1].strip().strip('"\'')
                    
        return username, api_key
    except FileNotFoundError:
        print(f"Error: Could not find the file '{file_path}'.")
        return None, None

def execute_base64_command(username, api_key):
    """
    Asks the user for their operating system and executes the corresponding terminal command.
    """
    credentials = f"{username}:{api_key}"
    
    print("\nWhich operating system are you using?")
    print("1. Mac / Linux")
    print("2. Windows")
    
    choice = input("Enter 1 or 2: ")
    
    if choice == "1":
        # Command for Mac/Linux using bash
        mac_command = f'echo -n "{credentials}" | base64'
        print("\nExecuting in Bash...")
        subprocess.run(mac_command, shell=True, executable='/bin/bash')
        
    elif choice == "2":
        # Command for Windows using PowerShell
        win_command = f'[Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("{credentials}"))'
        print("\nExecuting in PowerShell...")
        subprocess.run(["powershell", "-Command", win_command])
        
    else:
        print("Invalid choice. Please run the script again.")

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Extract credentials from a env.txt file and encode them in Base64.")
    
    parser.add_argument("--env-file", default="../../../../student_creds/env.txt", help="Path to the variables .txt file")
    
    args = parser.parse_args()
    
    print(f"Starting script... Reading from: '{args.env_file}'\n")
    
    # 1. Retrieve the variables from the text file
    username, api_key = read_configuration(args.env_file)
    
    # Verify that both variables were successfully found
    if username and api_key:
        print(f"Variables loaded successfully! (User: {username}, API Key: ****{api_key[-4:]})")
        # 2. Execute the terminal logic based on the OS
        execute_base64_command(username, api_key)
    else:
        print(f"Missing variables. Ensure WXD_USER and WXD_API_KEY exist in '{args.env_file}'.")

if __name__ == "__main__":
    main()