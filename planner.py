import json
import requests
import time
import os
from config import OLLAMA_API_URL, PLANNER_MODEL

def call_ollama(prompt, retries=2):
    payload = {
        "model": PLANNER_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    for attempt in range(retries + 1):
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
            response.raise_for_status()
            return response.json().get("response", "{}")
        except Exception as e:
            print(f"[Planner Error] Attempt {attempt+1} failed: {e}")
            if attempt < retries:
                time.sleep(5)
            else:
                return "{}"

def get_file_tree():
    tree = []
    base_dir = "generated_app"
    if not os.path.exists(base_dir):
        return "No files generated yet."
    for root, dirs, files in os.walk(base_dir):
        level = root.replace(base_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree.append(f"{subindent}{f}")
    return "\n".join(tree)

def generate_initial_plan(project_description):
    prompt = f"""
You are an expert Software Architect and AI Project Manager.
Project Description:
{project_description}

Your task: Create a detailed, step-by-step implementation plan (To-Do List) for building this app.
Break it down into small, executable steps.

You MUST respond strictly in JSON format with the following keys:
"analysis": "Brief analysis of the project requirements",
"todo_list": ["Step 1...", "Step 2...", "Step 3..."],
"plan": "Detailed instruction for the very first step to give to the executor."
"""
    result = call_ollama(prompt)
    try:
        data = json.loads(result)
        return data.get("plan", result), data.get("todo_list", [])
    except json.JSONDecodeError:
        return result, []

def critique_and_plan_next(project_description, previous_plan, execution_result, todo_list, time_remaining):
    file_tree = get_file_tree()
    
    prompt = f"""
You are the Software Architect monitoring the execution.
Original Project Goal:
{project_description}

Current File Tree:
{file_tree}

Previous Instruction Given:
{previous_plan}

Executor Result:
{execution_result}

Remaining To-Do List:
{todo_list}

Time Remaining: {time_remaining} minutes.

Analyze the result. If the step was successful, pop it from the todo list and plan the next step. If it failed or was incomplete, instruct the executor to fix it.

You MUST respond strictly in JSON format with these keys:
"analysis": "Review of the execution",
"errors": "Any bugs or missing requirements found",
"solutions": "How to fix the errors",
"new_todo_list": ["Remaining step 1", "Remaining step 2..."],
"next_plan": "The exact instruction for the executor for the next step. Must be highly detailed."
"""
    result = call_ollama(prompt)
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        print("[Planner] Failed to decode JSON. Attempting self-correction...")
        return {
            "analysis": "Failed to parse JSON output.",
            "errors": "JSON format error",
            "solutions": "Will retry formatting",
            "new_todo_list": todo_list,
            "next_plan": "Continue with the current task, but ensure you output files using the correct ### File: format."
        }
