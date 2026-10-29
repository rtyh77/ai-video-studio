import os
import json
from openai import OpenAI

# جلب مفتاح الـ API من متغيرات البيئة
api_key = os.environ.get("OPENAI_API_KEY")

def generate_story_board(topic, target_audience="children", num_scenes=5):
    """
    توليد القصة وتقسيم المشاهد والبرومبتات بشكل منظم تلقائياً
    """
    client = OpenAI(api_key=api_key)

    system_prompt = """
    أنت كاتب سيناريو ومخرج رسوم متحركة محترف. 
    مهمتك هي تحويل الفكرة المدخلة إلى سيناريو فيديو قصير مقسم إلى مشاهد، وتوليد برومبتات بصرية باللغة الإنجليزية لإنشاء الصور بنمط 3D Pixar.
    
    شروط هامة جداً:
    1. المخرجات يجب أن تكون صيغة JSON فقط بدون أي نص إضافي أو شرح.
    2. حدد وصفاً ثابتاً ومفصلاً للشخصيات الرئيسية (Character Consistency) واستخدم هذا الوصف في جميع البرومبتات البصرية.
    3. البرومبت البصري (visual_prompt) يجب أن يكون باللغة الإنجليزية لتفهمه نماذج توليد الصور بدقة.
    4. النص الراوي (narrator_text) يكون باللغة العربية ومشبعاً بالمشاعر والوضوح.
    """

    user_prompt = f"""
    قم بكتابة قصة قصيرة وممتعة عن: "{topic}"
    الفئة المستهدفة: {target_audience}
    عدد المشاهد المطلوب: {num_scenes} مشاهد.
    
    رجع النتيجة بهذا الهيكل الدقيق:
    {{
        "project_title": "العنوان",
        "character_design": {{"main_character": "الوصف الإنجليزي الثابت"}},
        "scenes": [
            {{
                "scene_number": 1,
                "narrator_text": "النص العربي للراوي",
                "visual_prompt": "الوصف البصري بالإنجليزية مع مواصفات الشخصية الثابتة",
                "audio_file": "scene_1.mp3"
            }}
        ]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )

    story_data = json.loads(response.choices[0].message.content)
    return story_data

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    
    topic = "مغامرة عصفور صغير يتعلم الشجاعة والطيران"
    result = generate_story_board(topic, num_scenes=4)
    
    output_path = "outputs/story_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        
    print(f"تم إنشاء القصة بنجاح وحفظها في {output_path}")
