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

def planner1_draft(project_description, context=""):
    prompt = f"""
You are Planner 1: The Lead Architect & Product Visionary.
Project Goal: {project_description}
Current File Tree: {get_file_tree()}
Execution Context: {context}

You have COMPLETE CREATIVE FREEDOM. 
- If you think of a new feature, a UX improvement, or error handling that would greatly benefit the user, ADD IT to the plan.
- Ensure the app is robust, bug-free, and handles all edge cases.
- CRITICAL for Mobile Apps: You must ensure the foundational project files (build.gradle, settings.gradle, AndroidManifest.xml) are created properly before or alongside the code.

Draft an actionable instruction for the Executor to implement the next logical step.
Return STRICT JSON:
{{
  "todo_list": ["step1", "step2"],
  "proposed_plan": "The highly detailed instruction for the executor"
}}
"""
    res = call_ollama(prompt)
    try: return json.loads(res)
    except: return {"todo_list": [], "proposed_plan": "Proceed with default implementation."}

def planner2_critique(draft_plan):
    prompt = f"""
You are Planner 2: The Critical Reviewer & UX Expert.
Your job is to review Planner 1's proposed plan.
Proposed Plan: {draft_plan}

- Evaluate if the plan is technically sound and avoids potential bugs.
- If Planner 1 added new creative features, evaluate them. Do they benefit the user? Are they practical?
- If the plan is solid, approve it. If there are flaws, missing error handling, or bad UX, reject it and provide reasons.

Return STRICT JSON:
{{
  "agreed": true,
  "critique": "Your reasoning, praise for good features, or suggested changes"
}}
"""
    res = call_ollama(prompt)
    try:
        data = json.loads(res)
        if "agreed" not in data: data["agreed"] = True
        return data
    except: return {"agreed": True, "critique": "Parse error, assuming agreed."}

def planner_review_executor(executor_proposal, current_plan):
    prompt = f"""
You are the Planning Board. The Executor read your plan but proposed a change.
Original Plan: {current_plan}
Executor's Proposal: {executor_proposal}

Decide whether to approve the executor's change based on code quality and user experience.
Return STRICT JSON:
{{
  "approved": true,
  "updated_plan": "The final instruction for the executor to run right now."
}}
"""
    res = call_ollama(prompt)
    try:
        data = json.loads(res)
        if "approved" not in data: data["approved"] = False
        return data
    except: return {"approved": False, "updated_plan": current_plan}
