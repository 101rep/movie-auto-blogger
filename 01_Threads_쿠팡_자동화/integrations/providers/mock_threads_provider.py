import uuid
from typing import List, Optional, Dict, Any
from integrations.interfaces import ThreadsProvider

class MockThreadsProvider(ThreadsProvider):
    def publish_post(self, text: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        post_id = f'mock_th_{uuid.uuid4().hex[:10]}'
        return {
            'status': 'SUCCESS',
            'post_id': post_id,
            'url': f'https://www.threads.net/@user/post/{post_id}',
            'text': text,
            'media_count': len(media_urls) if media_urls else 0
        }

    def publish_reply(self, parent_id: str, text: str) -> Dict[str, Any]:
        reply_id = f'mock_rep_{uuid.uuid4().hex[:10]}'
        return {
            'status': 'SUCCESS',
            'reply_id': reply_id,
            'parent_id': parent_id,
            'text': text
        }
