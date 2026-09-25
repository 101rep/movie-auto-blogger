# -*- coding: utf-8 -*-
"""
EnterPick24 Dark Editorial Design System & Unified CSS (V4).
Provides design tokens, responsive typography, movie card layout,
and full-page dark styling including WordPress comments area.
"""

ENTERPICK24_DARK_EDITORIAL_CSS = """
<!-- wp:html -->
<style id="enterpick24-v4-dark-editorial-theme">
/* ==========================================================================
   ENTERPICK24 V4 DARK EDITORIAL DESIGN TOKENS
   ========================================================================== */
:root {
  --ep-bg: #070a12;
  --ep-surface: #0b0f19;
  --ep-surface-card: #0f172a;
  --ep-surface-secondary: #131b2e;
  --ep-text: #f8fafc;
  --ep-text-muted: #94a3b8;
  --ep-border: #1e293b;
  --ep-border-subtle: #334155;
  --ep-accent: #2563eb;
  --ep-accent-hover: #1d4ed8;
  --ep-badge-bg: rgba(37, 99, 235, 0.18);
  --ep-badge-text: #60a5fa;
  --ep-input: #070a12;
  --ep-input-border: #334155;
  --ep-focus: #3b82f6;
}

/* Base Container */
.mab-article-container {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  color: var(--ep-text) !important;
  background-color: var(--ep-surface) !important;
  line-height: 1.9 !important;
  max-width: 860px !important;
  margin: 0 auto !important;
  padding: 24px !important;
  border-radius: 20px !important;
  border: 1px solid var(--ep-border) !important;
  box-sizing: border-box !important;
  word-break: keep-all !important;
}

/* Card Hierarchy: Poster -> Badge -> Title -> Meta -> Content */
.ep-card {
  margin-top: 32px !important;
  background: var(--ep-surface-card) !important;
  border: 1px solid var(--ep-border) !important;
  border-radius: 16px !important;
  padding: 24px !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
}

.ep-card-title {
  font-size: 21px !important;
  font-weight: 800 !important;
  color: #ffffff !important;
  margin: 8px 0 16px 0 !important;
  line-height: 1.45 !important;
  text-align: center !important;
}

/* Comparison Table (Mobile Horizontal Scrollable) */
.ep-table-container {
  width: 100% !important;
  overflow-x: auto !important;
  -webkit-overflow-scrolling: touch !important;
  margin: 28px 0 !important;
  border-radius: 12px !important;
  border: 1px solid var(--ep-border) !important;
}

.ep-dark-table {
  width: 100% !important;
  border-collapse: collapse !important;
  text-align: left !important;
  font-size: 14px !important;
  min-width: 580px !important;
  background: var(--ep-surface-card) !important;
}

.ep-dark-table th {
  background: var(--ep-surface-secondary) !important;
  color: #93c5fd !important;
  font-weight: 700 !important;
  padding: 14px 16px !important;
  border-bottom: 1px solid var(--ep-border) !important;
}

.ep-dark-table td {
  padding: 13px 16px !important;
  border-bottom: 1px solid var(--ep-border) !important;
  color: var(--ep-text) !important;
}

/* ==========================================================================
   PART 16~24: WORDPRESS COMMENTS DARK EDITORIAL UI OVERRIDE
   ========================================================================== */
#comments, 
.comments-area,
.ast-separate-container .comment-respond,
#respond {
  background: var(--ep-surface-card) !important;
  border: 1px solid var(--ep-border) !important;
  border-radius: 18px !important;
  padding: 28px !important;
  margin-top: 40px !important;
  color: var(--ep-text) !important;
  box-sizing: border-box !important;
}

#reply-title, 
.comment-reply-title {
  color: #ffffff !important;
  font-size: 20px !important;
  font-weight: 800 !important;
  margin-bottom: 14px !important;
  letter-spacing: -0.02em !important;
}

.comment-notes, 
#email-notes, 
.required-field-message {
  color: var(--ep-text-muted) !important;
  font-size: 13px !important;
  line-height: 1.6 !important;
}

/* Input Fields & Textarea */
.comments-area textarea#comment,
#ast-commentform textarea#comment,
.comments-area input[type="text"],
.comments-area input[type="email"],
.comments-area input[type="url"],
#ast-commentform input[type="text"],
#ast-commentform input[type="email"],
#ast-commentform input[type="url"] {
  background: var(--ep-input) !important;
  color: var(--ep-text) !important;
  border: 1px solid var(--ep-input-border) !important;
  border-radius: 10px !important;
  padding: 14px 16px !important;
  font-size: 14px !important;
  width: 100% !important;
  box-sizing: border-box !important;
  transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

.comments-area textarea#comment:focus,
#ast-commentform textarea#comment:focus,
.comments-area input[type="text"]:focus,
.comments-area input[type="email"]:focus,
.comments-area input[type="url"]:focus {
  border-color: var(--ep-focus) !important;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25) !important;
  outline: none !important;
}

.comments-area textarea#comment {
  min-height: 140px !important;
  resize: vertical !important;
}

/* Submit Button */
.comments-area #submit,
#ast-commentform #submit,
.form-submit input#submit {
  background: var(--ep-accent) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 12px 28px !important;
  font-size: 15px !important;
  font-weight: 700 !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
  display: inline-block !important;
}

.comments-area #submit:hover,
#ast-commentform #submit:hover,
.form-submit input#submit:hover {
  background: var(--ep-accent-hover) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4) !important;
}

/* Cookies Consent */
.comment-form-cookies-consent label {
  color: var(--ep-text-muted) !important;
  font-size: 13px !important;
}

/* Existing Comment Items */
.ast-comment-list, 
.commentlist {
  list-style: none !important;
  padding: 0 !important;
  margin: 28px 0 0 0 !important;
}

.ast-comment-list li.comment, 
.commentlist li.comment {
  background: var(--ep-surface-secondary) !important;
  border: 1px solid var(--ep-border) !important;
  border-radius: 12px !important;
  padding: 18px !important;
  margin-bottom: 16px !important;
  color: var(--ep-text) !important;
}

.ast-comment-list .comment-author .fn, 
.comment-author .fn {
  color: #ffffff !important;
  font-weight: 700 !important;
}

.ast-comment-list .comment-metadata a, 
.comment-metadata a {
  color: var(--ep-text-muted) !important;
  font-size: 12px !important;
  text-decoration: none !important;
}

.ast-comment-list .reply a, 
.comment-reply-link {
  color: #60a5fa !important;
  font-weight: 600 !important;
  font-size: 13px !important;
}

/* Nested replies */
.ast-comment-list .children, 
.children {
  border-left: 2px solid var(--ep-accent) !important;
  margin-left: 18px !important;
  padding-left: 14px !important;
}

/* ==========================================================================
   PART 22 & 35: MOBILE VIEWPORT (320px ~ 430px) OPTIMIZATION
   ========================================================================== */
@media screen and (max-width: 540px) {
  .mab-article-container {
    padding: 16px !important;
    border-radius: 12px !important;
  }
  .ep-card {
    padding: 16px !important;
    border-radius: 12px !important;
  }
  .ep-card-title {
    font-size: 18px !important;
  }
  #comments, 
  .comments-area, 
  #respond {
    padding: 18px !important;
    border-radius: 12px !important;
  }
  .ast-comment-formwrap.ast-row {
    display: flex !important;
    flex-direction: column !important;
    row-gap: 12px !important;
  }
  .ast-comment-formwrap p {
    width: 100% !important;
    float: none !important;
    margin: 0 !important;
  }
  .form-submit input#submit {
    width: 100% !important;
    padding: 14px 20px !important;
  }
  .ep-poster-wrapper {
    max-width: 280px !important;
  }
}
</style>
<!-- /wp:html -->
"""
