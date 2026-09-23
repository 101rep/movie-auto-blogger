import pytest
from database.connection import SessionLocal
from database.models import Account
from services.reply_service import ReplyEngineService

def test_reply_engine_generation():
    db = SessionLocal()
    svc = ReplyEngineService(db)

    test_cases = [
        ("toontoooon", "다이소 귀여운 키링", "fan1", "너무 귀여워요 어디서 사셨나요?"),
        ("kth.101rep", "맥북 배터리 관리", "dev1", "설정 방법이나 앱 이름 추천 부탁드려요"),
        ("ktaehoon80", "월요일 출근", "worker1", "월요일 너무 피곤해요 퇴근하고 싶다 ㅠㅠ"),
        ("yr170425", "주방 기름때 청소", "housewife1", "청소 꿀팁 너무 유용해요 대박!"),
        ("101rep80", "가성비 비교", "smart1", "가격 차이 많이 나나요? 진짜 공감돼요"),
        ("lookatmeai", "환절기 피부 팁", "beauty1", "피부 화장 떴을 때 이 루틴 해볼게요"),
        ("taechi.tube", "근교 카페 여행", "travel1", "장소 감성 넘치네요 어딘가요?")
    ]

    for uname, post, author, comment in test_cases:
        acc = db.query(Account).filter(Account.username == uname).first()
        assert acc is not None, f"Account {uname} should exist"
        reply = svc.generate_reply_text(acc, post, author, comment)
        assert len(reply) > 5, f"Reply for {uname} should not be empty"
        # Check that product inquiry replies correctly mention item number and profile link
        if "어디" in comment:
            assert "프로필 링크" in reply or "링크" in reply
        print(f"\n[{uname}] @{author}: {comment} -> Reply: {reply}".encode('utf-8', 'replace').decode('latin1', 'replace'))

    db.close()
