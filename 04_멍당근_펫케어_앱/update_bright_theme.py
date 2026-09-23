import os

index_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\index.html"
style_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\style.css"

# 1. Update style.css with bright pastel Wayo-inspired theme
new_css = """/* PetLog AI - Bright & Premium Wayo-inspired Theme */
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800;900&display=swap');

:root {
  --primary-blue: #3b82f6;
  --primary-indigo: #4f46e5;
  --primary-peach: #ff7e67;
  --primary-amber: #f59e0b;
  --primary-emerald: #10b981;
  --bg-main: #f8fafc;
  --card-bg: #ffffff;
  --safe-area-top: env(safe-area-inset-top, 0px);
  --safe-area-bottom: env(safe-area-inset-bottom, 16px);
}

body {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
  -webkit-tap-highlight-color: transparent;
  background-color: #f1f5f9;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(203, 213, 225, 0.6);
  border-radius: 4px;
}

/* Bright Card Shadows & Hover Effects */
.pet-card {
  background: #ffffff;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 20px -2px rgba(148, 163, 184, 0.12);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.pet-card:active {
  transform: scale(0.985);
}

/* Interactive Pill Badges */
.badge-best {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
}

.badge-hot {
  background: linear-gradient(135deg, #ff7e67, #ea580c);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(234, 88, 12, 0.25);
}

.badge-free {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25);
}

/* Checkbox & Symptom Buttons (Bright Mode) */
.check-btn {
  background-color: #f8fafc;
  color: #475569;
  border: 1px solid #e2e8f0;
  transition: all 0.15s ease;
}
.check-btn.active {
  background-color: #3b82f6 !important;
  color: #ffffff !important;
  border-color: #3b82f6 !important;
  font-weight: 700;
  box-shadow: 0 3px 10px rgba(59, 130, 246, 0.3);
}

.symptom-btn {
  background-color: #f8fafc;
  color: #475569;
  border: 1px solid #e2e8f0;
  transition: all 0.15s ease;
}
.symptom-btn.active {
  background-color: #ef4444 !important;
  color: #ffffff !important;
  border-color: #ef4444 !important;
  font-weight: 700;
  box-shadow: 0 3px 10px rgba(239, 68, 68, 0.3);
}

/* Animations */
@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
.animate-slide-up {
  animation: slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes gentleBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
.animate-gentle {
  animation: gentleBounce 2.5s ease-in-out infinite;
}

/* Leaflet Map Tuning */
.leaflet-container {
  font-family: 'Pretendard', sans-serif !important;
}
.custom-user-marker, .custom-place-marker {
  border: none !important;
  background: transparent !important;
}

/* ================= Mobile Safe Area Inset Support (Android 3-Button & iOS) ================= */
#app-container {
  padding-bottom: calc(5rem + env(safe-area-inset-bottom, 22px)) !important;
}

nav.fixed.bottom-0 {
  padding-bottom: calc(0.6rem + env(safe-area-inset-bottom, 18px)) !important;
  padding-left: max(0.5rem, env(safe-area-inset-left, 0px)) !important;
  padding-right: max(0.5rem, env(safe-area-inset-right, 0px)) !important;
}

#modal-pet-map > div,
#modal-compatibility > div,
#modal-auth > div,
#modal-trial-limit > div,
#modal-pro-service > div,
#modal-hospital-share > div {
  margin-bottom: calc(env(safe-area-inset-bottom, 16px) + 0.5rem);
}
"""

with open(style_file, 'w', encoding='utf-8') as f:
    f.write(new_css)

print("style.css updated with bright Wayo-style theme.")
