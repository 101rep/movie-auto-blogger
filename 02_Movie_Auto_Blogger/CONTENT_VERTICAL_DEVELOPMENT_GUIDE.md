# New Content Vertical Development Guide
## Universal Content Quality & Experience Engine v1.0

---

## Overview

This project uses a Universal Content Quality Engine that supports multiple blog verticals
(travel, movie, food, tech, etc.) sharing the same quality standards with domain-specific rules.

There are two content tracks:
- **Auto-Pilot**: Fully automated SEO-driven generation from candidate pool
- **Experience Studio**: Interview -> Context Notebook -> Outline -> Draft

---

## Architecture

```
app/
+-- core/
|   +-- quality/
|   |   +-- skill.py         # ContentQualitySkill
|   |   +-- profile.py       # QualityProfile + Registry
|   |   +-- provenance.py    # SourceType, ProvenanceRecord
|   +-- prompts/
|   |   +-- registry.py      # PromptRegistry v3.0
|   +-- registry.py          # PlatformRegistry + register_new_vertical()
+-- ai/
|   +-- experience_schemas.py  # Pydantic schemas
+-- services/
|   +-- experience_service.py          # Full interview workflow
|   +-- experience_grounding_service.py # Hallucination guard
+-- modules/
    +-- travel/module.py    # Travel vertical
    +-- movie/module.py     # Movie vertical
```

---

## 1. Quick Start: Register a New Vertical

```python
from app.core.registry import register_new_vertical

result = register_new_vertical(
    vertical_name="FOOD_BLOG",
    name_ko="restaurant review blog",
    description="Restaurant and cafe reviews based on personal visits",
    supported_features=["rating_table", "price_range", "faq"],
    prompts={
        "review": "You are an honest restaurant reviewer...",
    }
)
# Returns: {"vertical": "FOOD_BLOG", "quality_profile": "food_blog", ...}
```

This single call automatically:
1. Creates a QualityProfile named food_blog with E-E-A-T defaults
2. Registers prompts under verticals/food_blog/<key>
3. Returns registration summary

---

## 2. Custom QualityProfile

```python
from app.core.quality.profile import QualityProfile, QualityProfileRegistry

food_profile = QualityProfile(
    name="food_blog",
    min_body_length=800,
    target_word_count=1200,
    faq_required=True,
    schema_types=["LocalBusiness", "Review", "FAQPage"],
    experience_grounding=True,
    cliche_control=True,
    banned_cliches=["must visit", "highly recommended"],
    internal_links_min=2,
    external_links_min=1,
)
QualityProfileRegistry.register(food_profile)
```

---

## 3. ExperienceService Full Workflow

```python
service = ExperienceService()

# 1. Start interview
state, first_q = service.start_interview(topic="Tokyo cafe tour")

# 2. Loop: process answers
state, next_q, done = service.process_answer(state.session_id, user_answer)

# 3. Generate outline (3 titles, 3-4 H2 sections)
outline = service.generate_outline(state.session_id)

# 4. Generate draft grounded in Context Notebook
draft = service.generate_draft(state.session_id, outline.titles[0])

# 5. Verify grounding
report = ExperienceGroundingService.verify_draft(draft, state.context_notebook)
# report.status in (PASS, REVIEW, FAIL)
# report.grounding_ratio = float 0.0-1.0
# report.ungrounded_claims = list of ungrounded sentences

# 6. Approve and publish
if report.status == "PASS":
    service.approve_and_create_post(state.session_id, db, site_id=1)
```

---

## 4. Built-in Quality Profiles

| Profile | Min Length | Use Case |
|---------|-----------|----------|
| default | 600 | General |
| travel | 800 | Travel guides |
| movie | 500 | Movie reviews |
| experience | 1000 | First-person |
| listicle | 400 | List articles |
| news | 300 | News |
| product_review | 700 | Product reviews |

---

## 5. ContentQualitySkill API

```python
skill = ContentQualitySkill(profile_name="travel")

# Build AI system instructions
instructions = skill.build_quality_system_instructions()

# Inspect generated text - returns dict
report = skill.inspect_text(html_content)
# report["detected_cliches"] - list of matched banned phrases
# report["char_count"] - character count
# report["is_length_ok"] - meets min_body_length
# report["passed"] - True if length OK and no cliches

# Sanitize cliches
clean = skill.sanitize_cliches(raw_text)
```

---

## 6. ExperienceGroundingReport Schema

| Field | Type | Description |
|-------|------|-------------|
| total_claims | int | Total personal experience claims |
| grounded_count | int | Claims matched to Notebook |
| ungrounded_count | int | Unmatched claims |
| grounding_ratio | float | grounded/total (1.0=perfect) |
| status | str | PASS / REVIEW / FAIL |
| claims | list | All detected claims |
| ungrounded_claims | list | Only ungrounded claims |

Status logic:
- PASS: zero ungrounded claims
- REVIEW: <=1 ungrounded when total >= 4
- FAIL: >=2 ungrounded claims

---

## 7. Database Schema

Post table (new nullable columns):
- generator_version VARCHAR
- quality_profile VARCHAR
- experience_grounding_status VARCHAR (PASS/REVIEW/FAIL/NULL)

interview_sessions table (new):
- session_id UUID
- topic, status (IN_PROGRESS/COMPLETED/OUTLINED/DRAFTED/APPROVED)
- turns_json, context_notebook_json, outline_json, draft_json, grounding_report_json

---

## 8. WordPress Publishing Rules

- Schema.org JSON-LD is embedded DIRECTLY in html_content
- Do NOT send custom meta fields (Rank Math/Yoast not installed on either site)
- travelpick24.com = Travel blog
- trendspot24.com = Movie blog

---

## 9. Admin UI

Navigate to /admin/experience for the Experience Studio.

Tabs:
- Experience Studio (취재 스튜디오): Interview workflow
- Auto-Pilot: Existing automated generation (unchanged)

Right panel shows live Context Notebook accumulating episodes, facts, and discoveries.

---

## 10. Test Commands

```powershell
# Run all 11 quality and experience tests
.venv/Scripts/pytest tests/test_content_quality_and_experience.py tests/test_travel_vertical.py -v

# Verify imports
python -c "import app.admin.routes; print('Routes OK')"
python -c "from app.core.registry import register_new_vertical; print('Registry OK')"
```

Expected: 11 passed, 2 warnings

---

Generated by Universal Content Quality & Experience Engine v1.0
trendspot24.com (Movie) | travelpick24.com (Travel)
