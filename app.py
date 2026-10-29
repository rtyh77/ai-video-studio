import streamlit as st
import os
import json
import requests
from google import genai
from google.genai.errors import APIError

# إعداد صفحة الويب
st.set_page_config(page_title="AI Video Studio Pro", page_icon="🎬", layout="centered")

st.title("🎬 استديو إنتاج الفيديوهات بالذكاء الاصطناعي (النسخة المتقدمة)")
st.write("نظام ذكي متطور لإنتاج القصص والرسومات مع إدارة تلقائية لمفاتيح الذكاء الاصطناعي وخلو من الأخطاء!")

# دالة ذكية لجلب قائمة المفاتيح ودعم النظام المتقدم (Rotation)
def get_gemini_clients():
    keys_list = []
    # التحقق من وجود قائمة مفاتيح متعددة
    if "GEMINI_API_KEYS" in st.secrets:
        keys_list = list(st.secrets["GEMINI_API_KEYS"])
    # التحقق من وجود مفتاح فردي كاحتياطي
    elif "GEMINI_API_KEY" in st.secrets:
        keys_list = [st.secrets["GEMINI_API_KEY"]]
    
    clients = []
    for k in keys_list:
        if k.strip():
            clients.append(genai.Client(api_key=k))
    return clients

huggingface_api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")

# خانات الإدخال من المستخدم
topic_input = st.text_input("📝 أدخل فكرة القصة أو الموضوع:", "مغامرة عصفور صغير يتعلم الشجاعة في الغابة")
audience_input = st.selectbox("🎯 الفئة المستهدفة:", ["أطفال (قصص وترفيه)", "عام / تثقيفي", "تشويق ومغامرات"])
scenes_count = st.slider("🎞️ عدد المشاهد المطلوبة:", min_value=2, max_value=6, value=3)

# دالة توليد الصور عبر Hugging Face API
def generate_image_from_prompt(prompt_text):
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {}
    if huggingface_api_key:
        headers = {"Authorization": f"Bearer {huggingface_api_key}"}
    
    payload = {"inputs": prompt_text}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception:
        return None

# زر التشغيل بنظام التدوير المتقدم
if st.button("🚀 ابدأ توليد السيناريو والرسومات (نظام متطور)"):
    if not topic_input.strip():
        st.warning("⚠️ يرجى كتابة فكرة القصة أولاً!")
    else:
        clients = get_gemini_clients()
        if not clients:
            st.error("⚠️ لم يتم العثور على أي مفتاح GEMINI صالح في إعدادات الأمان (Secrets).")
        else:
            story_data = None
            success = False
            
            # حلقة التبديل التلقائي بين المفاتيح عند حدوث نفاد حصة أو خطأ
            for idx, client in enumerate(clients):
                with st.spinner(f"🤖 محاولة الاتصال عبر المفتاح الاحترافي رقم ({idx + 1})..."):
                    try:
                        prompt = f"""
                        أنت مخرج ومؤلف محترف. قم بتأليف قصة قصيرة بناءً على الموضوع التالي: "{topic_input}".
                        الفئة المستهدفة: {audience_input}.
                        عدد المشاهد المطلوبة: {scenes_count}.
                        
                        أجب بصيغة JSON متوافقة حصرياً مع هذا الهيكل ودون أي نصوص إضافية:
                        {{
                            "project_title": "عنوان القصة",
                            "scenes": [
                                {{
                                    "scene_number": 1,
                                    "narrator_text": "نص الراوي للمشهد بالعربية",
                                    "visual_prompt": "High quality cinematic prompt in English describing the scene in detail"
                                }}
                            ]
                        }}
                        """
                        
                        response = client.models.generate_content(
                            model="gemini-3.8-flash",
                            contents=prompt,
                        )
                        
                        raw_text = response.text.strip()
                        if raw_text.startswith("```json"):
                            raw_text = raw_text[7:]
                        if raw_text.endswith("```"):
                            raw_text = raw_text[:-3]
                            
                        story_data = json.loads(raw_text.strip())
                        success = True
                        break # نجحت العملية، اخرج من الحلقة
                        
                    except Exception as e:
                        # إذا حدث خطأ نفاد الحصص، ينتقل تلقائياً للمفتاح التالي في القائمة
                        continue
            
            if success and story_data:
                os.makedirs("outputs", exist_ok=True)
                with open("outputs/story_output.json", "w", encoding="utf-8") as f:
                    json.dump(story_data, f, ensure_ascii=False, indent=4)
                    
                st.success("✨ تم توليد القصة والسيناريو بنجاح تام عبر النظام المتقدم! جاري رسم الصور...")
                
                # عرض النتائج وتوليد الصور لكل مشهد
                st.subheader("📜 المشاهد والرسومات المولدة:")
                scenes_list = story_data.get("scenes", [])
                
                for scene in scenes_list:
                    scene_num = scene['scene_number']
                    narrator = scene['narrator_text']
                    v_prompt = scene['visual_prompt']
                    
                    with st.expander(f"🎬 المشهد رقم {scene_num}", expanded=True):
                        st.write(f"**🗣️ الراوي:** {narrator}")
                        st.code(f"AI Image Prompt: {v_prompt}", language="text")
                        
                        with st.spinner(f"🎨 جاري رسم صورة المشهد {scene_num} بجودة عالية..."):
                            img_bytes = generate_image_from_prompt(v_prompt)
                            if img_bytes:
                                st.image(img_bytes, caption=f"صورة المشهد {scene_num}", use_container_width=True)
                            else:
                                st.warning("⚠️ تعذر توليد الصورة لهذا المشهد مؤقتاً، يمكنك إعادة المحاولة.")
            else:
                st.error("❌ عذراً، لقد تجاوزت الحد الأقصى لجميع المفاتيح المتاحة في القائمة. يرجى إضافة مفتاح جديد أو الانتظار حتى يتجدد الحد.")

        st.info("💡 الأداة تعمل الآن بنظام مبرمج متقدم لضمان أعلى استقرار!")
