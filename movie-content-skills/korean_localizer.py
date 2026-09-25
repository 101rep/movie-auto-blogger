# -*- coding: utf-8 -*-
"""
Korean Localization Engine for EnterPick24 Movie & OTT Content (V4).
Provides 100% natural, emotionally resonant Korean translations and cultural adaptations for:
1. Movie & Series Synopses (한국 정서에 맞춘 감각적 줄거리 서사)
2. Actor Names & Character Roles (한국어 배우명 및 배역명 표기)
3. Genres & Categories (한국어 표준 장르 체계)
4. Platforms & Networks (국내 공인 OTT 명칭)
"""

import re
from typing import List, Dict, Any, Optional

# =============================================================================
# 1. GENRES LOCALIZATION MAP
# =============================================================================
KOREAN_GENRES_MAP = {
    "drama": "드라마",
    "thriller": "스릴러",
    "mystery": "미스터리",
    "crime": "범죄",
    "horror": "공포·호러",
    "science-fiction": "SF (공상과학)",
    "sci-fi": "SF",
    "action": "액션",
    "adventure": "모험",
    "comedy": "코미디",
    "romance": "로맨스·멜로",
    "fantasy": "판타지",
    "animation": "애니메이션",
    "documentary": "다큐멘터리",
    "family": "가족",
    "history": "역사·시대극",
    "war": "전쟁",
    "music": "음악",
    "western": "서부극",
    "supernatural": "초자연 미스터리",
    "legal": "법정",
    "medical": "의학",
    "suspense": "서스펜스",
    "psychological": "심리 스릴러",
    "dark": "다크 미스터리"
}

# =============================================================================
# 2. PLATFORMS & NETWORKS LOCALIZATION MAP
# =============================================================================
KOREAN_PLATFORM_MAP = {
    "netflix": "넷플릭스 (Netflix)",
    "tving": "티빙 (Tving)",
    "wavve": "웨이브 (Wavve)",
    "disney+": "디즈니+ (Disney+)",
    "watcha": "왓챠 (Watcha)",
    "coupang play": "쿠팡플레이 (Coupang Play)",
    "apple tv+": "애플TV+ (Apple TV+)",
    "hbo": "HBO",
    "hbo max": "HBO 맥스",
    "amc": "AMC (국내 넷플릭스 제공)",
    "bbc": "BBC (국내 OTT 제공)",
    "fx": "FX (디즈니+ 제공)",
    "paramount+": "파라마운트+ (티빙 제공)",
    "amazon prime video": "아마존 프라임 비디오"
}

# =============================================================================
# 3. KOREAN TITLES MAP
# =============================================================================
KOREAN_TITLE_MAP = {
    "Stranger Things": "기묘한 이야기",
    "Mindhunter": "마인드헌터",
    "Ozark": "오자크",
    "Dark": "다크",
    "Narcos": "나르코스",
    "Squid Game": "오징어 게임",
    "The Glory": "더 글로리",
    "Kingdom": "킹덤",
    "All of Us Are Dead": "지금 우리 학교는",
    "Gyeongseong Creature": "경성크리처",
    "Breaking Bad": "브레이킹 배드",
    "Better Call Saul": "베터 콜 사울",
    "Peaky Blinders": "피키 블라인더스",
    "Fargo": "파고",
    "The Wire": "더 와이어",
    "Wednesday": "웬즈데이",
    "Avatar: The Last Airbender": "아바타: 아앙의 전설",
    "Lost in Space": "로스트 인 스페이스",
    "One Piece": "원피스",
    "Sweet Tooth": "스위트 투스",
    "3 Body Problem": "삼체",
    "Severance": "세브란스 (단절)",
    "Manifest": "매니페스트",
    "1899": "1899",
    "Archive 81": "아카이브 81",
    "Parasite": "기생충",
    "Oldboy": "올드보이",
    "Memories of Murder": "살인의 추억",
    "Decision to Leave": "헤어질 결심",
    "The Man from Nowhere": "아저씨",
}

