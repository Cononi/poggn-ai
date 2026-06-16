#!/usr/bin/env python3
from __future__ import annotations
import re

MAX_FEATURES = 6

FEATURE_WORDS = {
    "product": "상품 product item catalog",
    "order": "주문 order checkout purchase",
    "payment": "결제 payment pay billing",
    "member": "회원 user member account auth login",
    "cart": "장바구니 cart basket",
    "coupon": "쿠폰 coupon discount",
    "delivery": "배송 delivery shipment shipping",
    "review": "리뷰 후기 review rating",
    "inventory": "재고 inventory stock",
    "post": "게시글 post article board bulletin",
    "comment": "댓글 comment reply",
    "notification": "알림 notification notice",
    "file": "파일 file upload attachment image media",
    "report": "신고 report moderation",
    "reservation": "예약 reservation booking appointment",
    "availability": "일정 availability calendar slot schedule",
    "resource": "자원 resource room seat equipment",
    "cancellation": "취소 cancellation refund",
    "course": "강의 course class lecture",
    "lesson": "수업 lesson chapter video",
    "enrollment": "수강 enrollment registration",
    "progress": "진도 progress completion",
    "quiz": "퀴즈 quiz exam test",
    "certificate": "수료 certificate certification",
    "account": "고객사 account company",
    "contact": "연락처 contact lead customer",
    "deal": "영업기회 deal opportunity sales",
    "activity": "활동 activity task followup",
    "pipeline": "파이프라인 pipeline stage",
    "permission": "권한 permission role acl",
    "category": "카테고리 category taxonomy",
    "tag": "태그 tag hashtag",
    "author": "작성자 author writer",
    "seller": "판매자 seller vendor",
    "buyer": "구매자 buyer",
    "listing": "매물 listing item offer 중고거래",
    "settlement": "정산 settlement payout",
    "dispute": "분쟁 dispute claim",
    "chat": "채팅 chat message dm",
    "patient": "환자 patient",
    "doctor": "의사 doctor physician provider",
    "schedule": "일정 schedule calendar timetable",
    "media": "미디어 media image video",
}

DOMAIN_PRESETS = [
    {
        "triggers": "병원 clinic hospital healthcare medical 의원 진료",
        "base": ["patient", "doctor", "schedule", "reservation"],
        "optional": ["payment", "notification", "file"],
    },
    {
        "triggers": "커뮤니티 community 게시판 board forum bulletin",
        "base": ["post", "comment"],
        "optional": ["member", "notification", "file", "report"],
    },
    {
        "triggers": "쇼핑몰 ecommerce shop mall commerce store",
        "base": ["product", "member", "cart", "order"],
        "optional": ["payment", "coupon", "delivery", "review", "inventory"],
    },
    {
        "triggers": "예약 booking reservation appointment",
        "base": ["resource", "availability", "reservation"],
        "optional": ["payment", "notification", "cancellation", "member"],
    },
    {
        "triggers": "강의 lms education learning course lecture",
        "base": ["course", "lesson", "enrollment", "progress"],
        "optional": ["quiz", "certificate", "payment", "member"],
    },
    {
        "triggers": "crm sales 영업 고객관리",
        "base": ["account", "contact", "deal", "activity"],
        "optional": ["report", "pipeline", "permission"],
    },
    {
        "triggers": "블로그 blog",
        "base": ["post", "category", "tag"],
        "optional": ["comment", "author", "media"],
    },
    {
        "triggers": "마켓플레이스 marketplace 중고거래 flea trade 거래",
        "base": ["seller", "listing", "buyer", "order"],
        "optional": ["chat", "review", "payment", "settlement", "dispute"],
    },
]

STACK_WORDS = """
spring boot jpa h2 react mui next vue angular svelte typescript javascript
java kotlin node express nest vite gradle maven mysql postgres redis docker
api rest graphql swagger openapi frontend backend fullstack
"""
REQUEST_WORDS = """
만들어줘 만들어 개발 구현 추가 수정 개선 간단한 사이트 앱 서비스 시스템
create build make implement add update fix simple app web service platform
"""
def words(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9가-힣_]+", text.lower()))


def ordered_add(out: list[str], value: str) -> None:
    if value and value not in out:
        out.append(value)


def has_any(text_words: set[str], keys: str) -> bool:
    return bool(text_words & words(keys))


def has_frontend(text: str) -> bool:
    return has_any(words(text), "frontend react next vue angular svelte mui 화면 ui tsx")


def generic_features(text_words: set[str]) -> list[str]:
    found: list[str] = []
    for name, keys in FEATURE_WORDS.items():
        if has_any(text_words, keys):
            ordered_add(found, name)
    return found


def infer_features(text: str, explicit: str = "", max_features: int = MAX_FEATURES) -> list[str]:
    if explicit:
        return [x.strip() for x in explicit.split(",") if x.strip()][:max_features]
    q = words(text)
    found: list[str] = []
    for preset in DOMAIN_PRESETS:
        if not has_any(q, preset["triggers"]):
            continue
        for feature in preset["base"]:
            ordered_add(found, feature)
        for feature in preset["optional"]:
            if has_any(q, FEATURE_WORDS.get(feature, feature)):
                ordered_add(found, feature)
    for feature in generic_features(q):
        ordered_add(found, feature)
    stop = words(STACK_WORDS + " " + REQUEST_WORDS)
    filtered = [x for x in found if x not in stop]
    return (filtered or ["api"])[:max_features]
