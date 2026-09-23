import os

index_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\index.html"
style_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\style.css"
app_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\app.js"

# 1. Update style.css with Sitter & Live GPS & Shortform styles
with open(style_file, 'r', encoding='utf-8') as f:
    css = f.read()

sitter_css = """
/* Sitter & Dual Mode Badges */
.mode-switch-active {
  background-color: #3b82f6 !important;
  color: #ffffff !important;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

/* GPS Live Tracking Pulse */
.gps-pulse-marker {
  width: 14px;
  height: 14px;
  background: #3b82f6;
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7);
  animation: gpsPulse 1.8s infinite;
}
@keyframes gpsPulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
  70% { transform: scale(1.2); box-shadow: 0 0 0 12px rgba(59, 130, 246, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}

/* Shortform Story Ring */
.story-ring {
  background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
  padding: 2.5px;
  border-radius: 50%;
}
"""

if '/* Sitter & Dual Mode Badges' not in css:
    css = css + "\n" + sitter_css
    with open(style_file, 'w', encoding='utf-8') as f:
        f.write(css)

print("style.css updated with Sitter & GPS & Story styles.")
