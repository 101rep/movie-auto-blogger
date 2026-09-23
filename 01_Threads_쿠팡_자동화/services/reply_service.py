import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import Account, Content, AutoReply
from integrations.threads_api import ThreadsOfficialAPI
from integrations.factory import get_ai_provider
from integrations.providers.real_ai_provider import RealAIProvider

logger = logging.getLogger("ReplyEngine")

class ReplyEngineService:
    """
    Autonomous Threads Comment & Sub-Reply (대댓글) Engine.
    Detects follower comments and responds authentically matching each account persona.
    """
    def __init__(self, db: Session):
        self.db = db

    def generate_reply_text(self, account: Account, post_text: str, author: str, comment_text: str) -> str:
        """
        Generate empathetic, witty, context-aware human-like reply matching account tone.
        Intelligently directs product inquiries to the exact Pick Item Number (e.g. 101번).
        """
        tone = account.tone or "친근하고 진솔한 일상 어조"
        username = account.username
        author_tag = f"@{author}"

        # Determine target product item_code for this post/account
        from database.models import PickItem
        item_code = "101"
        try:
            items = self.db.query(PickItem).filter(PickItem.account_id == account.id).all()
            for it in items:
                if it.title and any(k in post_text for k in it.title.split()[:2]):
                    item_code = it.item_code or str(it.id)
                    break
            else:
                pinned = next((it for it in items if it.is_pinned), None)
                if pinned:
                    item_code = pinned.item_code or str(pinned.id)
                elif items:
                    item_code = items[0].item_code or str(items[0].id)
        except Exception:
            item_code = "101"

        # Check if commenter is asking for product coordinates / purchase link / price
        c_lower = comment_text.lower()
        is_product_inquiry = any(w in c_lower for w in ["어디", "좌표", "정보", "얼마", "링크", "구매", "사요", "어디서", "품번", "사이트", "공유", "추천", "다이소"])

        # 1. Real AI Provider if configured
        ai_provider = get_ai_provider()
        if isinstance(ai_provider, RealAIProvider):
            try:
                system_prompt = (
                    f"당신은 Threads 계정 @{username}의 운영자입니다.\n"
                    f"계정 카테고리: {account.category} / 어조: {tone}\n"
                    f"현재 소개 중인 꿀템 번호: [{item_code}번]\n"
                    "규칙:\n"
                    "1. 상투적인 AI 어투(예: '좋은 질문이네요', '도움이 되었길 바랍니다')를 절대 쓰지 마세요.\n"
                    "2. 친근하고 진솔한 한국어 구어체(해요체, ㅋㅋㅋ, ㅎㅎ, ㅠㅠ 등)로 1~2문장으로 답글을 작성하세요.\n"
                    f"3. 독자가 제품 정보, 구매처, 좌표, 링크, 얼마인지 물어보는 경우: '프로필 링크 [{item_code}번] 검색 시 최저가 바로 확인'할 수 있다고 자연스럽게 안내하세요.\n"
                    "4. 본문에 직접 긴 외부 URL을 적지 말고 '프로필 링크 [N번]'으로만 깔끔하게 유도하세요.\n"
                    f"5. 댓글 작성자({author_tag})의 말에 진심으로 공감하거나 유용한 팁을 덧붙이세요."
                )
                user_prompt = (
                    f"원문 포스팅:\n{post_text[:200]}\n\n"
                    f"댓글 작성자: {author_tag}\n"
                    f"댓글 내용:\n{comment_text}\n\n"
                    "위 댓글에 달아줄 센스 있고 야무진 대댓글을 1~2문장으로 작성해주세요."
                )
                reply = ai_provider.generate_text(system_prompt, user_prompt)
                if reply and len(reply.strip()) > 3:
                    return reply.strip().replace('"', '')
            except Exception as e:
                logger.warning(f"AI reply generation fallback: {e}")

        # 2. Contextual Persona Rule-Based Smart Reply Engine
        if "toontoooon" in username:
            if is_product_inquiry:
                return f"앗 {author_tag}님! 요거 제 프로필 링크 [{item_code}번]에 좌표 남겨뒀어요! 검색창에 {item_code} 치시면 1초 만에 바로 나와요 ㅋㅋㅋ ✨"
            elif any(w in c_lower for w in ["귀엽", "이쁘", "예쁘", "취향"]):
                return f"저도 이거 보고 심장 멎을 뻔했어요 ㅠㅠ 데스크에 두니까 일할 때마다 힐링돼요 ㅎㅎ"
            else:
                return f"맞아요 ㅋㅋㅋ {author_tag}님도 완전 공감하시죠!! 이거 진짜 실물이 200배는 더 귀여워요 ✨"

        elif "kth.101rep" in username:
            if is_product_inquiry:
                return f"{author_tag}님 관심 감사해요! 프로필 링크 [{item_code}번] 검색하시면 상세 스펙이랑 실시간 최저가 할인 좌표 바로 확인하실 수 있습니다."
            elif any(w in c_lower for w in ["방법", "어떻게", "설정", "앱"]):
                return f"{author_tag}님, 요거 무료 앱 쓰시거나 단축어 세팅해두시면 훨씬 편해져요! 꼭 한번 적용해보세요."
            elif any(w in c_lower for w in ["배터리", "맥북", "거치대", "모니터", "발열"]):
                return "실제로 2달 넘게 매일 써보니까 발열이랑 작업 피로도 줄어드는 게 확실히 체감되더라고요 ㅎㅎ"
            else:
                return f"맞습니다 {author_tag}님! 생산성 올리는 덴 이런 사소한 세팅 디테일이 진짜 큰 차이를 만드는 것 같아요."

        elif "yr170425" in username:
            if is_product_inquiry:
                return f"이웃님~ 요거 제 프로필 링크 [{item_code}번]에 깔끔하게 정리해뒀어요! 검색창에 {item_code}번 치시면 바로 찾으실 수 있답니다 ㅎㅎ ☕️"
            elif any(w in c_lower for w in ["정리", "청소", "살림", "주방", "수납"]):
                return "맞아요 이웃님~ 저도 처음엔 반신반의했는데 써보고 살림 스트레스가 확 줄었어요 ㅠㅠ"
            elif any(w in c_lower for w in ["꿀팁", "대박", "저도", "좋네요"]):
                return f"도움이 되셨다니 너무 뿌듯해요 {author_tag}님! 오늘도 기분 좋은 하루 보내세요 ☕️"
            else:
                return f"공감해주셔서 감사해요 {author_tag}님! 우리 살림 동지님들 다들 편해졌으면 좋겠어요 ㅎㅎ"

        elif "ktaehoon80" in username:
            if is_product_inquiry:
                return f"{author_tag}님 생존템 좌표는 제 프로필 링크 [{item_code}번]에 모아뒀어요! 검색창에 {item_code}번 치시면 바로 나옵니다 ㅠㅠ 오늘도 파이팅입니다!"
            elif any(w in c_lower for w in ["퇴근", "출근", "월요", "피곤", "힘들", "야근"]):
                return "동지님 ㅠㅠ 오늘 하루도 진짜 버티느라 고생 많으셨습니다! 저녁에 맛있는 거 꼭 챙겨드세요!"
            elif any(w in c_lower for w in ["영양제", "체력", "잠", "커피", "건강"]):
                return "직장인은 역시 생존템 빨이죠 ㅋㅋㅋ 저도 이거 없으면 오후에 영혼 가출해요 ㅠㅠ"
            else:
                return "아 진짜 너무 공감돼요 ㅋㅋㅋ 직장인 마음은 다 똑같나 봅니다... 오늘도 칼퇴 기원합니다!"

        elif "taechi.tube" in username:
            if is_product_inquiry:
                return f"{author_tag}님, 요거 제 프로필 링크 [{item_code}번] 검색하시면 상세 정보랑 좌표 바로 확인하실 수 있어요 🌿"
            elif any(w in c_lower for w in ["여행", "장소", "감성", "숙소", "휴가"]):
                return f"{author_tag}님, 주말에 가볍게 다녀오기 정말 좋은 스팟이에요! 날씨 좋을 때 꼭 가보셔요 🌿"
            else:
                return f"사진 보니까 또 가고 싶어지네요 ㅎㅎ 공감 남겨주셔서 감사해요 {author_tag}님!"

        elif "lookatmeai" in username:
            if is_product_inquiry:
                return f"{author_tag}님! 요거 제 프로필 링크 [{item_code}번] 검색하시면 바로 최저가 좌표 나와요 ✨ 꼭 득템하세요!"
            elif any(w in c_lower for w in ["피부", "톤", "추천", "화장", "코디", "뷰티"]):
                return f"{author_tag}님 꿀팁 캐치하셨네요! 요즘 날씨에 이 조합이 톤그로 없이 제일 자연스러워요 ✨"
            else:
                return f"센스 있으신 {author_tag}님 바로 알아보시네요 ㅎㅎ 예쁘게 봐주셔서 감사해요!"

        elif "101rep80" in username:
            if is_product_inquiry:
                return f"{author_tag}님 호구 탈출 최저가 좌표는 제 프로필 링크 [{item_code}번] 검색하시면 1초컷입니다 ㅋㅋㅋ"
            elif any(w in c_lower for w in ["가격", "비교", "가성비", "할인"]):
                return f"{author_tag}님, 비싼 브랜드 제품이랑 스펙 다 뜯어봤는데 차이 거의 없더라고요 ㅋㅋㅋ 호구 탈출 성공입니다!"
            else:
                return f"역시 똑순이 분들은 다 통하나 봐요 ㅋㅋㅋ {author_tag}님 돈 아끼는 게 최고입니다!"

        return f"{author_tag}님 공감 댓글 남겨주셔서 너무 감사해요! 오늘도 행복한 하루 보내세요 ㅎㅎ"

    def check_and_reply_for_account(self, account: Account) -> List[Dict[str, Any]]:
        """
        Fetch comments on recent posts for this account and automatically post smart replies.
        """
        if not account.access_token:
            return []

        api = ThreadsOfficialAPI(access_token=account.access_token)
        replied_list = []

        try:
            recent_threads = api.get_user_threads(limit=10)
            if not recent_threads:
                return []

            for th in recent_threads:
                post_id = str(th.get("id", ""))
                post_text = th.get("text", "")
                if not post_id:
                    continue

                replies = api.get_replies(post_id)
                for rep in replies:
                    comment_id = str(rep.get("id", ""))
                    comment_author = str(rep.get("username", ""))
                    comment_text = rep.get("text", "")

                    # Skip our own comments
                    if not comment_author or comment_author == account.username:
                        continue

                    # Skip if already replied in DB
                    existing = self.db.query(AutoReply).filter(AutoReply.comment_id == comment_id).first()
                    if existing:
                        continue

                    # Generate reply text
                    reply_text = self.generate_reply_text(account, post_text, comment_author, comment_text)

                    # Publish reply via Threads Graph API (threaded to the comment)
                    res = api.publish_reply(parent_id=comment_id, text=reply_text)
                    reply_id = res.get("reply_id")

                    # Verify and record to threads_task
                    try:
                        from services.threads_verification import ThreadsVerificationService
                        ThreadsVerificationService.log_and_verify_comment(
                            db=self.db,
                            account_name=account.username,
                            parent_post_id=post_id,
                            comment_body=reply_text,
                            reply_result=res,
                            target_url=f"https://www.threads.net/post/{post_id}"
                        )
                    except Exception as v_err:
                        logger.warning(f"[ThreadsTask] Reply logging notice: {v_err}")

                    # Save record to database
                    record = AutoReply(
                        account_id=account.id,
                        post_id=post_id,
                        comment_id=comment_id,
                        comment_author=comment_author,
                        comment_text=comment_text,
                        reply_id=reply_id,
                        reply_text=reply_text
                    )
                    self.db.add(record)
                    self.db.commit()

                    logger.info(f"[AutoReply] Replied to @{comment_author} on @{account.username}: {reply_text}")
                    replied_list.append({
                        "account": account.username,
                        "author": comment_author,
                        "comment": comment_text,
                        "reply": reply_text
                    })

        except Exception as e:
            logger.error(f"[AutoReply] Error processing replies for @{account.username}: {e}")

        return replied_list

    def process_all_accounts(self) -> List[Dict[str, Any]]:
        """
        Process incoming comments across all active accounts.
        """
        accounts = self.db.query(Account).filter(Account.access_token != None, Account.status == "ACTIVE").all()
        all_replies = []
        for acc in accounts:
            try:
                res = self.check_and_reply_for_account(acc)
                all_replies.extend(res)
            except Exception as e:
                logger.error(f"Error in reply loop for {acc.username}: {e}")
        return all_replies
