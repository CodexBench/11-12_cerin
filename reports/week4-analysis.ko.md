# Week 4 WHEN·WHAT 파일럿 분석

- 실행 저장: `8/8`
- 비공개 평가 완료: `6`
- 평가 완료 run 중 resolved: `6/6`
- Token budget 초과: `2`
- 표본: 1 task × 1 repetition — 연구 결론이 아닌 시스템 파일럿

## WHEN

| 문서 수준 | OFF 결과 | OFF tokens | ON 결과 | ON tokens |
|---|---|---:|---|---:|
| full | normal_success | 37066 | budget_exceeded | 59535 |
| partial | normal_success | 34514 | normal_success | 27389 |
| sparse | budget_exceeded | 55328 | normal_success | 46227 |

## WHAT

| 지침 정보 | 결과 | Resolved | 시간(초) | Effective tokens | 명령/테스트 명령 |
|---|---|---:|---:|---:|---:|
| none | normal_success | True | 184.366 | 37066 | 11/3 |
| repo | normal_success | True | 134.903 | 32417 | 10/6 |
| test | normal_success | True | 151.990 | 43921 | 12/6 |
| combined | budget_exceeded | None | 201.167 | 59535 | 20/7 |

## 실패 사례

### full_on

- 분류: `budget_exceeded`
- Effective tokens: `59535` / `50000`
- 원인: `BudgetExceededError: token budget exceeded: 59535 > 50000`
- 해석: Codex process는 정상 종료했지만 budget gate가 evaluator 실행 전에 fail-closed 처리함.

### sparse_off

- 분류: `budget_exceeded`
- Effective tokens: `55328` / `50000`
- 원인: `BudgetExceededError: token budget exceeded: 55328 > 50000`
- 해석: Codex process는 정상 종료했지만 budget gate가 evaluator 실행 전에 fail-closed 처리함.

## 해석 제한

모든 evaluator 완료 run이 resolved됐지만, task 1개·반복 1회이므로 지침 효과를 주장할 수 없다. 특히 budget 초과 두 조건은 정확성 결과가 결측이며 unresolved로 세면 안 된다. 본 결과는 144회 본실험을 실행하기 전 조건 생성·로그 연결·예산 중단·실패 보존을 검증한 것이다.
