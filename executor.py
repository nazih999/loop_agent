import os
import re
import requests
import time
from config import OLLAMA_API_URL, EXECUTOR_MODEL

def call_ollama(prompt, retries=2):
    payload = {
        "model": EXECUTOR_MODEL,
        "prompt": prompt,
        "stream": False
    }
    for attempt in range(retries + 1):
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"[Executor Error] Attempt {attempt+1} failed: {e}")
            if attempt < retries:
                time.sleep(5)
            else:
                return f"Execution failed due to connection error: {e}"

def save_extracted_files(text):
    """
    Looks for blocks like:
    ### File: path/to/file.py
    ```python
    ... code ...
    ```
    And saves them physically to the generated_app directory.
    """
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

def execute_plan(plan):
    prompt = f"""
You are an expert Software Engineer and Executor.
Your task is to implement the provided plan EXACTLY.
Write the actual code. Do not skip or use placeholders.

CRITICAL INSTRUCTION FOR SAVING FILES:
If you write or modify a file, you MUST format your response EXACTLY like this:
### File: relative/path/to/filename.ext
```language
// full file code here
```

Plan to execute:
{plan}
"""
    result = call_ollama(prompt)
    saved_files = save_extracted_files(result)
    
    if saved_files:
        return f"Execution successful. Saved {len(saved_files)} files: {', '.join(saved_files)}\n\nExecutor output:\n{result}"
    return f"Execution completed, but no files were saved. Executor output:\n{result}"
