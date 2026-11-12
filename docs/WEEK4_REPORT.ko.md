# CodexBench Week 4 수행 보고서

## 1. 결론

Week 4의 핵심인 WHEN 6조건과 WHAT 4조건을 실행 가능한 manifest로 구현했고, 중복 조건을 공유한 8회 파일럿을 실제 Codex와 공식 SWE-bench Docker evaluator로 끝까지 실행했다. 8회 중 6회는 비공개 평가까지 완료되어 모두 resolved됐고, 2회는 50,000 effective-token 상한을 넘겨 평가 전에 안전하게 중단됐다.

12 tasks × 6 WHEN conditions × 2 repetitions의 **144회 본실험 계획도 준비·고정**했다. 다만 144회 전체 실행은 최대 7.2M effective tokens와 장시간의 머신 점유가 가능한 작업이므로 이번 저장소 생성 과정에서 임의로 시작하지 않았다. CLI는 20회를 넘는 matrix에 `--confirm-large-matrix`를 요구한다.

## 2. 구현한 것

### 조건 생성

- WHEN: 문서 수준 `full/partial/sparse` × 추가 지침 `off/on`
- WHAT: `none/repo/test/combined`
- 숨긴 문서가 agent patch에 섞이지 않도록 patch 추출에서 제외
- 조건 metadata와 숨김 경로를 run ID digest에 포함

`partial`은 contribution/governance 진입 문서를 숨기고, `sparse`는 README와 `.github`까지 추가로 숨긴다. 이는 발견 가능한 문서량의 proxy이며 코드 주석·docstring 전체를 제거하지는 않는다.

### 실행 계획과 안전장치

- seed `1112`로 실행 순서를 결정적으로 셔플
- manifest의 최대 run 수·effective tokens·wall time 사전 검증
- 실행 중 누적 token·시간 상한 재검사
- 20회 초과 matrix에 명시적 확인 플래그 요구
- append-only event, Codex JSONL, stdout/stderr, patch, evaluator 결과, SQLite 저장
- `--resume` 시 최초 실행 시간을 보존하고 완료 단계만 재사용

### 분석

- 정확성: evaluator의 `resolved`
- 효율성: 실행 시간과 effective tokens
- 행동: 명령·실패 명령·테스트 명령·파일 변경·agent 메시지 수
- 실패: `budget_exceeded`를 일반 실패와 분리하고 evaluator 결측을 보존

## 3. 실제 파일럿 결과

대상은 `sympy__sympy-20590`, 8 unique conditions, 반복 1회다.

| 조건 | 문서/지침 | 결과 | Resolved | 시간(초) | Effective tokens |
|---|---|---|---:|---:|---:|
| `full_off` | full / none | normal_success | true | 184.366 | 37,066 |
| `full_on` | full / combined | budget_exceeded | 결측 | 201.167 | 59,535 |
| `partial_off` | partial / none | normal_success | true | 211.437 | 34,514 |
| `partial_on` | partial / combined | normal_success | true | 121.569 | 27,389 |
| `sparse_off` | sparse / none | budget_exceeded | 결측 | 187.135 | 55,328 |
| `sparse_on` | sparse / combined | normal_success | true | 146.683 | 46,227 |
| `what_repo` | full / repo | normal_success | true | 134.903 | 32,417 |
| `what_test` | full / test | normal_success | true | 151.990 | 43,921 |

집계:

- 저장된 run: 8/8
- 비공개 evaluator 완료: 6
- evaluator 완료 run의 resolved: 6/6
- budget 초과: 2
- 전체 시간: 1,339.250초(약 22.3분), 평균 167.406초
- 전체 effective tokens: 336,397, 평균 42,049.625
- 금액: ChatGPT 구독 실행이므로 실제 USD 비용 산정 불가

## 4. 오류와 처리

### `full_on`, `sparse_off` token budget 초과

두 Codex process는 exit code 0으로 종료했지만 각각 59,535와 55,328 effective tokens를 사용해 run 상한 50,000을 넘었다. 하네스는 이 상태에서 evaluator를 실행하지 않고 `budget_exceeded`로 fail-closed 처리했다. 따라서 두 결과는 패치가 틀렸다는 뜻의 unresolved가 아니라 **정확성 평가 결측**이다. agent trace와 stderr는 실패 분석을 위해 보존했다.

### arm64 Docker 환경

호스트는 arm64이고 공식 SWE-bench image는 `linux/amd64`였다. 기존에 받아 둔 공식 prebuilt image를 emulation으로 사용했다. 환경 검증은 통과했지만 Docker memory가 12GiB 권장치보다 낮다는 경고를 기록했다.

### 실행 파일 위치 변경

Codex Desktop 업데이트로 CLI 위치가 기본 PATH와 달라져 `CODEXBENCH_CODEX_CLI`로 현재 실행 파일의 절대 경로를 지정했다. SWE-bench CLI와 task 저장소도 같은 방식으로 명시했다.

## 5. 144회 본실험 준비 상태

`experiments/week4-when-main.yaml`에는 12개의 검증된 SymPy task, WHEN 6조건, 반복 2회가 들어 있다. 생성된 계획은 run ID가 모두 고유하고 총 144회다.

- 사전 상한: 144 runs
- effective-token 상한: 7,200,000
- wall-time 상한: 561,600초(156시간)
- 실행 명령에는 `--confirm-large-matrix` 필요

실행 전에는 나머지 공식 image를 받을 디스크 공간, Docker memory, 허용 token·시간을 다시 확인해야 한다. 이번 8회 평균을 단순 외삽하면 144회 agent 시간은 약 6.7시간이지만 image 준비와 evaluator 시간, task별 편차가 포함되지 않은 참고치다.

## 6. 해석 가능한 것과 없는 것

이번 결과로 확인한 것은 조건 생성, Codex trace 수집, patch 격리, 비공개 평가, 예산 중단, SQLite 저장, 재개, 분석이 한 흐름으로 동작한다는 점이다.

아직 “AGENTS.md가 어떤 조건에서 성능을 높인다”는 연구 결론을 낼 수는 없다. 이유는 task 1개·반복 1회이고, 두 조건의 평가값이 budget 때문에 결측이기 때문이다. 연구 질문에 답하려면 준비된 144회 WHEN 본실험을 반복 실행하고, task 단위 paired 분석과 신뢰구간을 계산해야 한다.

## 7. 주요 결과 파일

- `experiments/week4-pilot.yaml`: 실제 8회 파일럿
- `experiments/week4-when-main.yaml`: 144회 본실험
- `plans/week4-when-main-12x6x2.jsonl`: 고정 실행 순서
- `reports/week4-analysis.ko.md`: 자동 생성 WHEN·WHAT 표
- `reports/week4-summary.json`: 일반 집계
- `results/week4/`: 공개 가능한 실행·평가 아티팩트

## 8. 참고

OpenAI의 [Build AI coding agent evals with skills](https://developers.openai.com/blog/eval-skills)를 참고해 prompt, trace/artifacts, 결정적 검사, score를 분리하고 `codex exec --json` 이벤트를 보존했다.
