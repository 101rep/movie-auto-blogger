import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

class KlingAIClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("KLING_API_KEY", "")
        self.base_url = "https://api.klingai.com/v1"

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_video(self, prompt: str, aspect_ratio="9:16", duration="5", mode="std") -> dict:
        """
        Kling AI에 텍스트 프롬프트로 비디오 생성 작업을 요청합니다.
        """
        if not self.api_key:
            return {"error": "Kling API 키가 설정되지 않았습니다."}

        url = f"{self.base_url}/videos/text2video"
        payload = {
            "model": "kling-v1",
            "prompt": prompt,
            "aspect_ratio": aspect_ratio, # 9:16 (쇼츠 세로) 또는 16:9
            "duration": str(duration),    # 5 또는 10초
            "mode": mode                 # 'std' (표준) 또는 'pro' (고화질)
        }

        try:
            print(f"[Kling AI] 비디오 생성 요청 전송: \"{prompt[:30]}...\" (비율: {aspect_ratio}, {duration}초)")
            res = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            data = res.json()
            if res.status_code == 200 and data.get("code") == 0:
                task_id = data.get("data", {}).get("task_id")
                print(f"[Kling AI] 생성 작업 등록 성공 (Task ID: {task_id})")
                return {"success": True, "task_id": task_id}
            else:
                print(f"[Kling AI] 생성 요청 실패: {data}")
                return {"success": False, "error": data.get("message", "Unknown error")}
        except Exception as e:
            print(f"[Kling AI] 예외 발생: {e}")
            return {"success": False, "error": str(e)}

    def check_task_status(self, task_id: str) -> dict:
        """작업 진행 상태를 조회합니다."""
        url = f"{self.base_url}/videos/text2video/{task_id}"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=15)
            data = res.json()
            if res.status_code == 200 and data.get("code") == 0:
                task_data = data.get("data", {})
                status = task_data.get("task_status") # submitted, processing, succeed, failed
                return {
                    "status": status,
                    "result": task_data.get("task_result", {}),
                    "data": task_data
                }
            return {"status": "error", "message": data.get("message")}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def wait_and_download_video(self, task_id: str, output_path: str, max_wait_sec=300) -> str:
        """비디오 생성이 완료될 때까지 대기하고 완성된 MP4를 다운로드합니다."""
        print(f"[Kling AI] 비디오 렌더링 완료 대기 중... (최대 {max_wait_sec}초)")
        start_time = time.time()

        while time.time() - start_time < max_wait_sec:
            res = self.check_task_status(task_id)
            status = res.get("status")

            if status == "succeed":
                videos = res.get("result", {}).get("videos", [])
                if videos and "url" in videos[0]:
                    video_url = videos[0]["url"]
                    print(f"[Kling AI] 렌더링 완료! 비디오 다운로드 중 -> {output_path}")
                    
                    r = requests.get(video_url, stream=True, timeout=60)
                    if r.status_code == 200:
                        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                        with open(output_path, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                        print(f"[Kling AI] 다운로드 성공: {output_path}")
                        return output_path
                return None
            elif status == "failed":
                print(f"[Kling AI] 비디오 생성 실패: {res}")
                return None
            else:
                print(f"[Kling AI] 생성 진행 중 ({status})... 5초 후 재확인")
                time.sleep(5)

        print("[Kling AI] 대기 시간 초과")
        return None
