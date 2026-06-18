import os
import re
import requests
import time
import json
from config import OLLAMA_API_URL, EXECUTOR_MODEL

def call_ollama(prompt, retries=2, json_format=False):
    payload = {
        "model": EXECUTOR_MODEL,
        "prompt": prompt,
        "stream": False
    }
    if json_format:
        payload["format"] = "json"
        
    for attempt in range(retries + 1):
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            if attempt < retries: time.sleep(5)
            else: return ""

def save_extracted_files(text):
    saved_files = []
    pattern = r"###\s*File:\s*([^\n]+)\n\s*```[a-zA-Z]*\n(.*?)```"
    matches = re.finditer(pattern, text, re.DOTALL)
    base_dir = "generated_app"
    os.makedirs(base_dir, exist_ok=True)
    
    for match in matches:
        filepath = match.group(1).strip()
        code = match.group(2)
        full_path = os.path.join(base_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(code)
        saved_files.append(filepath)
    return saved_files

def evaluate_plan(plan):
    prompt = f"""
You are the Executor (Lead Developer).
Read the following plan provided by the Planners:
{plan}

Do you ACCEPT this plan as is, or do you PROPOSE a better technical approach?
Return STRICT JSON:
{{
  "decision": "ACCEPT", 
  "proposal": "If PROPOSE, explain your better approach. If ACCEPT, leave empty."
}}
"""
    res = call_ollama(prompt, json_format=True)
    try:
        data = json.loads(res)
        return data
    except:
        return {"decision": "ACCEPT", "proposal": ""}

def execute_plan(plan):
    prompt = f"""
You are the Executor. Implement the plan EXACTLY.
Write actual code. Do not skip.
CRITICAL INSTRUCTION FOR SAVING FILES:
If you write a file, you MUST format your response EXACTLY like this:
### File: path/to/filename.ext
```language
// code
```

Plan:
{plan}
"""
    result = call_ollama(prompt)
    saved_files = save_extracted_files(result)
    
    if saved_files:
        return f"Execution successful. Saved {len(saved_files)} files: {', '.join(saved_files)}"
    return f"Execution completed, no files saved."
