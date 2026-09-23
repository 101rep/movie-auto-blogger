import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TTSEngine:
    def __init__(self, api_key=None, voice_id="pNInz6obpgDQGcFmaJgB"): # Adam / Korean capable voice
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")
        
    def generate_speech(self, text: str, output_path: str, voice_id: str = None) -> str:
        """ElevenLabs API를 호출하여 한국어 음성 파일을 생성합니다."""
        target_voice = voice_id or self.voice_id
        
        if not self.api_key:
            print("[TTS] ElevenLabs API 키가 없습니다. Edge-TTS 백업 모드로 전환합니다.")
            return self._generate_edge_tts(text, output_path)
            
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{target_voice}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.2,
                "use_speaker_boost": True
            }
        }
        
        try:
            print(f"[TTS] ElevenLabs API 음성 합성 요청 중... (글자수: {len(text)})")
            response = requests.post(url, json=data, headers=headers, timeout=30)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"[TTS] 음성 생성 성공: {output_path}")
                return output_path
            else:
                print(f"[TTS] ElevenLabs 오류 ({response.status_code}): {response.text}")
                print("[TTS] 백업 Edge-TTS로 재시도합니다.")
                return self._generate_edge_tts(text, output_path)
        except Exception as e:
            print(f"[TTS] ElevenLabs 요청 예외 발생: {e}")
            return self._generate_edge_tts(text, output_path)

    def _generate_edge_tts(self, text: str, output_path: str) -> str:
        """무료 Edge-TTS 백업 음성 생성"""
        import asyncio
        import edge_tts
        
        async def _run():
            voice = "ko-KR-SunHiNeural" # 또는 ko-KR-InJoonNeural
            communicate = edge_tts.Communicate(text, voice)
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            await communicate.save(output_path)

        try:
            asyncio.run(_run())
            print(f"[TTS-Backup] Edge-TTS 음성 생성 성공: {output_path}")
            return output_path
        except Exception as e:
            print(f"[TTS-Backup] Edge-TTS 실패: {e}")
            raise e
