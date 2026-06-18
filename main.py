import time
import sys
from datetime import datetime
from config import DURATION_MINUTES, MAX_ITERATIONS
from planner import planner1_draft, planner2_critique, planner_review_executor
from executor import evaluate_plan, execute_plan

def time_remaining(start_time):
    elapsed = time.time() - start_time
    return max(0, int((DURATION_MINUTES * 60 - elapsed) / 60))

def run_loop(project_description):
    print(f"🚀 Starting Multi-Agent Debate Loop for:\n{project_description}")
    start_time = time.time()
    iteration = 1
    
    context = "Initial startup."
    
    while iteration <= MAX_ITERATIONS and time_remaining(start_time) > 0:
        print(f"\n🔄 --- Iteration {iteration} (Time left: {time_remaining(start_time)} mins) ---")
        
        # Debate Phase
        print("🧠 Planner 1 is drafting a plan...")
        draft_data = planner1_draft(project_description, context)
        draft_plan = draft_data.get("proposed_plan", "")
        
        print("🧐 Planner 2 is critiquing the draft...")
        critique_data = planner2_critique(draft_plan)
        
        agreed_plan = draft_plan
        if not critique_data.get("agreed", True):
            print("⚠️ Planner 2 rejected it! Planner 1 is adjusting...")
            new_draft = planner1_draft(project_description, f"Planner 2 rejected previous plan because: {critique_data.get('critique')}. Fix it.")
            agreed_plan = new_draft.get("proposed_plan", draft_plan)
            print("✅ Planners reached an agreement.")
        else:
            print("✅ Planner 2 approved the draft.")

        # Executor Evaluation Phase
        print("💻 Executor is evaluating the agreed plan...")
        eval_data = evaluate_plan(agreed_plan)
        
        final_plan_to_execute = agreed_plan
        if eval_data.get("decision", "ACCEPT") == "PROPOSE":
            print(f"✋ Executor PROPOSED a change: {eval_data.get('proposal')}")
            print("⚖️ Planners are reviewing the proposal...")
            review = planner_review_executor(eval_data.get("proposal"), agreed_plan)
            if review.get("approved", False):
                print("👍 Planners APPROVED the executor's proposal.")
                final_plan_to_execute = review.get("updated_plan", agreed_plan)
            else:
                print("👎 Planners REJECTED the executor's proposal. Enforcing original plan.")
        else:
            print("👍 Executor ACCEPTED the plan.")

        # Execution Phase
        print("⚙️ Executor is writing the code...")
        result = execute_plan(final_plan_to_execute)
        print(f"📝 Result: {result}")
        
        context = f"Last execution result: {result}"
        iteration += 1

    print("\n🏁 Multi-Agent Loop finished!")
    print("✅ Check 'generated_app/' for output files.")

if __name__ == "__main__":
    desc = sys.argv[1] if len(sys.argv) > 1 else "Build a python app"
    run_loop(desc)
