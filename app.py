import streamlit as st
import os
import json
from openai import OpenAI

# إعداد صفحة الويب
st.set_page_config(page_title="AI Video Studio", page_icon="🎬", layout="centered")

st.title("🎬 استديو إنتاج الفيديوهات بالذكاء الاصطناعي")
st.write("اصنع قصصك ورسومك المتحركة تلقائياً عبر إدخال فكرة بسيطة فقط!")

# قراءة مفتاح الـ API من أسرار Streamlit بأمان
openai_api_key = st.secrets.get("OPENAI_API_KEY")

# خانات الإدخال من المستخدم
topic_input = st.text_input("📝 أدخل فكرة القصة أو الموضوع:", "مغامرة عصفور صغير يتعلم الشجاعة في الغابة")
audience_input = st.selectbox("🎯 الفئة المستهدفة:", ["أطفال (قصص وترفيه)", "عام / تثقيفي", "تشويق ومغامرات"])
scenes_count = st.slider("🎞️ عدد المشاهد المطلوبة:", min_value=2, max_value=8, value=4)

# زر التشغيل
if st.button("🚀 ابدأ توليد السيناريو والمشاهد"):
    if not topic_input.strip():
        st.warning("⚠️ يرجى كتابة فكرة القصة أولاً!")
    elif not openai_api_key:
        st.error("⚠️ مفتاح OpenAI API غير موجود في إعدادات الأمان (Secrets). يرجى إضافته أولاً.")
    else:
        with st.spinner("🤖 جاري التواصل مع الذكاء الاصطناعي وتجهيز القصة الحقيقية..."):
            try:
                client = OpenAI(api_key=openai_api_key)
                
                prompt = f"""
                أنت مخرج ومؤلف قصص أطفال محترف. قم بتأليف قصة قصيرة بناءً على الموضوع التالي: "{topic_input}".
                الفئة المستهدفة: {audience_input}.
                عدد المشاهد المطلوبة: {scenes_count}.
                
                أجب حصرياً بصيغة JSON متوافقة مع هذا الهيكل دون أي نصوص إضافية:
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
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                story_data = json.loads(response.choices.message.content)
                
                # حفظ النتائج
                os.makedirs("outputs", exist_ok=True)
                with open("outputs/story_output.json", "w", encoding="utf-8") as f:
                    json.dump(story_data, f, ensure_ascii=False, indent=4)
                    
                st.success("✨ تم توليد القصة والسيناريو بالذكاء الاصطناعي بنجاح!")
                
                # عرض النتائج
                st.subheader("📜 تفاصيل المشاهد المولدة:")
                for scene in story_data.get("scenes", []):
                    with st.expander(f"المشهد {scene['scene_number']}"):
                        st.write(f"**الراوي:** {scene['narrator_text']}")
                        st.code(f"Prompt: {scene['visual_prompt']}", language="text")
                        
            except Exception as e:
                st.error(f حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")

        st.info("💡 الخطوة القادمة: ربط محرك توليد الصور وتجميع الفيديو لتصبح الأداة متكاملة تماماً!")
