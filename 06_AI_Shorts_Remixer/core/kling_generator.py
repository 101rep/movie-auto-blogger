import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

class KlingVideoGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("KLING_API_KEY", "")
        self.base_url = "https://api.klingai.com/v1"

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_text_to_video_task(self, prompt: str, duration: str = "5", aspect_ratio: str = "9:16", mode: str = "std") -> str:
        """
        Kling AI Text-to-Video 생성 작업을 요청합니다.
        duration: '5' 또는 '10' (초)
        aspect_ratio: '9:16' (쇼츠/세로), '16:9' (가로), '1:1' (정사각형)
        mode: 'std' (표준), 'pro' (고화질)
        """
        if not self.api_key:
            raise ValueError("[Kling AI] API 키가 설정되지 않았습니다.")

        url = f"{self.base_url}/videos/text2video"
        payload = {
            "model_name": "kling-v1",
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "mode": mode
        }

        print(f"[Kling AI] 비디오 생성 요청 중: \"{prompt[:30]}...\" ({aspect_ratio}, {duration}초)")
        response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
        
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("code") == 0 or "data" in res_data:
                task_id = res_data.get("data", {}).get("task_id")
                print(f"[Kling AI] 작업 접수 성공 (Task ID: {task_id})")
                return task_id
            else:
                raise RuntimeError(f"[Kling AI] API 응답 에러: {res_data}")
        else:
            raise RuntimeError(f"[Kling AI] HTTP 에러 ({response.status_code}): {response.text}")

    def wait_and_download(self, task_id: str, output_path: str, max_wait_sec: int = 300) -> str:
        """비디오 렌더링 완료를 대기하고 MP4 파일을 다운로드합니다."""
        url = f"{self.base_url}/videos/text2video/{task_id}"
        headers = self._get_headers()
        start_time = time.time()

        print(f"[Kling AI] 비디오 렌더링 대기 중... (최대 {max_wait_sec}초)")
        while time.time() - start_time < max_wait_sec:
            try:
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    task_status = data.get("task_status")
                    
                    if task_status == "succeed":
                        works = data.get("task_result", {}).get("videos", [])
                        if works:
                            video_url = works[0].get("url")
                            print(f"[Kling AI] 영상 렌더링 완료! 다운로드 중: {video_url}")
                            return self._download_file(video_url, output_path)
                    elif task_status == "failed":
                        err_msg = data.get("task_status_msg", "알 수 없는 오류")
                        raise RuntimeError(f"[Kling AI] 렌더링 실패: {err_msg}")
                    else:
                        print(f" - 진행 상태: {task_status}... (대기 중)")
            except Exception as e:
                print(f"[Kling AI] 상태 조회 중 예외: {e}")
            
            time.sleep(10)

        raise TimeoutError("[Kling AI] 비디오 생성 제한 시간(Timeout) 초과")

    def _download_file(self, url: str, output_path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        r = requests.get(url, stream=True, timeout=60)
        if r.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            print(f"[Kling AI] 파일 저장 완료: {output_path}")
            return output_path
        else:
            raise RuntimeError(f"[Kling AI] 다운로드 실패 ({r.status_code})")

    def generate_single_video(self, prompt: str, output_path: str, duration="5", aspect_ratio="9:16") -> str:
        """프롬프트 한 줄로 Kling AI 영상 생성 및 다운로드 원스톱 실행"""
        task_id = self.create_text_to_video_task(prompt, duration=duration, aspect_ratio=aspect_ratio)
        return self.wait_and_download(task_id, output_path)
