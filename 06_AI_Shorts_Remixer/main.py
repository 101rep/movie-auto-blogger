import os
import sys
import glob

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from dotenv import load_dotenv
from core.video_analyzer import VideoAnalyzer
from core.tts_engine import TTSEngine
from core.video_editor import VideoEditor

load_dotenv()

def run_remixer(input_dir: str = None, output_file: str = None):
    print("==================================================")
    print("[AI 쇼츠 리믹스 & 로컬라이징 자동화 엔진 가동]")
    print("==================================================")

    # 1. 입력 영상 디렉토리 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if not input_dir:
        potential_dir = os.path.abspath(os.path.join(base_dir, "..", "분석실"))
        if os.path.exists(potential_dir):
            input_dir = potential_dir
        else:
            input_dir = os.path.join(base_dir, "input_videos")

    out_dir = os.path.join(input_dir, "분석실완료")
    os.makedirs(out_dir, exist_ok=True)

    mp4_files = [f for f in glob.glob(os.path.join(input_dir, "*.mp4")) if "분석실완료" not in f]
    if not mp4_files:
        print(f"[오류] {input_dir} 경로에 처리할 mp4 영상 파일이 없습니다.")
        return False

    print(f"[1/4] 입력 영상 탐색 완료: 총 {len(mp4_files)}개 발견")
    for f in mp4_files:
        print(f"  - {os.path.basename(f)}")

    # 2. AI 영상 분석 및 15초 스토리보드/대본 기획
    print("\n[2/4] [AI] 멀티모달 분석 및 15초 쇼츠 대본 기획 중...")
    analyzer = VideoAnalyzer()
    plan = analyzer.analyze_and_plan_shorts(mp4_files, target_duration=15)
    
    print("\n---------------- [기획된 15초 쇼츠 대본] ----------------")
    print(f"[*] 제목: {plan.get('title')}")
    print(f"[*] 전체 대본: {plan.get('full_script')}")
    print("[*] 컷 타임라인:")
    for cut in plan.get("cuts", []):
        print(f"   [컷 {cut.get('cut_number')}] 소스: {cut.get('source_video')} ({cut.get('start_time')}s~{cut.get('end_time')}s)")
        print(f"      자막: \"{cut.get('caption')}\"")
        print(f"      음성: \"{cut.get('narration')}\"")
    print("-------------------------------------------------------")

    # 3. ElevenLabs 한국어 고품질 TTS 더빙 생성
    print("\n[3/4] [TTS] ElevenLabs 고품질 한국어 음성 생성 중...")
    tts = TTSEngine()
    temp_dir = os.path.join(base_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    audio_path = os.path.join(temp_dir, "elevenlabs_narration.mp3")
    
    tts_text = plan.get("full_script")
    tts.generate_speech(tts_text, audio_path)

    # 4. 15초 9:16 세로 숏폼 렌더링 & BGM/효과음/자막 합성
    print("\n[4/4] [Video] 15초 숏폼 지능형 컷 편집 + BGM/SFX 사운드 믹싱 렌더링 중...")
    editor = VideoEditor(output_width=1080, output_height=1920, fps=30)
    
    if not output_file:
        safe_title = "".join([c for c in plan.get("title", "ai_shorts") if c.isalnum() or c in (' ', '_', '-')]).strip()
        output_file = os.path.join(out_dir, f"{safe_title}_15s_final.mp4")

    rendered_path = editor.render_shorts(
        plan=plan,
        video_dir=input_dir,
        narration_audio_path=audio_path,
        output_path=output_file
    )

    print("\n==================================================")
    print("[성공] 15초 AI 쇼츠 제작이 성공적으로 완료되었습니다!")
    print(f"[*] 완성본 파일: {rendered_path}")
    print("==================================================")
    return rendered_path

if __name__ == "__main__":
    run_remixer()
