import time
import sys
import json
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
    print(f"🚀 Starting Autonomous AI Agent Loop for project:\n{project_description[:100]}...")
    start_time = time.time()
    
    print("⏳ Generating Initial Plan...")
    plan, todo_list = generate_initial_plan(project_description)
    
    iteration = 1
    
    while iteration <= MAX_ITERATIONS and time_remaining(start_time) > 0:
        print(f"\n🔄 Iteration {iteration} (Time left: {time_remaining(start_time)} mins)")
        print(f"📝 Current To-Do List length: {len(todo_list)}")
        
        print("💻 Executor is running...")
        result = execute_plan(plan)
        
        print("🧠 Planner is analyzing the result...")
        critique = critique_and_plan_next(project_description, plan, result, todo_list, time_remaining(start_time))
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_iteration(iteration, plan, result, critique, timestamp)
        
        if isinstance(critique, dict):
            plan = critique.get("next_plan", str(critique))
            todo_list = critique.get("new_todo_list", todo_list)
        else:
            plan = str(critique)
            
        iteration += 1

    print("\n🏁 Loop finished! Generating final report...")
    generate_final_report()
    print("✅ Files saved: log_detailed.json, log_readable.txt, final_report.txt")
    print("✅ Generated app files are inside the 'generated_app/' folder.")

if __name__ == "__main__":
    desc = sys.argv[1] if len(sys.argv) > 1 else "Build a simple python app"
    run_loop(desc)
