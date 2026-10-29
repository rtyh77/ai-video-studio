import os
import json
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def assemble_video():
    """
    دمج الصور والتعليقات الصوتية لكل مشهد لإنتاج الفيديو النهائي
    """
    story_path = "outputs/story_output.json"
    if not os.path.exists(story_path):
        print("⚠️ ملف السيناريو غير موجود!")
        return

    with open(story_path, "r", encoding="utf-8") as f:
        story_data = json.load(f)

    scene_clips = []
    
    print("🎬 جاري بناء وترتيب مشاهد الفيديو...")
    
    for scene in story_data.get("scenes", []):
        scene_num = scene["scene_number"]
        img_path = scene.get("image_path")
        audio_path = scene.get("audio_path")
        
        # التأكد من وجود ملف الصورة والصوت للمشهد
        if os.path.exists(img_path) and os.path.exists(audio_path):
            # تحميل ملف الصوت لمعرفة مدته الزمنية الدقيقة
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # إنشاء مقطع الصورة وتحديد مدته بناءً على مدة الصوت
            image_clip = ImageClip(img_path).set_duration(duration)
            
            # دمج الصورة مع الصوت الخاص بالمشهد
            video_scene = image_clip.set_audio(audio_clip)
            scene_clips.append(video_scene)
            
            print(f"-> تم ربط مشهد {scene_num} (المدة: {duration:.2f} ثانية)")
        else:
            print(f"⚠️ تحذير: ملفات المشهد {scene_num} غير مكتملة (صورة أو صوت مفقود).")

    if scene_clips:
        # دمج جميع المشاهد وراء بعضها لتشكيل الفيديو الكامل
        print("🔄 جاري دمج وتصدير الفيديو النهائي...")
        final_video = concatenate_videoclips(scene_clips, method="compose")
        
        os.makedirs("outputs/video", exist_ok=True)
        output_video_path = "outputs/video/final_project_video.mp4"
        
        # تصدير الفيديو بجودة مناسبة ومعدل إطارات 24fps
        final_video.write_videofile(
            output_video_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac"
        )
        
        print(f"🎉 مبروك! تم إنتاج الفيديو النهائي بنجاح وحفظه في: {output_video_path}")
    else:
        print("❌ لم يتم العثور على أي مشاهد صالحة للدمج.")

if __name__ == "__main__":
    assemble_video()
