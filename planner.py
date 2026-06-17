import json
import requests
import time
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
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("response", "{}")
        except Exception as e:
            print(f"[Planner Error] محاولة {attempt+1} فشلت: {e}")
            if attempt < retries:
                time.sleep(5)
            else:
                return "{}"

def generate_initial_plan(project_description):
    prompt = f"""
أنت مهندس برمجيات ومخطط مشاريع (Planner).
وصف المشروع: {project_description}
المطلوب: ضع خطة أولية مفصلة للتنفيذ.
يجب أن تكون الإجابة بصيغة JSON تحتوي على مفتاح "plan" وقيمته نص الخطة.
"""
    result = call_ollama(prompt)
    try:
        return json.loads(result).get("plan", result)
    except json.JSONDecodeError:
        return result

def critique_and_plan_next(previous_plan, execution_result, time_remaining, log_history):
    prompt = f"""
أنت المخطط. قم بتحليل نتيجة التنفيذ التالية ووضع خطة للخطوة القادمة.
الخطة السابقة: {previous_plan}
نتيجة التنفيذ: {execution_result}
الوقت المتبقي: {time_remaining} دقيقة.

أرجع إجابتك بصيغة JSON حصراً تحتوي على المفاتيح التالية:
"analysis": "نص: تحليل النتيجة",
"errors": "نص: الأخطاء التي وجدتها",
"solutions": "نص: حلول الأخطاء",
"new_ideas": "نص: أفكار تطويرية",
"next_plan": "نص: الخطة التالية التي يجب على المنفذ القيام بها"
"""
    result = call_ollama(prompt)
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {
            "analysis": "فشل في تحليل JSON، تم استخدام النص الخام.",
            "errors": "غير معروف",
            "solutions": "غير معروف",
            "new_ideas": "غير معروف",
            "next_plan": result
        }