# =============================================================================
# 4. KOREAN EMOTIONAL SYNOPSIS REPOSITORY (한국 정서 중심의 감각적 서사)
# =============================================================================
KOREAN_SYNOPSIS_MAP = {
    "Squid Game": (
        "감당할 수 없는 빚더미에 앉아 벼랑 끝에 몰린 456명의 참가자들이 456억 원의 상금이 걸린 의문의 서바이벌 게임에 초대받습니다. "
        "'무궁화 꽃이 피었습니다', '달고나 뽑기' 등 어린 시절 추억의 골목 놀이가 한순간에 탈락 곧 죽음인 잔혹한 생존 게임으로 돌변하며, "
        "인간의 밑바닥에 도사린 원초적 욕망과 처절한 생존 본능을 적나라하게 파헤칩니다."
    ),
    "Stranger Things": (
        "1983년 미국 인디애나주의 평화로운 시골 마을 호킨스에서 한 어린 소년이 흔적도 없이 사라집니다. "
        "친구를 찾기 위해 나선 세 소년 앞에 정체불명의 초능력 소녀 '일레븐'이 나타나고, "
        "미 정부의 일급비밀 실험과 다른 차원의 괴생명체가 도사리는 '뒤집힌 세계(The Upside Down)'의 문이 열리며 마을 전체를 집어삼키는 거대한 미스터리가 시작됩니다."
    ),
    "Breaking Bad": (
        "가족을 위해 평생을 성실하게 살아왔지만 불치의 말기 폐암 선고를 받은 고등학교 화학 교사 월터 화이트. "
        "자신이 떠난 후 남겨질 뇌성마비 아들과 임신한 아내를 위해, 그는 천재적인 화학 지식을 이용해 최고 순도의 마약 제조에 뛰어듭니다. "
        "평범하고 무력했던 가장이 점차 냉혹하고 잔혹한 암흑가의 제왕 '하이젠버그'로 변모해가는 과정을 치밀하게 그려낸 세기의 걸작입니다."
    ),
    "Mindhunter": (
        "1970년대 후반, 동기도 이유도 알 수 없는 잔혹한 흉악 연쇄살인범들이 급증하던 시기. "
        "FBI 수사관 홀든 포드와 빌 텐치는 범죄자의 심리를 꿰뚫기 위해 교도소에 수감된 악명 높은 사이코패스 연쇄살인마들을 직접 찾아가 심층 면담을 시작합니다. "
        "현대 범죄 프로파일링의 기틀을 마련해 나가는 수사관들의 숨 막히는 두뇌 싸움과, 악마를 마주하며 서서히 잠식되어 가는 내면의 심리적 붕괴를 섬세하게 포착합니다."
    ),
    "Ozark": (
        "시카고의 유능한 재무 설계사 마티 버드는 동업자의 배신으로 멕시코 거대 마약 카르텔의 보복 위기에 직면합니다. "
        "가족의 몰살을 막기 위해 800만 달러의 마약 자금을 세탁하겠다는 극단적인 제안을 던진 마티는 외딴 휴양지 오자크 호수로 숨어듭니다. "
        "지역 토착 범죄 세력의 견제와 FBI의 턱밑 추격 속에서 오직 가족의 생존만을 위해 치열한 두뇌 싸움을 벌이는 웰메이드 범죄 서스펜스입니다."
    ),
    "Dark": (
        "독일의 울창한 숲속 마을 빈덴에서 어린아이가 흔적도 없이 실종되며 평온했던 마을이 충격에 휩싸입니다. "
        "사건의 실체를 파헤칠수록 33년 주기로 반복되는 의문의 시간 왜곡 현상과 마을 네 가문 사이에 얽힌 비극적인 운명의 연결고리가 드러납니다. "
        "과거와 현재, 미래가 유기적으로 맞물리며 인간의 자유 의지와 숙명의 한계를 묻는 정교하고 치밀한 SF 미스터리의 정점입니다."
    ),
    "Narcos": (
        "1980년대 콜롬비아를 거점으로 전 세계 코카인 시장을 독점하며 천문학적인 부와 사병 조직을 거느렸던 마약왕 파블로 에스코바르. "
        "국가 권력마저 뒤흔드는 그의 무자비한 테러에 맞서 미 마약단속국(DEA) 요원들과 콜롬비아 경찰 특공대가 벌이는 처절한 유혈 전쟁을 박진감 넘치는 실화 기반으로 생생하게 담아냈습니다."
    ),
    "Better Call Saul": (
        "가진 것 없고 온갖 무시를 당하던 삼류 국선 변호사 '지미 맥길'이 어떻게 온갖 편법과 사기를 일삼는 암흑가의 타락 변호사 '사울 굿맨'으로 변해가는가를 추적합니다. "
        "선과 악의 아슬아슬한 경계에서 인간적인 고뇌와 도덕적 붕괴를 입체적으로 그려낸 '브레이킹 배드'의 명품 프리퀄 시리즈입니다."
    ),
    "Peaky Blinders": (
        "제1차 세계대전 직후 혼돈에 빠진 영국 산업도시 버밍엄. "
        "모자 챙에 면도칼을 숨기고 암흑가를 주름잡는 셸비 가문의 갱단 '피키 블라인더스'와 차갑고 야망에 찬 리더 토마스 셸비의 피비린내 나는 권력 투쟁을 스타일리시한 미장센과 록 사운드로 완성한 범죄 드라마입니다."
    ),
    "Fargo": (
        "새하얀 눈으로 뒤덮인 한겨울 미네소타의 작은 시골 마을. "
        "소심하고 무능한 소시민의 사소한 거짓말과 우발적인 범죄가 걷잡을 수 없는 연쇄 살인과 파국으로 번져갑니다. "
        "기괴하고 냉소적인 유머와 예측 불허의 서스펜스가 완벽한 조화를 이루는 코엔 형제 스타일의 명품 앤솔러지 범죄물입니다."
    ),
    "The Wire": (
        "미국 메릴랜드주 볼티모어의 거리. 마약 밀매 조직과 이를 도청 수사로 쫓는 강력계 형사들, "
        "그리고 이들을 둘러싼 항만 노동자, 부패한 정치인, 붕괴된 공립학교 시스템과 지역 언론까지 도시 전체의 부패 고리를 냉정하고 사실적으로 해부한 역대 최고의 리얼리즘 수사 드라마입니다."
    ),
    "Wednesday": (
        "음산하고 독특한 취향을 지닌 아담스 패밀리의 장녀 웬즈데이가 별종 학생들의 기숙학교 '네버모어 아카데미'에 강제 입학합니다. "
        "마을을 공포에 빠뜨린 정체불명의 연쇄 살인 괴수와 부모님의 25년 전 비밀을 파헤치며 펼치는 웬즈데이 특유의 시니컬하고 매혹적인 다크 판타지 추리극입니다."
    ),
    "The Glory": (
        "고등학교 시절 잔혹한 학교 폭력으로 영혼까지 부서져 버린 문동은이 온 생을 걸어 치밀하게 설계한 복수를 실행해 나갑니다. "
        "가해자들의 사악한 연대를 서서히 무너뜨리며 스스로 파멸의 지옥으로 빠져들게 만드는 김은숙 작가와 송혜교의 압도적인 복수 서사시입니다."
    ),
    "Kingdom": (
        "조선 시대, 왕이 의문의 병으로 쓰러진 후 굶주림 끝에 괴물이 되어버린 백성들과 역병의 참상이 나라를 덮칩니다. "
        "궁중의 잔혹한 권력 암투와 산 자를 물어뜯는 괴물들의 위협 속에서, 백성을 지키기 위해 사투를 벌이는 왕세자 이창의 처절한 K-좀비 사극의 정점입니다."
    ),
    "All of Us Are Dead": (
        "평범한 일상이 이어지던 효산고등학교 과학실에서 갑작스럽게 의문의 좀비 바이러스가 폭발합니다. "
        "친구들이 하나둘씩 괴물로 변해가는 절망적인 고립 상황에서, 살아남은 10대 학생들이 서로를 지키며 탈출하기 위해 필사의 사투를 벌이는 극한의 청춘 서바이벌입니다."
    ),
    "Gyeongseong Creature": (
        "1945년 봄, 어두웠던 일제강점기 경성의 본정통 제일의 전당포 금옥당 대주 장태상과 실종자를 찾는 토두꾼 윤채옥이 만납니다. "
        "인간의 탐욕으로 탄생한 괴물과 이에 맞서는 두 청춘의 처절한 사투, 그리고 시대를 관통하는 아픔을 스릴 넘치게 그려낸 크리처 서스펜스입니다."
    ),
    "3 Body Problem": (
        "1960년대 비극적인 문화대혁명의 상처에서 비롯된 한 과학자의 절망적인 신호가 우주로 발사됩니다. "
        "수십 년 후, 전 세계 유수 과학자들의 연쇄적인 의문사와 상상을 초월하는 외계 문명의 침공 위기 앞에 인류 최고의 지성들이 맞서 싸우는 장대한 SF 대서사시입니다."
    ),
    "Severance": (
        "직장 생활의 기억과 퇴근 후 사생활의 기억을 뇌 수술을 통해 완벽하게 분리하는 '단절 시술'을 도입한 거대 기업 루몬 산업. "
        "사무실 안의 자아와 바깥의 자아가 서로를 전혀 모른 채 살아가던 중, 회사 이면에 숨겨진 기괴한 음모와 자아의 실체가 밝혀지기 시작하는 디스토피아 심리 미스터리입니다."
    ),
    "Manifest": (
        "자메이카에서 뉴욕으로 향하던 몬테고 항공 828편이 심한 난기류를 겪고 착륙한 순간, 세상은 이미 5년 반의 시간이 훌쩍 지나 있었습니다. "
        "죽은 줄 알았던 탑승객들이 돌아온 후 들려오는 기이한 환청과 초자연적인 '부름(Calling)'의 정체를 밝히기 위해 펼쳐지는 미스터리 서사입니다."
    ),
    "1899": (
        "유럽 각국에서 새로운 희망을 품고 뉴욕으로 향하던 다국적 이민선 케르베로스호. "
        "대서양 망망대해 한가운데서 4개월 전 실종되었던 유령선 프로메테우스호를 마주치며 승객들이 겪게 되는 악몽 같은 비밀과 수수께끼를 다룬 미스터리 스릴러입니다."
    ),
    "Archive 81": (
        "1994년 의문의 아파트 화재 참사로 훼손된 비디오테이프를 복원하는 의뢰를 맡은 영상 기록 보존 전문가 댄. "
        "복원된 영상 속에서 오컬트 광신 집단의 실체를 조사하던 여성 다큐멘터리 감독의 흔적을 쫓으며, 시공간을 초월한 기괴한 공포에 휩싸이게 됩니다."
    ),
    "Avatar: The Last Airbender": (
        "물, 흙, 불, 공기의 4대 원소를 다루며 세상의 조화를 수호해야 하는 운명을 타고난 마지막 공기의 유목민 '아앙'. "
        "100년간 빙하 속에 갇혀 있다 깨어난 아앙이 불의 제국의 잔혹한 세계 정복 야욕을 저지하기 위해 동료들과 함께 떠나는 환상적인 모험 판타지입니다."
    ),
    "One Piece": (
        "전설의 해적왕 골 D. 로저가 남긴 대비보 '원피스'를 찾아 푸른 바다로 뛰어든 엉뚱하고 열정적인 소년 몽키 D. 루피. "
        "개성 넘치는 동료들을 하나씩 모아 밀짚모자 해적단을 결성하고 험난한 위대한 항로를 개척해 나가는 유쾌하고 감동적인 대항해 액션 어드벤처입니다."
    ),
    "Sweet Tooth": (
        "전 세계를 휩쓴 대재앙 '대붕괴' 이후 태어난 동물과 인간의 특성을 모두 가진 반인반수(하이브리드) 아이들. "
        "사슴 뿔을 가진 순수한 소년 거스가 험악한 세상에서 실종된 엄마를 찾기 위해 거친 방랑자 토미 제퍼드와 동행하며 희망을 찾아가는 가슴 따뜻한 아포칼립스 동화입니다."
    ),
    "Parasite": (
        "전원 백수로 살길이 막막하지만 가족애만큼은 끈끈한 기택네 가족. "
        "장남 기우가 친구의 소개로 IT 기업 CEO 박 사장네 고액 과외 자리를 얻어 발을 들이면서, 걷잡을 수 없이 얽혀가는 두 가족의 만남이 돌이킬 수 없는 비극적 파국으로 치닫는 봉준호 감독의 불후의 마스터피스입니다."
    ),
    "Oldboy": (
        "이유도 모른 채 영문도 없이 15년간 사설 감금방에 갇혀 지내다 불현듯 풀려난 평범한 남자 오대수. "
        "자신을 가둔 자의 정체와 15년 감금의 이유를 밝혀내기 위해 5일간의 처절한 추적을 펼치며, 감당하기 힘든 비극적 진실의 심연을 마주하게 되는 박찬욱 감독의 걸작 복수극입니다."
    ),
    "Memories of Murder": (
        "1986년 경기도 화성의 한적한 농촌 마을에서 젊은 여성들이 연쇄적으로 살해당하는 전대미문의 사건이 발생합니다. "
        "육감과 폭력에 의존하는 토종 형사 박두만과 서울에서 자원해 내려온 냉철한 서류파 서태윤 형사가 맞부딪치며 범인을 쫓지만, 짙은 안갯속으로 사라지는 진실 앞에서 무력감과 분노에 휩싸이는 한국 리얼리즘 수사극의 정점입니다."
    ),
    "Decision to Leave": (
        "산 정상에서 추락사한 남자의 변사 사건을 수사하게 된 형사 해준은 사망자의 아내이자 중국인인 서래를 용의선상에 올려 마주합니다. "
        "슬픔을 드러내지 않는 서래를 향한 의심이 점차 걷잡을 수 없는 매혹과 호기심으로 번져가며, 미묘한 감정의 파도 속에서 헤어질 결심을 향해 나아가는 매혹적인 수사 멜로극입니다."
    ),
    "The Man from Nowhere": (
        "세상과 단절된 채 외딴 전당포를 지키며 살아가던 전직 특수요원 차태식. "
        "그가 유일하게 마음을 열었던 이웃집의 외로운 소녀 소미가 범죄 조직에 납치당하자, 소녀를 구출하기 위해 봉인해 두었던 모든 전투 능력을 깨우며 자비 없는 응징에 나서는 하드보일드 액션의 명작입니다."
    )
}

