import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from dotenv import load_dotenv

load_dotenv()

class ShortsRemixerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 AI 쇼츠 리믹스 스튜디오 (Kling AI 비디오 생성 + ElevenLabs 탑재)")
        self.root.geometry("820x780")
        self.root.minsize(760, 680)
        self.root.configure(bg="#1e1e2e")

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e2e")
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("맑은 고딕", 10))
        style.configure("Header.TLabel", background="#1e1e2e", foreground="#89b4fa", font=("맑은 고딕", 15, "bold"))

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 타이틀
        header = ttk.Label(main_frame, text="⚡ AI 비디오 분석 & 15초 쇼츠 리믹스 스튜디오", style="Header.TLabel")
        header.pack(pady=(0, 10))

        # 1. Kling AI 자동 비디오 생성 프롬프트 박스 (옵션)
        kling_frame = ttk.LabelFrame(main_frame, text=" 🤖 Kling AI 자동 영상 생성 (선택 사항) ", padding=10)
        kling_frame.pack(fill=tk.X, pady=4)

        kling_sub = ttk.Frame(kling_frame)
        kling_sub.pack(fill=tk.X)
        ttk.Label(kling_sub, text="영상 주제/프롬프트:").pack(side=tk.LEFT)
        self.kling_prompt_var = tk.StringVar(value="신비로운 사이버펑크 네온 도시를 질주하는 미래형 스포츠카, 초고화질, 영화같은 조명")
        ttk.Entry(kling_sub, textvariable=self.kling_prompt_var, font=("맑은 고딕", 9)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.btn_kling = ttk.Button(kling_sub, text="✨ Kling AI 영상 생성", command=self.start_kling_generation)
        self.btn_kling.pack(side=tk.RIGHT)

        # 2. 입력 폴더 설정
        folder_frame = ttk.LabelFrame(main_frame, text=" 📂 입력 영상 폴더 ", padding=10)
        folder_frame.pack(fill=tk.X, pady=4)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_input = os.path.abspath(os.path.join(base_dir, "..", "분석실"))
        if not os.path.exists(default_input):
            default_input = os.path.join(base_dir, "input_videos")

        self.input_dir_var = tk.StringVar(value=default_input)
        ttk.Entry(folder_frame, textvariable=self.input_dir_var, font=("맑은 고딕", 9)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(folder_frame, text="폴더 선택", command=self.browse_folder).pack(side=tk.RIGHT)

        # 3. 음성 및 사운드 FX 엔진 설정
        sound_frame = ttk.LabelFrame(main_frame, text=" 🎙️ 사운드 & 음성 엔진 ", padding=10)
        sound_frame.pack(fill=tk.X, pady=4)

        ttk.Label(sound_frame, text="TTS 음성 모드:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.tts_mode_var = tk.StringVar(value="자동 하이브리드 (일레븐랩스 우선 + Edge-TTS 백업)")
        tts_combo = ttk.Combobox(sound_frame, textvariable=self.tts_mode_var, values=[
            "자동 하이브리드 (일레븐랩스 우선 + Edge-TTS 백업)",
            "ElevenLabs 전용 (감정표현 극대화)",
            "Microsoft Edge-TTS 전용 (100% 완전 무료/무제한)"
        ], state="readonly", width=42)
        tts_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Label(sound_frame, text="배경음(BGM) & SFX:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.sfx_var = tk.StringVar(value="자동 BGM 선곡 + 컷 전환 효과음 (추천)")
        sfx_combo = ttk.Combobox(sound_frame, textvariable=self.sfx_var, values=[
            "자동 BGM 선곡 + 컷 전환 효과음 (추천)",
            "나레이션 음성만 사용"
        ], state="readonly", width=42)
        sfx_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)

        # 4. 비디오 편집 설정
        opt_frame = ttk.LabelFrame(main_frame, text=" 🎬 비디오 & 자막 설정 ", padding=10)
        opt_frame.pack(fill=tk.X, pady=4)

        ttk.Label(opt_frame, text="목표 재생시간:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.duration_var = tk.StringVar(value="15초 (쇼츠 황금비율)")
        dur_combo = ttk.Combobox(opt_frame, textvariable=self.duration_var, values=["15초 (쇼츠 황금비율)", "30초", "60초"], state="readonly", width=25)
        dur_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Label(opt_frame, text="중국어 글씨 제거:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.clean_mode_var = tk.StringVar(value="스마트 마스킹 & 블러 (추천)")
        clean_combo = ttk.Combobox(opt_frame, textvariable=self.clean_mode_var, values=["스마트 마스킹 & 블러 (추천)", "인페인팅 복원", "중앙 스마트 크롭"], state="readonly", width=25)
        clean_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)

        # 5. 실행 버튼
        self.btn_run = tk.Button(
            main_frame, 
            text="🚀 15초 쇼츠 전자동 생성 시작", 
            bg="#a6e3a1", 
            fg="#11111b", 
            font=("맑은 고딕", 12, "bold"), 
            relief=tk.FLAT, 
            padx=20, 
            pady=8,
            cursor="hand2",
            command=self.start_processing
        )
        self.btn_run.pack(fill=tk.X, pady=8)

        # 6. 실시간 로그 창
        log_frame = ttk.LabelFrame(main_frame, text=" 📜 실시간 제작 진행 로그 ", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        self.log_text = tk.Text(log_frame, bg="#11111b", fg="#a6adc8", font=("Consolas", 9), wrap=tk.WORD, relief=tk.FLAT)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 7. 하단 액션 버튼
        btn_box = ttk.Frame(main_frame)
        btn_box.pack(fill=tk.X, pady=(4, 0))
        self.btn_open_folder = ttk.Button(btn_box, text="📂 '분석실완료' 폴더 열기", command=self.open_output_folder)
        self.btn_open_folder.pack(side=tk.RIGHT)

        self.log("💡 [준비 완료] Kling AI & ElevenLabs & Edge-TTS 및 자동 BGM 파이프라인이 모두 활성화되었습니다.\n")

    def log(self, text: str):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def browse_folder(self):
        selected = filedialog.askdirectory(initialdir=self.input_dir_var.get())
        if selected:
            self.input_dir_var.set(selected)

    def open_output_folder(self):
        input_dir = self.input_dir_var.get()
        out_dir = os.path.join(input_dir, "분석실완료")
        os.makedirs(out_dir, exist_ok=True)
        os.startfile(out_dir)

    def start_kling_generation(self):
        self.btn_kling.config(state=tk.DISABLED)
        threading.Thread(target=self._kling_worker, daemon=True).start()

    def _kling_worker(self):
        try:
            from core.kling_client import KlingAIClient
            client = KlingAIClient()
            prompt = self.kling_prompt_var.get()
            self.log(f"🎬 [Kling AI] 비디오 생성 시작: '{prompt}'")
            res = client.generate_video(prompt=prompt, aspect_ratio="9:16", duration="5")
            if res.get("success"):
                task_id = res["task_id"]
                self.log(f"⏳ [Kling AI] 작업 등록 완료 (ID: {task_id}). 렌더링 대기 중...")
                out_file = os.path.join(self.input_dir_var.get(), f"kling_{task_id[:8]}.mp4")
                downloaded = client.wait_and_download_video(task_id, out_file)
                if downloaded:
                    self.log(f"🎉 [Kling AI] 비디오 저장 성공: {downloaded}")
                    messagebox.showinfo("Kling AI 완료", f"새로운 AI 비디오가 생성되어 분석실 폴더에 저장되었습니다!\n\n{downloaded}")
            else:
                self.log(f"❌ [Kling AI] 요청 실패: {res.get('error')}")
                messagebox.showerror("Kling AI 오류", str(res.get('error')))
        except Exception as e:
            self.log(f"❌ [Kling AI] 예외: {e}")
            messagebox.showerror("오류", str(e))
        finally:
            self.btn_kling.config(state=tk.NORMAL)

    def start_processing(self):
        self.btn_run.config(state=tk.DISABLED, bg="#6c7086", text="⏳ 쇼츠 제작 진행 중...")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            from main import run_remixer
            input_dir = self.input_dir_var.get()
            self.log("🚀 AI 쇼츠 제작 파이프라인 가동...")
            res = run_remixer(input_dir=input_dir)
            if res:
                self.log(f"\n🎉 제작 완료! 파일: {res}")
                messagebox.showinfo("제작 완료", f"15초 쇼츠가 성공적으로 완성되었습니다!\n\n저장 위치:\n{res}")
            else:
                self.log("\n❌ 제작 실패: 입력 영상을 확인해주세요.")
        except Exception as e:
            self.log(f"\n❌ 오류 발생: {e}")
            messagebox.showerror("오류 발생", str(e))
        finally:
            self.btn_run.config(state=tk.NORMAL, bg="#a6e3a1", text="🚀 15초 쇼츠 전자동 생성 시작")

if __name__ == "__main__":
    root = tk.Tk()
    app = ShortsRemixerGUI(root)
    root.mainloop()
