import pytest
from utils.json_parser import clean_json_string, parse_and_validate_json
from domain_types.schemas import ProductScoreResult

def test_clean_json_markdown():
    raw = """```json
    {
        "price_score": 18,
        "review_score": 19,
        "rating_score": 20,
        "shipping_score": 19,
        "conversion_score": 18,
        "content_score": 14,
        "seasonality_score": 8,
        "total_score": 88,
        "reason": "테스트 점수 이유"
    }
    ```"""
    parsed = parse_and_validate_json(raw, ProductScoreResult)
    assert parsed.total_score == 88
    assert parsed.price_score == 18

def test_json_validation_failure():
    invalid_raw = '{"total_score": "not_an_int"}'
    with pytest.raises(Exception):
        parse_and_validate_json(invalid_raw, ProductScoreResult)