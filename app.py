import streamlit as st
import os
import json
from google import genai

# إعداد صفحة الويب
st.set_page_config(page_title="AI Video Studio", page_icon="🎬", layout="centered")

st.title("🎬 استديو إنتاج الفيديوهات بالذكاء الاصطناعي")
st.write("اصنع قصصك ورسومك المتحركة تلقائياً عبر إدخال فكرة بسيطة فقط باستخدام Gemini!")

# قراءة مفتاح الـ API من أسرار Streamlit بأمان
gemini_api_key = st.secrets.get("GEMINI_API_KEY")

# خانات الإدخال من المستخدم
topic_input = st.text_input("📝 أدخل فكرة القصة أو الموضوع:", "مغامرة عصفور صغير يتعلم الشجاعة في الغابة")
audience_input = st.selectbox("🎯 الفئة المستهدفة:", ["أطفال (قصص وترفيه)", "عام / تثقيفي", "تشويق ومغامرات"])
scenes_count = st.slider("🎞️ عدد المشاهد المطلوبة:", min_value=2, max_value=8, value=4)

# زر التشغيل
if st.button("🚀 ابدأ توليد السيناريو والمشاهد"):
    if not topic_input.strip():
        st.warning("⚠️ يرجى كتابة فكرة القصة أولاً!")
    elif not gemini_api_key:
        st.error("⚠️ مفتاح GEMINI_API_KEY غير موجود في إعدادات الأمان (Secrets). يرجى إضافته أولاً.")
    else:
        with st.spinner("🤖 جاري التواصل مع Gemini وتجهيز القصة الحقيقية..."):
            try:
                # التهيئة باستخدام المكتبة الجديدة والمفتاح السري
                client = genai.Client(api_key=gemini_api_key)
                
                prompt = f"""
                أنت مخرج ومؤلف قصص أطفال محترف. قم بتأليف قصة قصيرة بناءً على الموضوع التالي: "{topic_input}".
                الفئة المستهدفة: {audience_input}.
                عدد المشاهد المطلوبة: {scenes_count}.
                
                أجب بصيغة JSON متوافقة حصرياً مع هذا الهيكل ودون أي نصوص إضافية:
                {{
                    "project_title": "عنوان القصة",
                    "character_design": {{"main_character": "صفات الشخصية الرئيسية بالإنجليزية لتوليد الصور"}},
                    "scenes": [
                        {{
                            "scene_number": 1,
                            "narrator_text": "نص الراوي للمشهد بالعربية",
                            "visual_prompt": "English prompt for image generation"
                        }}
                    ]
                }}
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                
                # تنظيف النص واستخراج الـ JSON بدقة
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                    
                story_data = json.loads(raw_text.strip())
                
                # حفظ النتائج
                os.makedirs("outputs", exist_ok=True)
                with open("outputs/story_output.json", "w", encoding="utf-8") as f:
                    json.dump(story_data, f, ensure_ascii=False, indent=4)
                    
                st.success("✨ تم توليد القصة والسيناريو بواسطة Gemini بنجاح!")
                
                # عرض النتائج
                st.subheader("📜 تفاصيل المشاهد المولدة:")
                for scene in story_data.get("scenes", []):
                    with st.expander(f"المشهد {scene['scene_number']}"):
                        st.write(f"**الراوي:** {scene['narrator_text']}")
                        st.code(f"Prompt: {scene['visual_prompt']}", language="text")
                        
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بـ Gemini: {e}")

        st.info("💡 الخطوة القادمة: ربط محرك توليد الصور وتجميع الفيديو لتصبح الأداة متكاملة تماماً!")