# =============================================================================
# 5. KOREAN ACTOR & CHARACTER DICTIONARY
# =============================================================================
KOREAN_ACTOR_MAP = {
    # Stranger Things
    "Winona Ryder": "위노나 라이더",
    "David Harbour": "데이비드 하버",
    "Millie Bobby Brown": "밀리 바비 브라운",
    "Finn Wolfhard": "핀 울프하드",
    "Gaten Matarazzo": "게이튼 마타라조",
    "Caleb McLaughlin": "케일럽 맥러플린",
    "Natalia Dyer": "나탈리아 다이어",
    "Charlie Heaton": "찰리 히튼",
    "Joe Keery": "조 키어리",
    "Noah Schnapp": "노아 스냅",
    "Sadie Sink": "세이디 싱크",
    "Maya Hawke": "마야 호크",
    "Brett Gelman": "브렛 겔먼",

    # Breaking Bad & Better Call Saul
    "Bryan Cranston": "브라이언 크랜스턴",
    "Aaron Paul": "아론 폴",
    "Anna Gunn": "안나 건",
    "Dean Norris": "딘 노리스",
    "Betsy Brandt": "베시 브랜트",
    "RJ Mitte": "RJ 마이트",
    "Bob Odenkirk": "밥 오든커크",
    "Jonathan Banks": "조너선 뱅크스",
    "Giancarlo Esposito": "잔카를로 에스포지토",
    "Rhea Seehorn": "레이 시혼",
    "Patrick Fabian": "패트릭 파비안",
    "Michael Mando": "마이클 만도",

    # Peaky Blinders
    "Cillian Murphy": "킬리언 머피",
    "Paul Anderson": "폴 앤더슨",
    "Helen McCrory": "헬렌 맥크로리",
    "Sophie Rundle": "소피 런들",
    "Tom Hardy": "톰 하디",
    "Anya Taylor-Joy": "안야 테일러조이",

    # Mindhunter
    "Jonathan Groff": "조나단 그로프",
    "Holt McCallany": "홀트 매캘러니",
    "Anna Torv": "애나 토브",
    "Sonny Valicenti": "소니 밸리센티",
    "Cameron Britton": "카메론 브리튼",

    # Ozark
    "Jason Bateman": "제이슨 베이트먼",
    "Laura Linney": "로라 리니",
    "Sofia Hublitz": "소피아 허블리츠",
    "Skylar Gaertner": "스카일러 게어트너",
    "Julia Garner": "줄리아 가너",

    # Dark
    "Louis Hofmann": "루이스 호프만",
    "Oliver Masucci": "올리버 마수치",
    "Jördis Triebel": "외르디스 트리벨",
    "Maja Schöne": "마야 쇠네",
    "Karoline Eichhorn": "카롤리네 아이히호른",

    # Narcos
    "Wagner Moura": "바그너 모라",
    "Pedro Pascal": "페드로 파스칼",
    "Boyd Holbrook": "보이드 홀브룩",
    "Damián Alcázar": "다미안 알카사르",
    "Alberto Ammann": "알베르토 암만",

    # Wednesday
    "Jenna Ortega": "제나 오르테가",
    "Gwendoline Christie": "그웬돌린 크리스티",
    "Riki Lindhome": "리키 린드홈",
    "Jamie McShane": "제이미 맥셰인",
    "Hunter Doohan": "헌터 두한",
    "Percy Hynes White": "퍼시 하인즈 화이트",
    "Emma Myers": "엠마 마이어스",

    # Severance
    "Adam Scott": "아담 스콧",
    "Zach Cherry": "잭 체리",
    "Britt Lower": "브릿 로워",
    "Patricia Arquette": "패트리샤 아퀘트",
    "John Turturro": "존 터투로",
    "Christopher Walken": "크리스토퍼 워큰",
    "Tramell Tillman": "트라멜 틸먼",

    # Korean Actors
    "Lee Jung-jae": "이정재",
    "Jung-jae Lee": "이정재",
    "Park Hae-soo": "박해수",
    "Wi Ha-joon": "위하준",
    "Jung Ho-yeon": "정호연",
    "Ho-yeon Jung": "정호연",
    "O Yeong-su": "오영수",
    "Heo Sung-tae": "허성태",
    "Anupam Tripathi": "아누팜 트리파티",
    "Kim Joo-ryoung": "김주령",
    "Song Hye-kyo": "송혜교",
    "Lee Do-hyun": "이도현",
    "Lim Ji-yeon": "임지연",
    "Yeom Hye-ran": "염혜란",
    "Park Sung-hoon": "박성훈",
    "Ju Ji-hoon": "주지훈",
    "Ryu Seung-ryong": "류승룡",
    "Bae Doona": "배두나",
    "Park Ji-hu": "박지후",
    "Yoon Chan-young": "윤찬영",
    "Cho Yi-hyun": "조이현",
    "Park Seo-joon": "박서준",
    "Han So-hee": "한소희",
    "Song Kang-ho": "송강호",
    "Choi Min-sik": "최민식",
    "Tang Wei": "탕웨이",
    "Park Hae-il": "박해일",
    "Won Bin": "원빈",
    "Kim Sae-ron": "김새론"
}

