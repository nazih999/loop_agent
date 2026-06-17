import json
from datetime import datetime

log_data = []

def log_iteration(iteration_num, plan, result, critique, timestamp):
    entry = {
        "iteration": iteration_num,
        "timestamp": timestamp,
        "plan": plan,
        "execution_result": result,
        "critique": critique
    }
    log_data.append(entry)
    
    with open("log_detailed.json", "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=4)
        
    with open("log_readable.txt", "a", encoding="utf-8") as f:
        f.write(f"\n{'='*40}\n")
        f.write(f"Iteration: {iteration_num} | Time: {timestamp}\n")
        f.write(f"--- Plan ---\n{plan}\n\n")
        f.write(f"--- Execution Result ---\n{result}\n\n")
        f.write(f"--- Planner Critique ---\n{json.dumps(critique, ensure_ascii=False, indent=2)}\n")

def generate_final_report():
    total_iterations = len(log_data)
    report = f"""Final Execution Report
========================
Total Iterations Completed: {total_iterations}

Summary of Operations:
"""
    for entry in log_data:
        critique = entry.get("critique", {})
        if isinstance(critique, dict):
            report += f"\n- Iteration {entry['iteration']}:\n"
            report += f"  * Errors Found: {critique.get('errors', 'None')}\n"
            report += f"  * Solutions: {critique.get('solutions', 'None')}\n"
        
    with open("final_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
