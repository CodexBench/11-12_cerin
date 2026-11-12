# 11-12_cerin — CodexBench Week 4

CodexBench의 핵심 질문인 **WHEN(언제 지침이 유용한가)** 과 **WHAT(어떤 지침이 유용한가)** 를 실행 가능한 조건으로 만들고, Codex 실행부터 비공개 SWE-bench 평가·결과 분석까지 연결한 Week 4 결과물입니다.

GitHub 저장소 이름에는 `/`를 사용할 수 없어 요청한 `11/12_cerin`을 `11-12_cerin`으로 표기합니다.

## 이번 주 결과

- WHEN 본실험: 12 tasks × 6 conditions × 2 repetitions = **144회 결정적 실행 계획**
- WHEN·WHAT 엔지니어링 파일럿: 1 task × 8 unique conditions × 1 repetition = **8회 실제 실행**
- 비공개 Docker 평가 완료: **6회**, 전부 resolved
- 실행 전 중단: **2회**, per-run 50,000 effective-token budget 초과
- 자동 테스트: Pydantic 검증, 계획·예산, 재개, 행동 지표와 실패 분류 포함

상세 결과와 제한은 [Week 4 보고서](docs/WEEK4_REPORT.ko.md), 자동 생성 표는 [WHEN·WHAT 분석](reports/week4-analysis.ko.md)에서 확인할 수 있습니다.

## 실험 조건

WHEN은 동일한 task·base commit·model·evaluator에서 저장소 문서 수준 `full/partial/sparse`와 추가 `AGENTS.md`의 `off/on`을 비교합니다. WHAT은 문서가 온전한 상태에서 `none/repo/test/combined` 지침을 비교합니다.

정확한 문서 제거 규칙과 한계는 [조건 명세](conditions/README.md)에 기록했습니다. `partial`과 `sparse`는 발견 가능한 저장소 안내를 단계적으로 숨기는 실용적 proxy이며, 모든 docstring까지 제거한 절대적인 무문서 상태는 아닙니다.

## 요구사항

- Python 3.11 이상
- Git, Docker Desktop
- 인증된 Codex CLI
- SWE-bench CLI와 `swe-bench-tasks`

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pip install swebench
git clone https://github.com/SWE-bench/swe-bench-tasks.git
```

도구 위치가 기본값과 다르면 절대 경로를 지정합니다.

```bash
export CODEXBENCH_CODEX_CLI=/absolute/path/to/codex
export CODEXBENCH_SWEBENCH_CLI=/absolute/path/to/swebench
export CODEXBENCH_TASK_REPO=/absolute/path/to/swe-bench-tasks
```

## 재현 명령

먼저 manifest와 Docker 환경을 검증하고 실행 계획을 만듭니다.

```bash
.venv/bin/codexbench validate experiments/week4-pilot.yaml --pull-images
.venv/bin/codexbench plan experiments/week4-pilot.yaml --output plans
.venv/bin/codexbench plan experiments/week4-when-main.yaml --output plans
```

8회 파일럿과 분석을 실행합니다.

```bash
.venv/bin/codexbench run-all experiments/week4-pilot.yaml --resume
.venv/bin/codexbench report experiments/week4-pilot.yaml --output reports
.venv/bin/codexbench analyze-week4 experiments/week4-pilot.yaml --output reports
```

144회 본실험은 비용과 시간을 확인한 뒤 명시적으로 승인해야 시작됩니다. 20회를 넘는 matrix는 실수로 실행되지 않도록 차단됩니다.

```bash
.venv/bin/codexbench run-all experiments/week4-when-main.yaml \
  --resume --confirm-large-matrix
```

## 주요 경로

```text
experiments/       파일럿·본실험 manifest
instructions/      repo/test/combined AGENTS.md
conditions/        조건 조작 규칙과 해석 한계
plans/             seed로 고정된 JSONL 실행 순서
reports/           자동 집계와 WHEN·WHAT 분석
results/week4/     공개 가능한 실제 실행 로그·평가 결과
codexbench/        runner, planner, evaluator, 저장·분석 코드
```

로컬 실행 중간물은 `runs/`에 저장되고 Git에서는 제외합니다. `results/week4/`에는 재현 검토에 필요한 아티팩트만 별도로 내보냅니다.

## 예산·재개·해석

각 run ID는 task·condition·repetition·명세 digest로 결정됩니다. `--resume`은 동일 run의 완료 단계를 재사용하며 조건 간 대화는 공유하지 않습니다. per-run 및 전체 matrix의 token·wall-time 상한을 넘으면 fail-closed로 중단합니다.

이번 실행은 ChatGPT 구독 인증을 사용했으므로 API 가격을 곱한 달러 비용은 실제 청구액이 아닙니다. 따라서 USD 비용은 `null`로 두고 시간과 token 사용량을 기록했습니다.

파일럿은 task 1개·반복 1회이므로 지침의 인과 효과에 대한 연구 결론이 아닙니다. 특히 budget 초과 두 run은 평가 결과가 없는 결측값이며 unresolved로 간주하지 않습니다.

## 테스트

```bash
.venv/bin/pytest
```

Codex eval 설계는 OpenAI의 [Build AI coding agent evals with skills](https://developers.openai.com/blog/eval-skills)에서 제안한 `prompt → trace/artifacts → deterministic checks → score` 구조와 `codex exec --json` 이벤트 수집 방식을 참고했습니다.