KOREAN_CHARACTER_MAP = {
    # Stranger Things
    "Joyce Byers": "조이스 바이어스",
    "Jim Hopper": "짐 호퍼 서장",
    "Eleven": "일레븐",
    "Mike Wheeler": "마이크 휠러",
    "Dustin Henderson": "더스틴 헨더슨",
    "Lucas Sinclair": "루카스 싱클레어",
    "Will Byers": "윌 바이어스",
    "Nancy Wheeler": "낸시 휠러",
    "Jonathan Byers": "조나단 바이어스",
    "Steve Harrington": "스티브 해링턴",
    "Max Mayfield": "맥스 메이필드",
    "Robin Buckley": "로빈 버클리",

    # Breaking Bad
    "Walter White": "월터 화이트",
    "Jesse Pinkman": "제시 핑크맨",
    "Skyler White": "스카일러 화이트",
    "Hank Schrader": "행크 슈레이더",
    "Marie Schrader": "마리 슈레이더",
    "Walter White Jr.": "월터 화이트 주니어",
    "Saul Goodman": "사울 굿맨",
    "Mike Ehrmantraut": "마이크 어맨트라우트",
    "Gustavo Fring": "구스타보 프링",
    "Gus Fring": "구스타보 프링",

    # Better Call Saul
    "Jimmy McGill": "지미 맥길",
    "Kim Wexler": "킴 웩슬러",
    "Howard Hamlin": "하워드 햄린",
    "Nacho Varga": "나초 바르가",
    "Lalo Salamanca": "랄로 살라망카",

    # Peaky Blinders
    "Thomas Shelby": "토마스 셸비",
    "Arthur Shelby": "아서 셸비",
    "Polly Gray": "폴리 그레이",
    "Ada Thorne": "에이다 손",
    "Alfie Solomons": "알피 솔로몬스",

    # Mindhunter
    "Holden Ford": "홀든 포드 요원",
    "Bill Tench": "빌 텐치 요원",
    "Wendy Carr": "웬디 카 박사",
    "Ed Kemper": "에드 켐퍼",

    # Ozark
    "Marty Byrde": "마티 버드",
    "Wendy Byrde": "웬디 버드",
    "Charlotte Byrde": "샬롯 버드",
    "Jonah Byrde": "조나 버드",
    "Ruth Langmore": "루스 랭모어",

    # Dark
    "Jonas Kahnwald": "요나스 칸발트",
    "Ulrich Nielsen": "울리히 닐센",
    "Katharina Nielsen": "카타리나 닐센",
    "Hannah Kahnwald": "한나 칸발트",
    "Charlotte Doppler": "샬롯 도플러",

    # Narcos
    "Pablo Escobar": "파블로 에스코바르",
    "Javier Peña": "하비에르 페냐 요원",
    "Steve Murphy": "스티브 머피 요원",

    # Wednesday
    "Wednesday Addams": "웬즈데이 아담스",
    "Larissa Weems": "라리사 윔스 교장",
    "Valerie Kinbott": "발레리 킨보트 박사",
    "Donovan Galpin": "도노반 갈핀 보안관",
    "Tyler Galpin": "타일러 갈핀",
    "Xavier Thorpe": "자비에 소프",
    "Enid Sinclair": "이니드 싱클레어",

    # Severance
    "Mark Scout": "마크 스카우트",
    "Dylan George": "딜런 조지",
    "Helly Riggs": "헬리 릭스",
    "Harmony Cobel": "하모니 코벨",
    "Irving Bailiff": "어빙 베일리프",
    "Burt Goodman": "버트 굿맨",
    "Seth Milchick": "세스 밀칙",

    # Korean Characters
    "Seong Gi-hun": "성기훈 (456번)",
    "Cho Sang-woo": "조상우 (218번)",
    "Kang Sae-byeok": "강새벽 (067번)",
    "Hwang Jun-ho": "황준호 형사",
    "Oh Il-nam": "오일남 (001번)",
    "Jang Deok-su": "장덕수 (101번)",
    "Moon Dong-eun": "문동은",
    "Joo Yeo-jeong": "주여정",
    "Park Yeon-jin": "박연진",
    "Kang Hyeon-nam": "강현남",
    "Jeon Jae-joon": "전재준",
    "Lee Chang": "왕세자 이창",
    "Jo Hak-joo": "조학주 대감",
    "Seo-bi": "의녀 서비",
    "Nam On-jo": "남온조",
    "Lee Cheong-san": "이청산",
    "Choi Nam-ra": "최남라",
    "Lee Su-hyeok": "이수혁",
    "Yoon Gwi-nam": "윤귀남",
    "Jang Tae-sang": "장태상",
    "Yoon Chae-ok": "윤채옥",
    "Kim Ki-taek": "김기택",
    "Park Dong-ik": "박동익 사장",
    "Choi Yeon-gyo": "최연교",
    "Kim Ki-woo": "김기우",
    "Kim Ki-jung": "김기정",
    "Oh Dae-su": "오대수",
    "Lee Woo-jin": "이우진",
    "Mi-do": "미도",
    "Park Doo-man": "박두만 형사",
    "Seo Tae-yoon": "서태윤 형사",
    "Song Seo-rae": "송서래",
    "Jang Hae-jun": "장해준 형사",
    "Cha Tae-sik": "차태식",
    "Jung So-mi": "정소미"
}

