import os
import cv2
import json
import base64
from dotenv import load_dotenv

load_dotenv()

class VideoAnalyzer:
    def __init__(self, api_key=None):
        self.gemini_key = api_key or os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")

    def inspect_video(self, video_path: str) -> dict:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": f"Cannot open {video_path}"}
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        return {
            "path": video_path,
            "filename": os.path.basename(video_path),
            "duration": round(duration, 2),
            "fps": round(fps, 2),
            "resolution": f"{width}x{height}",
            "width": width,
            "height": height
        }

    def analyze_and_plan_shorts(self, video_paths: list, target_duration=15) -> dict:
        video_infos = [self.inspect_video(p) for p in video_paths]
        print(f"[Analyzer] 분석 대상 비디오 {len(video_infos)}개 검사 완료:")
        for info in video_infos:
            print(f" - {info.get('filename')}: {info.get('duration')}초 ({info.get('resolution')})")

        return self._generate_storyboard_with_llm(video_infos, target_duration)

    def _generate_storyboard_with_llm(self, video_infos: list, target_duration=15) -> dict:
        v_list_text = "\n".join([
            f"영상 {i+1} [파일명: {v['filename']}]: 전체 길이 {v['duration']}초"
            for i, v in enumerate(video_infos)
        ])

        system_prompt = f"""
당신은 유튜브 쇼츠 / 틱톡 / 릴스 1000만 조회수를 만드는 숏폼 영상 전문 PD 및 카피라이터입니다.
주어진 3개의 영상 클립을 지능적으로 조합(짜깁기)하여 총 {target_duration}초 분량의 폭발적인 반응을 이끌어낼 쇼츠 편집 계획서를 작성해야 합니다.

[영상 목록]
{v_list_text}

[작성 규칙]
1. 총 재생 시간은 정확히 {target_duration}초여야 합니다.
2. 3단 구성 필수:
   - 1단계 (0 ~ 3.5초): 강력한 시선 집중 후킹 (어그로 / 충격 질문 / 공감 유도)
   - 2단계 (3.5 ~ 9.5초): 핵심 반전 또는 제품/기능의 놀라운 효과 시연
   - 3단계 (9.5 ~ 15.0초): 결론, 비포/애프터 만족감, 프로필 링크/구매 유도(CTA)
3. 나레이션 대본(ElevenLabs 한국어 더빙용)은 자연스럽고 귀에 쏙쏙 박히는 구어체 한국어로 작성하세요.
4. 반드시 유효한 JSON 형식으로만 응답하세요.

[응답 JSON 스키마]
{{
  "title": "쇼츠 제목",
  "total_duration": {target_duration},
  "full_script": "전체 한국어 나레이션 대본",
  "cuts": [
    {{
      "cut_number": 1,
      "source_video": "{video_infos[0]['filename']}",
      "start_time": 0.0,
      "end_time": 4.0,
      "narration": "첫 번째 구간 대사",
      "caption": "화면에 띄울 큰 자막"
    }},
    {{
      "cut_number": 2,
      "source_video": "{video_infos[1 % len(video_infos)]['filename']}",
      "start_time": 1.0,
      "end_time": 6.5,
      "narration": "두 번째 구간 대사",
      "caption": "화면에 띄울 큰 자막"
    }},
    {{
      "cut_number": 3,
      "source_video": "{video_infos[2 % len(video_infos)]['filename']}",
      "start_time": 0.5,
      "end_time": 5.5,
      "narration": "세 번째 구간 대사",
      "caption": "화면에 띄울 큰 자막"
    }}
  ]
}}
"""
        if self.gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_key)
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=system_prompt,
                    config={"response_mime_type": "application/json"}
                )
                res_text = response.text.strip()
                return json.loads(res_text)
            except Exception as e:
                print(f"[Analyzer] Gemini 분석 오류: {e}")

        # 기본 fallback
        return {
            "title": "진작 알았으면 삶이 편해졌을 꿀템",
            "total_duration": target_duration,
            "full_script": "아직도 이걸 손으로 직접 하세요? 이거 하나만 쓱 올려두면 1초 만에 깔끔하게 해결됩니다. 삶의 질 수직 상승하네요!",
            "cuts": [
                {
                    "cut_number": 1,
                    "source_video": video_infos[0]['filename'],
                    "start_time": 0.0,
                    "end_time": 4.0,
                    "narration": "아직도 이걸 손으로 직접 하세요?",
                    "caption": "아직도 손으로 고생하세요? 😱"
                },
                {
                    "cut_number": 2,
                    "source_video": video_infos[1 % len(video_infos)]['filename'],
                    "start_time": 1.0,
                    "end_time": 7.0,
                    "narration": "이거 하나만 쓱 올려두면 1초 만에 깔끔하게 해결됩니다.",
                    "caption": "1초 만에 마법처럼 해결! ✨"
                },
                {
                    "cut_number": 3,
                    "source_video": video_infos[2 % len(video_infos)]['filename'],
                    "start_time": 0.5,
                    "end_time": 4.5,
                    "narration": "삶의 질 수직 상승하네요!",
                    "caption": "삶의 질 100배 상승 꿀템 🔥"
                }
            ]
        }
