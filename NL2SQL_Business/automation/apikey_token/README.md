# NL2SQL Business Lab - Generate API Key Authorization Token

This directory contains a python script for NL2SQL Business Lab that automates the creation of the API Key Authorization token needed to use the watsonx.data remote MCP Server

## Prerequisites

- Python 3.9 or higher
- [env.txt](../../../../student_creds/env.txt) file with `WXD_USER` and `WXD_API_KEY` values set

## Files

- **`generate_token.py`** - Automates ApiKey Authorization Token creation
- **`README.md`** - This file

## Usage

- Open a terminal window in your root directory
- Execute the following:

1. Create virtual environment

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2. Run the script
   ```bash
   cd ./student/Labs/NL2SQL_Business/automation/apikey_token
   python generate_token.py
   ```

## What the Script Does

- Read environment variables from `env.txt` file
- Ask the user for his Operating System ( Mac/Linux or Windows)
- Execute a bash command to create a Base64-encoded authorization token.
- Show that token in the terminal

## Arguments

- The script uses the default location for the `env.txt` file, but you can use a different paths and execute the script with the following argument:
  - **--env-file** _path for the env.txt file_

- Return to [Configure watsonx.data Remote MCP Server Connection](../../watsonxdata_connection.md) to continue creating your remote MCP Server connection
