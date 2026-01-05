# 인수인계 분석 시스템 문서

## 개요

스마트A 분개장 데이터를 분석하여 **요약.json / 요약.xlsx**를 생성하는 시스템입니다.

---

## 워크플로우

```
[입력]                          [처리]                         [출력]
jsons/{company}/          →   handover_analysis.py    →    output/{company}/
├── 분개장.json                                              ├── 요약.xlsx
├── 손익계산서.json                                          ├── 요약.json
├── 회사등록_기본사항.json                                   ├── 인수인계_분석_YYYY_vXX.xlsx
├── 신용카드자동전표.json                                    └── 거래처별_증빙유형_*.xlsx
└── 매입매출전표입력.json
```

---

## 실행 방법

```bash
# 기본 실행
uv run python phase1/analysis/handover_analysis.py {company} {year}

# 예시
uv run python phase1/analysis/handover_analysis.py thej 2024
uv run python phase1/analysis/handover_analysis.py corp 2024
uv run python phase1/analysis/handover_analysis.py lucky 2024
```

---

## 출력 파일 설명

| 파일 | 내용 |
|------|------|
| `요약.xlsx` | 핵심 분석 결과 (9개 시트) |
| `요약.json` | 동일 내용 JSON 형식 |
| `인수인계_분석_*.xlsx` | 버전별 상세 분석 |
| `거래처별_증빙유형_*.xlsx` | 거래처별 전표 분석 |

---

## 요약.json 구조

```json
{
  "company_profile": {
    "회사명": "...",
    "업종": "...",
    "회사유형": "신용카드형/은행자동이체형/세금계산서형"
  },
  "income_verification": {
    "매출액": {"손익계산서": N, "분개장": N},
    "매출원가": {...},
    "판관비": {...},
    "영업외수익": {...},
    "영업외비용": {...}
  },
  "monthly_pl": {
    "1": {"매출액": N, "매출원가": N, ...},
    "2": {...},
    ...
  }
}
```

---

## 관련 문서

| 문서 | 설명 |
|------|------|
| [INPUT_SPEC.md](./INPUT_SPEC.md) | 입력 데이터 스펙 |
| [OUTPUT_SPEC.md](./OUTPUT_SPEC.md) | 출력 데이터 스펙 |
| [CODE_REFERENCE.md](./CODE_REFERENCE.md) | 코드표 레퍼런스 |
