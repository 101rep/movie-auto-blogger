import hashlib
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from apps.backend.tre.models import MockRemotePost
from .contracts import ProviderError

class MockThreadsProvider:
    def __init__(self, session_factory):
        self.factory = session_factory
    def _publish(self, text, key, parent=None):
        remote_id = "mock_" + hashlib.sha256(key.encode()).hexdigest()[:24]
        with self.factory() as db:
            existing = db.scalar(select(MockRemotePost).where(MockRemotePost.key == key))
            if existing:
                if existing.body != text or existing.parent_id != parent:
                    raise ProviderError("IDEMPOTENCY_CONFLICT")
                return existing.remote_id
            if parent and not db.scalar(select(MockRemotePost).where(MockRemotePost.remote_id == parent)):
                raise ProviderError("PARENT_NOT_FOUND")
            db.add(MockRemotePost(key=key,remote_id=remote_id,body=text,parent_id=parent))
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                existing = db.scalar(select(MockRemotePost).where(MockRemotePost.key == key))
                if not existing or existing.body != text or existing.parent_id != parent:
                    raise ProviderError("IDEMPOTENCY_CONFLICT")
        return remote_id
    def publish_text(self,text,key): return self._publish(text,key)
    def publish_image(self,text,image_url,key): return self._publish(text+"\n[MOCK IMAGE] "+image_url,key)
    def publish_reply(self,parent_id,text,key): return self._publish(text,key,parent_id)
    def get_post(self,remote_id):
        with self.factory() as db:
            p=db.scalar(select(MockRemotePost).where(MockRemotePost.remote_id==remote_id))
            if not p: raise ProviderError("REMOTE_NOT_FOUND", True)
            return {"id":p.remote_id,"text":p.body,"parent_id":p.parent_id,"mock":True}
    def get_insights(self,remote_id):
        self.get_post(remote_id)
        return {"views":None,"likes":None,"revenue":None,"mock":True}
    def validate_token(self): return True
    def refresh_token_if_supported(self): return None

class MockAIProvider:
    def analyze(self,source,accounts):
        return {"core_message":source.source_title,"target_reader":source.category,"desire":"시간 절약",
                "pain_point":"선택에 필요한 정보 부족","hook_candidate":"OBSERVATION",
                "evidence":[source.source_url] if source.source_url else [],"transformation":"요약 후 관점 재구성",
                "content_goal":"INFORMATION","product_keywords":[source.category],"risk_flags":["HUMAN_REVIEW_REQUIRED"],
                "source_reliability":"UNVERIFIED","account_matches":[{"account_id":a.id,"score":90 if a.category==source.category else 20} for a in accounts],"mock":True}
    def generate(self,source,account,persona,angle,hook):
        topic=source.source_title[:65]
        reader=persona.target_description if persona else account.category
        return f"{topic}, 어디부터 확인하면 좋을까요?\n\n{reader}에게는 선택 기준 2개를 먼저 적어보는 방법이 있어요.\n필요한 기능과 보관할 공간을 나눠 확인해 보세요.\n\n어떤 기준을 먼저 보시나요?"
    def rewrite(self,text,feedback): return text.replace("결론부터 말하면", "").strip()
    def classify(self,text): return "INFORMATION"

class MockTelegramProvider:
    def send(self,text,key):
        return "mock_tg_"+hashlib.sha256(key.encode()).hexdigest()[:16]

class MockAffiliateProvider:
    def __init__(self,products): self.products=products
    def search_products(self,keyword): return [p for p in self.products if keyword in p.name or keyword in p.category]
    def create_deeplink(self,url): return "https://example.invalid/affiliate/"+hashlib.sha256(url.encode()).hexdigest()[:12]
    def get_reports(self): return {"clicks":None,"orders":None,"revenue":None,"mock":True}
    def validate_product(self,p): return p.active and p.metadata_json.get("mock") is True

class ManualContentProvider:
    def __init__(self,items): self.items=items
    def fetch(self): return self.deduplicate([self.normalize(i) for i in self.items if self.validate(i)])
    def normalize(self,i): return {**i,"source_text":i["source_text"].strip()}
    def validate(self,i): return bool(i.get("source_text", "").strip())
    def deduplicate(self,items): return list({i["source_text"]:i for i in items}.values())
