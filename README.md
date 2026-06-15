# Spring Boot H2 쇼핑몰

간단한 쇼핑몰 REST API 예제입니다. Spring Boot, Spring Security, Spring Data JPA,
H2 인메모리 데이터베이스를 사용합니다.

## 실행

```bash
./gradlew bootRun
```

기본 계정은 `demo` / `password` 입니다.

## 주요 API

- `POST /api/auth/register`: 회원가입
- `GET /api/auth/me`: 현재 로그인 사용자
- `GET /api/products`: 상품 목록
- `POST /api/cart/items`: 장바구니 담기
- `GET /api/cart`: 장바구니 조회
- `POST /api/orders`: 체크아웃
- `GET /api/orders`: 주문 내역

로그인은 Spring Security 기본 form login 또는 HTTP Basic을 사용할 수 있습니다.
H2 콘솔은 `/h2-console`에서 확인할 수 있습니다.
