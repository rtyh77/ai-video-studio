import streamlit as st
import os
import json
import requests
from groq import Groq

# إعداد صفحة الويب
st.set_page_config(page_title="AI Video Studio Pro - Groq", page_icon="🎬", layout="centered")

st.title("🎬 استديو إنتاج الفيديوهات بالذكاء الاصطناعي (محرك Groq السريع)")
st.write("اصنع قصصك ورسومك المتحركة تلقائياً وبأقصى سرعة عبر إدخال فكرة بسيطة فقط باستخدام Groq و Hugging Face!")

# قراءة مفاتيح الأمان من أسرار Streamlit
groq_api_key = st.secrets.get("GROQ_API_KEY", "")
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

# زر التشغيل
if st.button("🚀 ابدأ توليد السيناريو والرسومات عبر Groq"):
    if not topic_input.strip():
        st.warning("⚠️ يرجى كتابة فكرة القصة أولاً!")
    elif not groq_api_key:
        st.error("⚠️ مفتاح GROQ_API_KEY غير موجود في إعدادات الأمان (Secrets). يرجى إضافته أولاً.")
    else:
        with st.spinner("🤖 جاري توليد القصة والسيناريو بسرعة فائقة عبر محرك Groq..."):
            try:
                client = Groq(api_key=groq_api_key)
                
                prompt = f"""
                أنت مخرج ومؤلف محترف. قم بتأليف قصة قصيرة بناءً على الموضوع التالي: "{topic_input}".
                الفئة المستهدفة: {audience_input}.
                عدد المشاهد المطلوبة: {scenes_count}.
                
                أجب بصيغة JSON متوافقة حصرياً مع هذا الهيكل ودون أي نصوص إضافية أو مقدمات (فقط الكود كـ JSON):
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
                
                # استخدام النموذج المعتمد والمتاح لجميع مفاتيح Groq المجانية
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that outputs strictly JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                raw_text = completion.choices[0].message.content.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                    
                story_data = json.loads(raw_text.strip())
                
                os.makedirs("outputs", exist_ok=True)
                with open("outputs/story_output.json", "w", encoding="utf-8") as f:
                    json.dump(story_data, f, ensure_ascii=False, indent=4)
                    
                st.success("✨ تم توليد القصة والسيناريو بنجاح خيالي! جاري رسم الصور...")
                
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
                        
            except Exception as e:
                st.error(f"حدث خطأ أثناء التنفيذ: {e}")

        st.info("💡 الأداة تعمل الآن بأقصى سرعة وكفاءة عبر محركات قوية ومستقرة!")
