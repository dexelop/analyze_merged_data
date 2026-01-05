# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
new_docs 폴더에 있는것은 참고용으로 사용하고 그 폴더는 수정하거나 삭제 하지 말 것. 


## Project Overview

**Handover Analysis System (인수인계 분석 시스템)** - A financial data analysis tool that:
- Merges journal entry data from WEHAGO SmartA accounting software with purchase/sales slips and credit card transactions
- Generates comprehensive financial summaries in JSON and XLSX formats
- Provides daily P&L analysis and handover documentation for accounting teams

## Commands

```bash
# Execute analysis script
uv run python {script_path} {company} {year}

# Examples
uv run python phase1/analysis/handover_analysis.py thej 2024
uv run python new_code/daily_journal.py corp 2024
```

## Architecture

### Data Flow
```
Input (5 JSON types per company)
    ↓
Preprocessing (Filter exclusions)
    ↓
Account Classification (PL vs BS by key_gr)
    ↓
Inventory Conversion (14x→45101, 15x→45501)
    ↓
Matching Engine (Date + Counterparty + Amount)
    ↓
Aggregation (Monthly, by Counterparty)
    ↓
Output (요약.json + 요약.xlsx + daily details)
```

### Directory Structure
- `input_merged_datas/` - Input data per company (JSON/XLSX pairs)
- `new_docs/` - Complete documentation suite

### Input Files (per company)
- `*_분개장.json` - Journal entries (General Ledger)
- `*_손익계산서.json` - Income Statement
- `*_회사등록_기본사항.json` - Company registration info
- `*_자동전표-신카-국세청.json` - Credit card auto-journals
- `*_매입매출전표입력.json` - Purchase/sales slip input

### Output Files
- `요약.xlsx` / `요약.json` - Core analysis (9 sheets)
- `인수인계_분석_YYYY_vXX.xlsx` - Versioned analysis
- `거래처별_증빙유형_*.xlsx` - Counterparty detail analysis

## Core Business Logic

### Preprocessing Exclusions
- `no_exter2=7`: 잉여금관련전표 (Retained earnings)
- `no_exter2=27`: 손익대체분개 (P&L reversal)
- `no_exter2=5` + 대변>0: 결산분개 재고대변 (Closing inventory credits)

### P&L Classification (key_gr values)
- 14: Sales/Revenue (매출)
- 19: SG&A (판관비)
- 20: Non-operating income (영업외수익)
- 21: Non-operating expense (영업외비용)

### Inventory-to-COGS Mapping
| Inventory Account | COGS Account |
|-------------------|--------------|
| 146xx | 45101 |
| 150xx | 45501 |
| 153xx | 45001 |
| 156xx | 45201 |
| 159xx | 45301 |

### Net Amount Calculation
- Revenue accounts: `credit - debit`
- Expense accounts: `debit - credit`

### Company Type Detection
- Bank auto-transfer ≥50% → 은행자동이체형
- Credit card ≥35% → 신용카드형
- Tax invoice ≥30% → 세금계산서형

## Key Code Tables

### Evidence Types (no_exter2)
- 0: Manual entry
- 5: Period-end closing
- 86: Tax invoice (세금계산서)
- 88: Credit card (신용카드)
- 89: Cash receipt (현금영수증)
- 90: Bank auto-journal

### Journal Status (ty_jungstat)
- 1: Confirmable
- 2: Confirmed
- 3: Excluded
- 4: Duplicate
- 5: Not recommended
- 6: Deleted

## Documentation Reference

All specifications are in `new_docs/`:
- `INPUT_SPEC.md` - Input data specification
- `OUTPUT_SPEC.md` - Output data specification
- `CODE_REFERENCE.md` - Complete code tables
- `COLUMN_SPEC.md` - Column definitions (★★★ = critical)
- `LOGIC_RULES.md` - Processing rules and order
- `병합지침서.md` - Merge instruction guide (Korean)
