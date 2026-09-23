import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips
from core.subtitle_cleaner import SubtitleCleaner
from core.sound_engine import SoundFXEngine

class VideoEditor:
    def __init__(self, output_width=1080, output_height=1920, fps=30):
        self.width = output_width
        self.height = output_height
        self.fps = fps
        self.cleaner = SubtitleCleaner(mode="smart_blur")
        self.font_path = self._find_korean_font()
        self.sound_engine = SoundFXEngine(temp_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "temp"))

    def _find_korean_font(self):
        candidates = [
            "C:/Windows/Fonts/malgunbd.ttf",
            "C:/Windows/Fonts/malgun.ttf",
            "C:/Windows/Fonts/gulim.ttc",
            "C:/Windows/Fonts/batang.ttc"
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return None

    def create_caption_image(self, text: str) -> np.ndarray:
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(self.font_path, 64) if self.font_path else ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        x = (self.width - text_w) // 2
        y = int(self.height * 0.76)

        padding_x = 30
        padding_y = 16
        box_x0 = x - padding_x
        box_y0 = y - padding_y
        box_x1 = x + text_w + padding_x
        box_y1 = y + text_h + padding_y

        draw.rounded_rectangle([box_x0, box_y0, box_x1, box_y1], radius=20, fill=(0, 0, 0, 185))

        outline_range = 3
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                if ox != 0 or oy != 0:
                    draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, 255))

        draw.text((x, y), text, font=font, fill=(255, 235, 59, 255))
        return np.array(img)

    def prepare_vertical_clip(self, clip: VideoFileClip) -> VideoFileClip:
        cw, ch = clip.size

        def clean_filter(get_frame, t):
            frame = get_frame(t)
            bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cleaned = self.cleaner.clean_frame(bgr)
            return cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB)

        cleaned_clip = clip.transform(clean_filter)

        bg_scale = max(self.width / cw, self.height / ch)
        bg_w, bg_h = int(cw * bg_scale), int(ch * bg_scale)
        bg_clip = cleaned_clip.resized((bg_w, bg_h))
        
        x_center = (bg_w - self.width) // 2
        y_center = (bg_h - self.height) // 2
        bg_clip = bg_clip.cropped(x1=x_center, y1=y_center, x2=x_center + self.width, y2=y_center + self.height)
        
        def blur_filter(get_frame, t):
            frame = get_frame(t)
            return cv2.GaussianBlur(frame, (51, 51), 0)
        
        bg_clip = bg_clip.transform(blur_filter)

        fg_scale = self.width / cw
        fg_w, fg_h = self.width, int(ch * fg_scale)
        fg_clip = cleaned_clip.resized((fg_w, fg_h))
        
        fg_y = (self.height - fg_h) // 2
        fg_clip = fg_clip.with_position(("center", fg_y))

        return CompositeVideoClip([bg_clip, fg_clip], size=(self.width, self.height))

    def render_shorts(self, plan: dict, video_dir: str, narration_audio_path: str, output_path: str) -> str:
        print(f"[Editor] 숏폼 영상 제작 시작: {plan.get('title')}")
        cut_clips = []
        caption_clips = []
        cut_start_times = []
        current_time = 0.0

        for cut in plan.get("cuts", []):
            src_name = cut["source_video"]
            src_path = os.path.join(video_dir, src_name)
            
            if not os.path.exists(src_path):
                for f in os.listdir(video_dir):
                    if f.endswith(".mp4") and (src_name in f or f in src_name):
                        src_path = os.path.join(video_dir, f)
                        break

            if not os.path.exists(src_path):
                continue

            vclip = VideoFileClip(src_path)
            start_t = min(cut.get("start_time", 0.0), vclip.duration - 0.5)
            end_t = min(cut.get("end_time", start_t + 4.0), vclip.duration)
            cut_duration = max(end_t - start_t, 1.0)

            sub = vclip.subclipped(start_t, end_t)
            vertical_sub = self.prepare_vertical_clip(sub).with_duration(cut_duration)
            cut_clips.append(vertical_sub)

            cut_start_times.append(current_time)

            caption_text = cut.get("caption", "")
            if caption_text:
                cap_img = self.create_caption_image(caption_text)
                cap_clip = ImageClip(cap_img).with_duration(cut_duration).with_start(current_time)
                caption_clips.append(cap_clip)

            current_time += cut_duration

        if not cut_clips:
            raise RuntimeError("합성할 유효한 비디오 클립이 없습니다.")

        final_video = concatenate_videoclips(cut_clips, method="compose")
        total_vid_dur = final_video.duration

        # 오디오 합성 (나레이션 + 시작 딩 + 컷 전환 슉 사운드 FX 믹싱)
        final_duration = min(total_vid_dur, 15.5)
        final_video = final_video.with_duration(final_duration)

        try:
            full_soundtrack = self.sound_engine.build_mixed_soundtrack(
                narration_path=narration_audio_path,
                cut_times=cut_start_times,
                total_duration=final_duration
            )
            mixed_audio = AudioFileClip(full_soundtrack).with_duration(final_duration)
            final_video = final_video.with_audio(mixed_audio)
            print("[Editor] 사운드 FX(후킹 딩, 전환 슉) + 나레이션 오디오 믹싱 완료!")
        except Exception as e:
            print(f"[Editor] 사운드 FX 믹싱 중 예외 (나레이션만 결합): {e}")
            if narration_audio_path and os.path.exists(narration_audio_path):
                narr = AudioFileClip(narration_audio_path).with_duration(final_duration)
                final_video = final_video.with_audio(narr)

        all_layers = [final_video] + [c for c in caption_clips if c.start < final_duration]
        composite_final = CompositeVideoClip(all_layers, size=(self.width, self.height)).with_duration(final_duration)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        print(f"[Editor] 최종 비디오 렌더링 중... -> {output_path}")
        
        composite_final.write_videofile(
            output_path,
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            preset="fast"
        )

        print(f"[Editor] 렌더링 완료! 저장 경로: {output_path}")
        return output_path