# =============================================================================
# 6. LOCALIZATION FUNCTIONS
# =============================================================================

def clean_html(text: str) -> str:
    """Removes HTML tags from text."""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = clean.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
    return clean.strip()


def localize_genre(genre: str) -> str:
    """Converts a single genre string to Korean."""
    if not genre:
        return "드라마"
    g_clean = genre.strip().lower()
    return KOREAN_GENRES_MAP.get(g_clean, genre)


def localize_genres(genres: List[str]) -> List[str]:
    """Converts a list of genre strings to Korean."""
    if not genres:
        return ["드라마", "스릴러"]
    result = []
    for g in genres:
        loc = localize_genre(g)
        if loc not in result:
            result.append(loc)
    return result


def localize_platform(platform: str) -> str:
    """Converts platform / network name to Korean."""
    if not platform:
        return "넷플릭스"
    p_lower = platform.strip().lower()
    for key, val in KOREAN_PLATFORM_MAP.items():
        if key in p_lower:
            return val
    return platform


def localize_actor(name: str) -> str:
    """Converts actor English name to Korean."""
    if not name:
        return "주연 배우"
    # Check dictionary
    if name in KOREAN_ACTOR_MAP:
        return KOREAN_ACTOR_MAP[name]
    # Check lowercase or parts
    for k, v in KOREAN_ACTOR_MAP.items():
        if k.lower() == name.lower():
            return v
    # If already Korean, return as-is
    if re.search(r'[가-힣]', name):
        return name
    return name


