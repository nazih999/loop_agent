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
        f.write(f"التكرار رقم: {iteration_num} | الوقت: {timestamp}\n")
        f.write(f"--- الخطة ---\n{plan}\n\n")
        f.write(f"--- نتيجة التنفيذ ---\n{result}\n\n")
        f.write(f"--- تحليل المخطط ---\n{json.dumps(critique, ensure_ascii=False, indent=2)}\n")

def generate_final_report():
    total_iterations = len(log_data)
    report = f"""تقرير نهاية التشغيل
========================
عدد التكرارات المنفذة: {total_iterations}

ملخص العمليات:
"""
    for entry in log_data:
        critique = entry.get("critique", {})
        if isinstance(critique, dict):
            report += f"\n- تكرار {entry['iteration']}:\n"
            report += f"  * أخطاء مصححة: {critique.get('errors', 'لا يوجد')}\n"
            report += f"  * أفكار جديدة: {critique.get('new_ideas', 'لا يوجد')}\n"
        
    with open("final_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
