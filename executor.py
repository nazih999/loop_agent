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
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=180)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"[Executor Error] محاولة {attempt+1} فشلت: {e}")
            if attempt < retries:
                time.sleep(5)
            else:
                return f"فشل التنفيذ بسبب خطأ في الاتصال: {e}"

def execute_plan(plan):
    prompt = f"""
أنت مبرمج ومنفذ مهام (Executor).
مهمتك هي تنفيذ الخطة التالية حرفياً، كتابة الكود اللازم، وإرجاع الكود ونتيجة التنفيذ فقط بدون أي مقدمات أو شروحات.
الخطة:
{plan}
"""
    return call_ollama(prompt)
