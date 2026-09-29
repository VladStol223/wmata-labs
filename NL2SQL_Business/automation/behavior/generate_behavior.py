#!/usr/bin/env python3
"""
Script to generate Agent Behavior file for watsonx.data Bootcamp

Usage:
    python generate_behavior.py --env-file ../../../../../student_creds/env.txt --presto-json ../../../../../student_creds/presto.json --template-file sql_agent_behavior_template.txt --output-file sql_agent_behavior.txt
"""

import json
import os
import argparse

def process_complex_template(env_file, presto_json, template_file, output_file):
    """
    Combines variables from an env.txt file and a Presto JSON config to populate a template.
    """
    variable_map = {}

    try:
        # --- 1. Parse Env File ---
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # .upper() ensures 'name' becomes 'NAME'
                        clean_key = key.strip().upper()
                        clean_value = value.strip().replace('"', '')
                        variable_map[clean_key] = clean_value

        # --- 2. Parse Presto JSON Config ---
        if os.path.exists(presto_json):
            with open(presto_json, 'r', encoding='utf-8') as f_json:
                config_data = json.load(f_json)
                variable_map["PRESTO_ENGINE"] = str(config_data["properties"]["connection"][2]["value"])

        # --- 3. Process Template ---
        if not os.path.exists(template_file):
            print(f"Error: Template '{template_file}' not found.")
            return

        with open(template_file, 'r', encoding='utf-8') as f_temp:
            content = f_temp.read()

        for key, value in variable_map.items():
            tag = f"<{key}>"
            content = content.replace(tag, value)

        # --- 4. Write Result ---
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(content)

        print(f"Successfully generated: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Template engine with ENV and JSON support.")

    # Define flags
    parser.add_argument("--env-file", default="../../../../../student_creds/env.txt", help="Path to the variables .txt file")
    parser.add_argument("--presto-json", default="../../../../../student_creds/presto.json", help="Path to the Presto config .json file")
    parser.add_argument("--template-file", default="sql_agent_behavior_template.txt", help="Path to the source template file")
    parser.add_argument("--output-file", default="sql_agent_behavior.txt", help="Path for the generated file (default: sql_agent_behavior.txt)")

    # Parse the arguments from terminal
    args = parser.parse_args()

    # Pass the arguments to the logic function
    process_complex_template(
        args.env_file, 
        args.presto_json, 
        args.template_file, 
        args.output_file
    )

if __name__ == "__main__":
    main()