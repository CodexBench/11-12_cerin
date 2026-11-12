# Week 4 파일럿 결과

- Experiment: `week4-when-what-pilot-1x8`
- 실행: `8/8`
- 완료 matrix: `False`
- 과금 경로: `chatgpt_subscription`
- 금전 비용: `N/A` — Monetary cost is N/A because ChatGPT subscription usage is not equivalent to API token pricing.

## 조건별 집계

| 조건 | 실행 | 완료 | Resolved | 성공률 | 평균 시간(초) | 평균 effective tokens |
|---|---:|---:|---:|---:|---:|---:|
| full_off | 1 | 1 | 1 | 1.0 | 184.366 | 37066.0 |
| full_on | 1 | 0 | 0 | None | 201.167 | 59535.0 |
| partial_off | 1 | 1 | 1 | 1.0 | 211.437 | 34514.0 |
| partial_on | 1 | 1 | 1 | 1.0 | 121.569 | 27389.0 |
| sparse_off | 1 | 0 | 0 | None | 187.135 | 55328.0 |
| sparse_on | 1 | 1 | 1 | 1.0 | 146.683 | 46227.0 |
| what_repo | 1 | 1 | 1 | 1.0 | 134.903 | 32417.0 |
| what_test | 1 | 1 | 1 | 1.0 | 151.99 | 43921.0 |

## 실행별 결과

| Task | 조건 | 결과 | Resolved | 시간(초) | effective tokens |
|---|---|---|---:|---:|---:|
| sympy__sympy-20590 | full_off | normal_success | True | 184.366 | 37066 |
| sympy__sympy-20590 | full_on | budget_exceeded | None | 201.167 | 59535 |
| sympy__sympy-20590 | partial_off | normal_success | True | 211.437 | 34514 |
| sympy__sympy-20590 | partial_on | normal_success | True | 121.569 | 27389 |
| sympy__sympy-20590 | sparse_off | budget_exceeded | None | 187.135 | 55328 |
| sympy__sympy-20590 | sparse_on | normal_success | True | 146.683 | 46227 |
| sympy__sympy-20590 | what_repo | normal_success | True | 134.903 | 32417 |
| sympy__sympy-20590 | what_test | normal_success | True | 151.99 | 43921 |