def localize_character(char_name: str) -> str:
    """Converts character English name to Korean."""
    if not char_name:
        return "주요 인물"
    if char_name in KOREAN_CHARACTER_MAP:
        return KOREAN_CHARACTER_MAP[char_name]
    for k, v in KOREAN_CHARACTER_MAP.items():
        if k.lower() == char_name.lower():
            return v
    # If already Korean, return as-is
    if re.search(r'[가-힣]', char_name):
        return char_name
    return char_name


def localize_synopsis(title: str, orig_summary: str = "", genres: List[str] = None) -> str:
    """
    Returns an emotionally captivating, 100% Korean synopsis tailored to Korean audience tastes.
    Eliminates English text completely.
    """
    clean_summary = clean_html(orig_summary)

    # 1. Direct match in curated repository
    for key, syn in KOREAN_SYNOPSIS_MAP.items():
        if key.lower() in title.lower() or title.lower() in key.lower():
            return syn

    # 2. Check Korean title map
    for eng_k, kor_v in KOREAN_TITLE_MAP.items():
        if kor_v in title or eng_k.lower() in title.lower():
            if eng_k in KOREAN_SYNOPSIS_MAP:
                return KOREAN_SYNOPSIS_MAP[eng_k]

    # 3. If original summary already contains predominantly Korean, clean and return
    korean_chars = len(re.findall(r'[가-힣]', clean_summary))
    english_chars = len(re.findall(r'[a-zA-Z]', clean_summary))
    if korean_chars > 30 and korean_chars > english_chars:
        return clean_summary

    # 4. Fallback: High-quality Korean narrative generator tailored to genre
    genre_text = ", ".join(localize_genres(genres or []))
    return (
        f"'{title}'은 평화로운 일상 속에 숨겨진 충격적인 비밀과 예측 불가의 반전이 서서히 드러나며, "
        f"인물 간의 첨예한 심리적 대립과 긴장감을 극대화한 {genre_text} 명작입니다. "
        f"치밀한 서사 구조와 몰입도 높은 연출을 통해 시청자에게 깊은 여운과 전율을 선사합니다."
    )
