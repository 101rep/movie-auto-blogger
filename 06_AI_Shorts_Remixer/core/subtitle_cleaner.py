import cv2
import numpy as np

class SubtitleCleaner:
    def __init__(self, mode="smart_blur"):
        """
        mode: 
          - 'smart_blur': 자막/글씨 예상 영역에 자연스러운 미세 블러 및 그라디언트 딤 적용
          - 'inpaint': 텍스트 마스크 감지 후 AI/OpenCV 인페인팅으로 배경 복원
          - 'crop_focus': 상하단 자막을 잘라내고 9:16 중앙 피사체에 포커스
        """
        self.mode = mode
        self._reader = None

    @property
    def reader(self):
        if self._reader is None:
            try:
                import easyocr
                self._reader = easyocr.Reader(['ch_sim', 'en', 'ko'], gpu=False)
            except Exception as e:
                print(f"[Cleaner] EasyOCR 로드 실패 (블러 모드로 대체): {e}")
        return self._reader

    def clean_frame(self, frame: np.ndarray) -> np.ndarray:
        """한 프레임에서 중국어 글씨/자막을 제거 또는 부드럽게 마스킹합니다."""
        h, w = frame.shape[:2]
        result = frame.copy()

        if self.mode == "smart_blur":
            # 1. 하단 자막 영역 (전체 높이의 75% ~ 92% 구간)
            sub_y1 = int(h * 0.72)
            sub_y2 = int(h * 0.94)
            sub_roi = result[sub_y1:sub_y2, :]
            
            # 가우시안 블러 처리
            blurred = cv2.GaussianBlur(sub_roi, (31, 31), 0)
            # 알파 블렌딩으로 경계면을 자연스럽게 융합
            alpha = 0.85
            result[sub_y1:sub_y2, :] = cv2.addWeighted(blurred, alpha, sub_roi, 1 - alpha, 0)
            
            # 2. 상단 워터마크/제목 영역 (0% ~ 15% 구간)
            top_y2 = int(h * 0.14)
            top_roi = result[0:top_y2, :]
            blurred_top = cv2.GaussianBlur(top_roi, (25, 25), 0)
            result[0:top_y2, :] = cv2.addWeighted(blurred_top, 0.75, top_roi, 0.25, 0)

        elif self.mode == "inpaint":
            # 텍스트 마스크 생성 (밝은 색 텍스트 + 엣지 검출)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 하단 영역 위주로 마스크 탐지
            mask = np.zeros((h, w), dtype=np.uint8)
            sub_y1 = int(h * 0.70)
            sub_roi_gray = gray[sub_y1:, :]
            
            # 밝은 글씨 마스킹
            _, thresh = cv2.threshold(sub_roi_gray, 200, 255, cv2.THRESH_BINARY)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            dilated = cv2.dilate(thresh, kernel, iterations=2)
            mask[sub_y1:, :] = dilated
            
            # Inpainting 수행
            result = cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)

        return result

    def process_video_clip_frame(self, get_frame, t):
        """MoviePy transform용 프레임 콜백 함수"""
        frame = get_frame(t) # RGB format
        # RGB -> BGR
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cleaned_bgr = self.clean_frame(bgr)
        # BGR -> RGB
        return cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB)
