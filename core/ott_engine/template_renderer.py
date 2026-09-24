# -*- coding: utf-8 -*-
"""
Netflix Dark Magazine E-E-A-T Template Renderer for EnterPick24.
Replicates Trendspot24's luxury dark aesthetic, Pretendard typography,
glassmorphic stat cards, Fanart transparent logo hero header,
and commercial affiliate monetization blocks.
"""

from typing import Dict, Any, List, Optional
import html
import json
from core.ott_engine.config import STREAMING_PLATFORMS, COMMERCIAL_CONFIG


class DarkMagazineRenderer:
    """Renders high-conversion, luxury dark-themed OTT magazine articles."""

    @staticmethod
    def render_article(
        show_data: Dict[str, Any],
        visual_assets: Dict[str, Optional[str]],
        article_content: Dict[str, Any],
        post_title: str
    ) -> str:
        """
        Renders full HTML magazine article conforming to Trendspot24 E-E-A-T standards.
        """
        platform_name = show_data.get("platform", "Global OTT")
        platform_info = STREAMING_PLATFORMS.get(platform_name, {"color": "#E50914", "badge": platform_name.upper(), "tag": "OTT"})
        platform_color = platform_info["color"]
        platform_badge = platform_info["badge"]

        # Visual assets fallback
        backdrop_url = visual_assets.get("backdrop") or show_data.get("image_original") or "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?q=80&w=1920"
        logo_url = visual_assets.get("hd_logo")
        clearart_url = visual_assets.get("clearart")

        # Ratings & schedule
        rating = show_data.get("rating", 8.5)
        next_ep = show_data.get("next_episode")
        next_airdate = f"{next_ep['airdate']} ({next_ep['airtime']})" if next_ep else "전편 스트리밍 중 (완결/시즌오프)"
        total_eps = show_data.get("total_episodes") or "미정"
        runtime = f"{show_data.get('runtime', 60)}분"
        genres = " · ".join(show_data.get("genres", ["드라마", "미스터리"]))

        # FAQs for Schema.org
        faqs = article_content.get("faqs", [])

        # Build HTML
        html_out = f"""<!-- EnterPick24 Premium OTT Dark Magazine Article (Trendspot24 E-E-A-T Engine) -->
<meta name="google" content="notranslate">
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">

<div class="mab-article-container notranslate" translate="no" lang="ko" style="font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Noto Sans KR', 'Segoe UI', sans-serif; color: #f8fafc; background: #0b0f19; line-height: 1.95; max-width: 860px; margin: 0 auto; padding: 24px; border-radius: 18px; border: 1px solid #1e293b; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">

  <!-- 1. HERO HEADER WITH FANART 4K BACKDROP & FLOATING LOGO -->
  <div style="position: relative; border-radius: 14px; overflow: hidden; background: linear-gradient(180deg, rgba(11,15,25,0.15) 0%, rgba(11,15,25,0.85) 65%, #0b0f19 100%), url('{backdrop_url}') center/cover no-repeat; padding: 70px 28px 28px 28px; min-height: 340px; display: flex; flex-direction: column; justify-content: flex-end; border: 1px solid rgba(255,255,255,0.08);">
    
    <!-- Status Badges -->
    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; align-items: center;">
      <span style="background: {platform_color}; color: #ffffff; font-size: 11px; font-weight: 800; padding: 5px 12px; border-radius: 20px; letter-spacing: 0.5px; box-shadow: 0 2px 10px rgba(0,0,0,0.4);">{platform_badge}</span>
      <span style="background: rgba(59, 130, 246, 0.9); color: #ffffff; font-size: 11px; font-weight: 800; padding: 5px 12px; border-radius: 20px; letter-spacing: 0.5px; backdrop-filter: blur(4px);">⏰ D-DAY 실시간 카운트다운</span>
      <span style="background: rgba(16, 185, 129, 0.9); color: #ffffff; font-size: 11px; font-weight: 800; padding: 5px 12px; border-radius: 20px; letter-spacing: 0.5px; backdrop-filter: blur(4px);">4K ULTRA HD · DOLBY ATMOS</span>
    </div>

    <!-- Fanart HD Transparent Logo or Fallback Title -->
"""
        if logo_url:
            html_out += f"""    <div style="margin-bottom: 16px;">
      <img src="{logo_url}" alt="{show_data.get('name')}" style="max-width: 340px; max-height: 110px; object-fit: contain; filter: drop-shadow(0 6px 18px rgba(0,0,0,0.9));" />
    </div>
"""
        html_out += f"""    <h1 style="font-size: 26px; font-weight: 800; line-height: 1.4; margin: 0 0 10px 0; color: #ffffff; text-shadow: 0 2px 8px rgba(0,0,0,0.9);">{post_title}</h1>
    <p style="font-size: 14px; color: #cbd5e1; margin: 0; text-shadow: 0 1px 4px rgba(0,0,0,0.8);">{article_content.get('hook_lead', '전 세계 시청자를 사로잡은 화제작, 지금 바로 확인해야 할 관전 포인트와 방영 정보를 완벽 정리합니다.')}</p>
  </div>

  <!-- 2. TVMAZE LIVE METADATA SPEC SHEET (GLASSMORPHISM) -->
  <div style="margin-top: 24px; background: rgba(30, 41, 59, 0.65); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 22px; display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);">
    <div style="text-align: center; border-right: 1px solid rgba(255,255,255,0.05); padding-right: 8px;">
      <span style="font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">스트리밍 플랫폼</span>
      <div style="font-size: 15px; font-weight: 800; color: #38bdf8; margin-top: 4px;">{platform_name}</div>
    </div>
    <div style="text-align: center; border-right: 1px solid rgba(255,255,255,0.05); padding-right: 8px;">
      <span style="font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">글로벌 평점</span>
      <div style="font-size: 15px; font-weight: 800; color: #fbbf24; margin-top: 4px;">★ {rating} / 10</div>
    </div>
    <div style="text-align: center; border-right: 1px solid rgba(255,255,255,0.05); padding-right: 8px;">
      <span style="font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">회차 정보</span>
      <div style="font-size: 15px; font-weight: 800; color: #f43f5e; margin-top: 4px;">총 {total_eps}부작</div>
    </div>
    <div style="text-align: center;">
      <span style="font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">다음 방영일정</span>
      <div style="font-size: 13px; font-weight: 700; color: #4ade80; margin-top: 4px;">{next_airdate}</div>
    </div>
  </div>

  <!-- 3. TITLE MEANING & SYMBOLISM -->
  <div style="margin-top: 36px; padding: 22px; background: rgba(15, 23, 42, 0.6); border-left: 4px solid #38bdf8; border-radius: 8px 12px 12px 8px;">
    <h2 style="font-size: 19px; font-weight: 700; color: #38bdf8; margin: 0 0 12px 0; display: flex; align-items: center; gap: 8px;">
      💡 제목의 의미와 숨겨진 상징성
    </h2>
    <div style="font-size: 15px; color: #e2e8f0; line-height: 1.85;">
      {article_content.get('title_symbolism', '이 작품의 타이틀은 단순한 명칭을 넘어 극 전체를 관통하는 핵심 복선과 인물의 내면적 딜레마를 상징합니다.')}
    </div>
  </div>

  <!-- 4. NON-SPOILER SYNOPSIS & WORLDBUILDING -->
  <div style="margin-top: 36px;">
    <h2 style="font-size: 21px; font-weight: 800; color: #ffffff; border-bottom: 2px solid #334155; padding-bottom: 10px; margin-bottom: 18px;">
      🎬 스포일러 없는 핵심 줄거리 & 세계관
    </h2>
    <div style="font-size: 15px; color: #e2e8f0; line-height: 1.9;">
      {article_content.get('synopsis_section', show_data.get('summary', ''))}
    </div>
  </div>
"""

        # 5. CAST & CHARACTERS (WITH FANART CLEARART IF AVAILABLE)
        cast_list = show_data.get("cast", [])
        if cast_list:
            html_out += f"""
  <!-- 5. CAST & CHARACTERS -->
  <div style="margin-top: 38px;">
    <h2 style="font-size: 21px; font-weight: 800; color: #ffffff; border-bottom: 2px solid #334155; padding-bottom: 10px; margin-bottom: 18px;">
      🎭 주요 인물 갈등 구도와 심리전 분석
    </h2>
"""
            if clearart_url:
                html_out += f"""    <div style="text-align: center; margin-bottom: 20px;">
      <img src="{clearart_url}" alt="Character Visual" style="max-width: 480px; width: 100%; height: auto; filter: drop-shadow(0 8px 24px rgba(0,0,0,0.6));" />
    </div>
"""
            html_out += """    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; margin-top: 16px;">
"""
            for actor in cast_list[:6]:
                actor_img = actor.get("person_image") or "https://via.placeholder.com/150x200/1e293b/94a3b8?text=Actor"
                html_out += f"""      <div style="background: #1e293b; border-radius: 10px; overflow: hidden; padding: 12px; border: 1px solid rgba(255,255,255,0.05); text-align: center;">
        <img src="{actor_img}" alt="{actor.get('person_name')}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin: 0 auto 10px auto; border: 2px solid #38bdf8;" />
        <div style="font-size: 13px; font-weight: 700; color: #ffffff;">{actor.get('person_name')}</div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 2px;">{actor.get('character_name')} 역</div>
      </div>
"""
            html_out += """    </div>
  </div>
"""

        # 6. BINGE-WATCH CHEAT SHEET (EPISODE GUIDE)
        episodes = show_data.get("episodes", [])
        if episodes:
            html_out += f"""
  <!-- 6. BINGE-WATCH CHEAT SHEET -->
  <div style="margin-top: 40px; background: rgba(15, 23, 42, 0.7); border: 1px solid #334155; border-radius: 14px; padding: 24px;">
    <h2 style="font-size: 20px; font-weight: 800; color: #38bdf8; margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px;">
      ⚡ 주말 몰아보기(Binge-Watch) 필수 회차 치트시트
    </h2>
    <p style="font-size: 14px; color: #94a3b8; margin-bottom: 18px;">바쁜 일상 속에서 가장 효율적으로 세계관과 결말 복선을 파악할 수 있는 핵심 회차별 가이드입니다.</p>
    <div style="display: flex; flex-direction: column; gap: 10px;">
"""
            for ep in episodes[:5]:
                ep_num = f"S{ep.get('season', 1):02d}E{ep.get('number', 1):02d}"
                ep_name = ep.get('name') or "에피소드"
                ep_rating = f"★ {ep.get('rating')}" if ep.get('rating') else "추천 회차"
                html_out += f"""      <div style="background: #1e293b; border-radius: 8px; padding: 14px; display: flex; justify-content: space-between; align-items: center; border-left: 3px solid #3b82f6;">
        <div>
          <span style="font-size: 11px; font-weight: 800; color: #38bdf8; background: rgba(56, 189, 248, 0.15); padding: 3px 8px; border-radius: 4px;">{ep_num}</span>
          <span style="font-size: 14px; font-weight: 600; color: #f1f5f9; margin-left: 8px;">{ep_name}</span>
        </div>
        <span style="font-size: 12px; font-weight: 700; color: #fbbf24;">{ep_rating}</span>
      </div>
"""
            html_out += """    </div>
  </div>
"""

        # 7. COMMERCIAL MONETIZATION & AFFILIATE BLOCKS
        vpn_cfg = COMMERCIAL_CONFIG["vpn"]
        ott_cfg = COMMERCIAL_CONFIG["ott_sub"]
        cinema_cfg = COMMERCIAL_CONFIG["cinema"]

        html_out += f"""
  <!-- 7. COMMERCIAL AFFILIATE & MONETIZATION CONTAINER -->
  <div style="margin-top: 42px; display: flex; flex-direction: column; gap: 18px;">
    
    <!-- OTT Official Platform Link -->
    <div style="background: linear-gradient(135deg, rgba(229, 9, 20, 0.15) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid rgba(229, 9, 20, 0.4); border-radius: 12px; padding: 22px;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
          <h3 style="font-size: 17px; font-weight: 800; color: #ffffff; margin: 0 0 6px 0;">{ott_cfg['title']}</h3>
          <p style="font-size: 13px; color: #cbd5e1; margin: 0;">{ott_cfg['desc']}</p>
        </div>
        <a href="{ott_cfg['url']}" target="_blank" rel="nofollow noopener" style="display: inline-block; background: {platform_color}; color: #ffffff; font-size: 13px; font-weight: 800; padding: 10px 18px; border-radius: 8px; text-decoration: none; box-shadow: 0 4px 14px rgba(229, 9, 20, 0.4);">
          {ott_cfg['button_text']} →
        </a>
      </div>
    </div>

    <!-- High-Commission VPN Guide (For Overseas Exclusives) -->
    <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid rgba(59, 130, 246, 0.4); border-radius: 12px; padding: 22px;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
          <h3 style="font-size: 17px; font-weight: 800; color: #ffffff; margin: 0 0 6px 0;">{vpn_cfg['title']}</h3>
          <p style="font-size: 13px; color: #cbd5e1; margin: 0;">{vpn_cfg['desc']}</p>
        </div>
        <a href="{vpn_cfg['url']}" target="_blank" rel="nofollow noopener" style="display: inline-block; background: #2563eb; color: #ffffff; font-size: 13px; font-weight: 800; padding: 10px 18px; border-radius: 8px; text-decoration: none; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);">
          {vpn_cfg['button_text']} →
        </a>
      </div>
    </div>

    <!-- Home Cinema Gear Recommendation (Coupang Partners) -->
    <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; border-radius: 12px; padding: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
          <h3 style="font-size: 16px; font-weight: 700; color: #f1f5f9; margin: 0 0 4px 0;">{cinema_cfg['title']}</h3>
          <p style="font-size: 13px; color: #94a3b8; margin: 0;">{cinema_cfg['desc']}</p>
        </div>
        <a href="{cinema_cfg['url']}" target="_blank" rel="nofollow noopener" style="display: inline-block; background: #334155; color: #38bdf8; font-size: 12px; font-weight: 700; padding: 8px 16px; border-radius: 6px; text-decoration: none; border: 1px solid #475569;">
          {cinema_cfg['button_text']}
        </a>
      </div>
    </div>

  </div>

  <!-- 8. FREQUENTLY ASKED QUESTIONS (FAQ ACCORDION) -->
  <div style="margin-top: 42px;">
    <h2 style="font-size: 21px; font-weight: 800; color: #ffffff; border-bottom: 2px solid #334155; padding-bottom: 10px; margin-bottom: 18px;">
      ❓ 자주 묻는 질문 (FAQ)
    </h2>
    <div style="display: flex; flex-direction: column; gap: 12px;">
"""
        for faq in faqs:
            q = faq.get("q", "")
            a = faq.get("a", "")
            html_out += f"""      <details style="background: #1e293b; border-radius: 10px; padding: 14px 18px; border: 1px solid rgba(255,255,255,0.06); cursor: pointer;">
        <summary style="font-size: 15px; font-weight: 700; color: #38bdf8; outline: none;">{q}</summary>
        <div style="margin-top: 10px; font-size: 14px; color: #cbd5e1; line-height: 1.8;">{a}</div>
      </details>
"""
        html_out += f"""    </div>
  </div>

  <!-- 9. SUMMARY & FINAL VERDICT -->
  <div style="margin-top: 40px; padding: 24px; background: rgba(30, 41, 59, 0.7); border-radius: 14px; border-top: 3px solid #38bdf8; text-align: center;">
    <div style="font-size: 13px; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">ENTERPICK24 OTT VERDICT</div>
    <div style="font-size: 20px; font-weight: 800; color: #ffffff; margin-bottom: 10px;">총평: 시간을 아깝지 않게 만들어 줄 올해의 필람작</div>
    <p style="font-size: 14px; color: #cbd5e1; max-width: 680px; margin: 0 auto; line-height: 1.8;">{article_content.get('verdict', '탄탄한 각본과 배우진의 호연, 감각적인 연출이 결합되어 OTT 시청자들에게 압도적인 몰입감을 선사합니다. 정주행을 강력히 추천합니다.')}</p>
  </div>

</div>
"""

        # Append Schema.org JSON-LD
        schema_json = {
            "@context": "https://schema.org",
            "@type": "TVSeries",
            "name": show_data.get("name"),
            "genre": show_data.get("genres"),
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": str(rating),
                "bestRating": "10",
                "ratingCount": "1000"
            }
        }
        html_out += f"\n<script type=\"application/ld+json\">\n{json.dumps(schema_json, ensure_ascii=False, indent=2)}\n</script>\n"

        return html_out
