import os
import json
import requests

def load_story():
    """قراءة ملف السيناريو والمشاهد الناتج من المرحلة الأولى"""
    path = "outputs/story_output.json"
    if not os.path.exists(path):
        print("⚠️ ملف السيناريو غير موجود! يرجى تشغيل script_generator.py أولاً.")
        return None
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_voiceovers(story_data):
    """
    هنا يتم ربط النصوص بالتعليق الصوتي (مثلاً عبر ElevenLabs API)
    """
    print("🎙️ جاري توليد التعليقات الصوتية للمشاهد...")
    os.makedirs("outputs/audio", exist_ok=True)
    
    for scene in story_data.get("scenes", []):
        scene_num = scene["scene_number"]
        text = scene["narrator_text"]
        print(f"-> معالجة الصوت للمشهد {scene_num}: {text[:30]}...")
        
        # (ملاحظة: هنا يتم إضافة كود طلب الـ API الخاص بصوت ElevenLabs وحفظ الملف في outputs/audio/)
        # مثال وهمي لحفظ مسار الملف:
        scene["audio_path"] = f"outputs/audio/scene_{scene_num}.mp3"

    return story_data

def generate_visuals(story_data):
    """
    هنا يتم إرسال البرومبتات البصرية لتوليد الصور لكل مشهد
    """
    print("🎨 جاري توليد الصور والمشاهد البصرية...")
    os.makedirs("outputs/images", exist_ok=True)
    
    character_base = story_data.get("character_design", {}).get("main_character", "")
    
    for scene in story_data.get("scenes", []):
        scene_num = scene["scene_number"]
        visual_prompt = scene["visual_prompt"]
        
        # دمج وصف الشخصية الثابت مع وصف المشهد لضمان ثبات الملامح (Character Consistency)
        full_prompt = f"{character_base}, {visual_prompt}"
        print(f"-> توليد صورة المشهد {scene_num} بالبرومبت: {full_prompt[:50]}...")
        
        # (ملاحظة: هنا يتم إضافة طلب الـ API الخاص بنموذج الصور وحفظ الصورة في outputs/images/)
        scene["image_path"] = f"outputs/images/scene_{scene_num}.png"

    return story_data

if __name__ == "__main__":
    story = load_story()
    if story:
        story = generate_voiceovers(story)
        story = generate_visuals(story)
        
        # تحديث ملف الـ JSON بمسارات الصور والأصوات الجديدة
        output_path = "outputs/story_output.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(story, f, ensure_ascii=False, indent=4)
            
        print("✅ تمت معالجة وتجهيز جميع مسارات الصور والأصوات بنجاح!")
