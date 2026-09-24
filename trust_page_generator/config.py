"""Configuration and WordPress Site Registry for Trust Page Generator V1.0."""
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = str(DATA_DIR / "trust_pages.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# 8 WordPress Blogs Master Registry
BLOG_REGISTRY: Dict[int, Dict[str, Any]] = {
    1: {
        "site_id": 1,
        "name": "트래블픽24",
        "url": "https://travelpick24.com",
        "user": "ktaehoon80@gmail.com",
        "pass": "FyjEIgqbXJzrT0h0nYEMXSXC",
        "vertical": "TRAVEL",
        "category": "종합 여행 가이드",
        "contact_email": "contact@travelpick24.com"
    },
    2: {
        "site_id": 2,
        "name": "트렌드스팟24",
        "url": "https://trendspot24.com",
        "user": "ktaehoon80@gmail.com",
        "pass": "cAJAtRGsDPC4r9zFwuBvtkaY",
        "vertical": "TREND",
        "category": "트렌드 & 라이프스타일",
        "contact_email": "contact@trendspot24.com"
    },
    3: {
        "site_id": 3,
        "name": "아이템픽24",
        "url": "https://item.travelpick24.com",
        "user": "ktaehoon80@gmail.com",
        "pass": "ZGeEcLKGwGxtwgIB3O4Yd0NY",
        "vertical": "PRODUCT",
        "category": "테크 기기 & 데스크테리어",
        "contact_email": "item@travelpick24.com"
    },
    4: {
        "site_id": 4,
        "name": "엔터픽24",
        "url": "https://enter.trendspot24.com",
        "user": "ktaehoon80@gmail.com",
        "pass": "aUma6aotA2Q5ugxkohI5PnKd",
        "vertical": "ENTERTAINMENT",
        "category": "영화 & 연예 OTT",
        "contact_email": "enter@trendspot24.com"
    },
    5: {
        "site_id": 5,
        "name": "복지픽23",
        "url": "https://welfare23.travelpick24.com",
        "user": "ktaehoon80@gmail.com",
        "pass": "aEfWGRB2saPixGDR5qVybLMI",
        "vertical": "WELFARE_YOUTH",
        "category": "청년 & 주거복지",
        "contact_email": "welfare23@travelpick24.com"
    },
    6: {
        "site_id": 6,
        "name": "복지픽24",
        "url": "https://welfare24.travelpick24.com",
        "user": "ktaehoon80@gmail.com",
        "pass": "tjSclWsJhxvlHLJKRqNLULyD",
        "vertical": "WELFARE_SENIOR",
        "category": "시니어 & 소상공인",
        "contact_email": "welfare24@travelpick24.com"
    },
    7: {
        "site_id": 7,
        "name": "복지픽25",
        "url": "https://welfare25.travelpick24.com",
        "user": "ktaehoon80@gmail.com",
        "pass": "A5XTcottQu6LP8FnKsP4Li57",
        "vertical": "WELFARE_VOUCHER",
        "category": "정부지원금 & 바우처",
        "contact_email": "welfare25@travelpick24.com"
    },
    8: {
        "site_id": 8,
        "name": "뉴스픽24",
        "url": "https://news.trendspot24.com",
        "user": "ktaehoon80@gmail.com",
        "pass": "qAjbgNrvE4V2yQh0IpB7yFR9",
        "vertical": "NEWS",
        "category": "실시간 시사 뉴스",
        "contact_email": "news@trendspot24.com"
    }
}
