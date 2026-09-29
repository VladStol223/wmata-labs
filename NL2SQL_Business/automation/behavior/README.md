# NL2SQL Business User Automation Script

This directory contains a python script for NL2SQL Business User. This script automates the creation of a behavior file that uses the catalog and schemas from the user watsonx.data instance.

## Purpose

The script eliminates manual addition of the file [sql_agent_behavior.txt](../assets/sql_agent_behavior.txt), that contains the behavior of the NL2SQL agent, making it faster to set up the lab environment for students.

## Files

- **`generate_behavior.py`** - Automates (NL2SQL Section 5.5)
- **`README.md`** - This file

## Prerequisites

- Python 3.9 or higher
- **env.txt** file in project root with required environment variables
- **presto.json** file with presto connection details, provided by the instructor

## Usage

1. Create virtual environment

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2. Run the script
   ```bash
   cd student/Labs/NL2SQL_Business/automation/behavior
   python generate_behavior.py \
     --env-file ../../../../student_creds/env.txt \
     --presto-json ../../../../student_creds/presto.json \
     --template-file ../../assets/sql_agent_behavior_template.txt \
     --output-file ../../assets/sql_agent_behavior.txt
   ```

## What the Script Does

- Read environment variables from `env.txt` file
- Read connection details from `presto.json` file
- Read `sql_agent_behavior_template.txt` file
- Replace placeholders in template file with values from environment variables
- Create a new `../../assets/sql_agent_behavior.txt` file to be use when defining NL2SQL agent behavior
  
## Verify completion:

- Script should report successful creation
- Check that a new file `../../assets/sql_agent_behavior.txt` was created

Return to the [Lab Guide](../../README.md#45-configure-agent-behavior)