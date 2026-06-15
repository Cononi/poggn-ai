# Engineering Quality Gate

## Blocking Issues

- business rule이 controller, UI, config, script에 흩어져 있습니다.
- public API가 persistence entity나 internal enum을 노출합니다.
- authorization, ownership, tenant boundary가 없습니다.
- list/detail serialization에 N+1 또는 lazy loading 위험이 있습니다.
- multi-step write에 transaction boundary가 없습니다.
- test/build/security 실패 또는 미실행 사유가 없습니다.
- 파일이 200줄, frontend component가 160줄을 넘고 분리 이유가 없습니다.
- validation, mapping, business rule이 반복됩니다.

## Done

quality lane은 pass/fail, file/line, command evidence, follow-up TASK를 남깁니다.
