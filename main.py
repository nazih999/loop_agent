import time
import sys
from datetime import datetime
from config import DURATION_MINUTES, MAX_ITERATIONS
from planner import generate_initial_plan, critique_and_plan_next
from executor import execute_plan
from logger import log_iteration, generate_final_report

def time_remaining(start_time):
    elapsed = time.time() - start_time
    total_seconds = DURATION_MINUTES * 60
    return max(0, int((total_seconds - elapsed) / 60))

def run_loop(project_description):
    print(f"🚀 بدء تشغيل النظام للمشروع: {project_description}")
    start_time = time.time()
    
    print("⏳ جاري التخطيط الأولي...")
    plan = generate_initial_plan(project_description)
    
    iteration = 1
    
    while iteration <= MAX_ITERATIONS and time_remaining(start_time) > 0:
        print(f"\n🔄 التكرار رقم {iteration} (الوقت المتبقي: {time_remaining(start_time)} دقيقة)")
        
        print("💻 جاري التنفيذ من طرف Executor...")
        result = execute_plan(plan)
        
        print("🧠 جاري التحليل من طرف Planner...")
        critique = critique_and_plan_next(plan, result, time_remaining(start_time), iteration)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_iteration(iteration, plan, result, critique, timestamp)
        
        if isinstance(critique, dict):
            plan = critique.get("next_plan", str(critique))
        else:
            plan = str(critique)
            
        iteration += 1

    print("\n🏁 انتهى الوقت أو تم الوصول للحد الأقصى للتكرارات!")
    print("📊 جاري توليد التقرير النهائي...")
    generate_final_report()
    print("✅ تم حفظ الملفات: log_detailed.json, log_readable.txt, final_report.txt")

if __name__ == "__main__":
    desc = sys.argv[1] if len(sys.argv) > 1 else "إنشاء تطبيق بايثون بسيط"
    run_loop(desc)
