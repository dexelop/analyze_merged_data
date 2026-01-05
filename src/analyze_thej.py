"""
더제이의원 분석 스크립트
- 기본 피벗, 거래처별, 증빙유형별, 월별 추이, 카드 현황 분석
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "input_merged_datas" / "example" / "result_2024_v01_20260105_155001.json"
OUTPUT_DIR = BASE_DIR / "output" / "example"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. 데이터 로드
print("1. 데이터 로드 중...")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    raw = json.load(f)

df = pd.DataFrame(raw['data'])
print(f"   총 {len(df)}건 로드 완료")

# 2. 파생 컬럼 생성
print("2. 파생 컬럼 생성 중...")

# is_vat: vat(86,87,88,89) vs 일반(나머지)
def get_is_vat(ev_type):
    if ev_type in [86, 87, 88, 89]:
        return "vat"
    return "일반"

df['is_vat'] = df['증빙유형'].apply(get_is_vat)

# 데이터소스 + is_vat 조합
def get_source_type(row):
    if row['데이터소스'] == '카드미반영':
        return '카드미반영'
    return f"분개장({row['is_vat']})"

df['소스유형'] = df.apply(get_source_type, axis=1)

# 요일 (회계일자에서 추출)
df['회계일자_dt'] = pd.to_datetime(df['회계일자'], format='%Y%m%d', errors='coerce')
df['요일'] = df['회계일자_dt'].dt.dayofweek  # 0=월, 6=일
df['요일명'] = df['요일'].map({0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'})

print(f"   파생 컬럼 생성 완료")

# 3. 기본 피벗 분석
print("3. 기본 피벗 분석 중...")

# 정렬순서 × 손익분류 × 계정과목 × 소스유형
pivot_basic = df.pivot_table(
    index=['정렬순서', '손익분류', '계정과목'],
    columns='소스유형',
    values='순액',
    aggfunc='sum',
    fill_value=0
)

# 열 순서 정리
col_order = ['분개장(vat)', '분개장(일반)', '카드미반영']
pivot_basic = pivot_basic.reindex(columns=[c for c in col_order if c in pivot_basic.columns], fill_value=0)

# 총합계 먼저 계산 (분개장요약 추가 전에)
pivot_basic['총합계'] = pivot_basic.sum(axis=1)

# 분개장 요약 컬럼 추가
if '분개장(vat)' in pivot_basic.columns and '분개장(일반)' in pivot_basic.columns:
    pivot_basic['분개장요약'] = pivot_basic['분개장(vat)'] + pivot_basic['분개장(일반)']
elif '분개장(vat)' in pivot_basic.columns:
    pivot_basic['분개장요약'] = pivot_basic['분개장(vat)']
elif '분개장(일반)' in pivot_basic.columns:
    pivot_basic['분개장요약'] = pivot_basic['분개장(일반)']

# 정렬순서로 정렬
pivot_basic = pivot_basic.sort_index(level=0)

print(f"   기본 피벗: {len(pivot_basic)}행")

# 4. 거래처별 분석 (판관비 중심)
print("4. 거래처별 분석 중...")

df_pangwan = df[df['손익분류'] == '판관비'].copy()

trade_analysis = df_pangwan.groupby(['계정과목', '거래처명', '월']).agg({
    '순액': ['sum', 'count']
}).reset_index()
trade_analysis.columns = ['계정과목', '거래처명', '월', '금액', '건수']

# 계정과목별 거래처 TOP 10
trade_top = df_pangwan.groupby(['계정과목', '거래처명'])['순액'].sum().reset_index()
trade_top = trade_top.sort_values(['계정과목', '순액'], ascending=[True, False])

# 계정과목별 TOP 10만 추출 (rank 사용)
trade_top['rank'] = trade_top.groupby('계정과목')['순액'].rank(method='first', ascending=False)
trade_top10 = trade_top[trade_top['rank'] <= 10].drop(columns=['rank'])

print(f"   거래처 분석: {len(trade_top10)}건 (TOP 10 per 계정)")

# 5. 증빙유형별 분석
print("5. 증빙유형별 분석 중...")

# 증빙유형 코드 → 이름 매핑
evidence_names = {
    0: '수기',
    1: '현금조정',
    5: '결산분개',
    40: '원천세',
    86: '세금계산서',
    87: '영세율',
    88: '카드',
    88.5: '카드미반영',
    89: '현금영수증',
    90: '통장자동'
}

df['증빙유형명'] = df['증빙유형'].map(evidence_names).fillna(df['증빙유형'].astype(str))

evidence_analysis = df.pivot_table(
    index=['손익분류', '계정과목'],
    columns='증빙유형명',
    values='순액',
    aggfunc='sum',
    fill_value=0
)

evidence_analysis['합계'] = evidence_analysis.sum(axis=1)

# 증빙률 계산 (세금계산서+카드+현금영수증 / 전체)
vat_cols = ['세금계산서', '카드', '현금영수증']
evidence_analysis['증빙금액'] = evidence_analysis[[c for c in vat_cols if c in evidence_analysis.columns]].sum(axis=1)
evidence_analysis['증빙률'] = (evidence_analysis['증빙금액'] / evidence_analysis['합계'].replace(0, 1) * 100).round(1)

print(f"   증빙유형 분석: {len(evidence_analysis)}행")

# 6. 월별 추이 분석
print("6. 월별 추이 분석 중...")

monthly_trend = df.pivot_table(
    index='손익분류',
    columns='월',
    values='순액',
    aggfunc='sum',
    fill_value=0
)

monthly_trend['합계'] = monthly_trend.sum(axis=1)
monthly_trend['평균'] = monthly_trend.iloc[:, :-1].mean(axis=1).round(0)

# 정렬순서 기준으로 정렬
sort_order = df.groupby('손익분류')['정렬순서'].first().sort_values()
monthly_trend = monthly_trend.reindex(sort_order.index)

print(f"   월별 추이: {len(monthly_trend)}행")

# 7. 카드 현황 분석
print("7. 카드 현황 분석 중...")

df_card = df[df['증빙유형'].isin([88, 88.5])].copy()

if len(df_card) > 0:
    # 전표상태 정리
    df_card['전표상태'] = df_card['전표상태'].fillna('없음')
    df_card['공제구분'] = df_card['공제구분'].fillna('없음')

    card_status = df_card.pivot_table(
        index='계정과목',
        columns=['공제구분', '전표상태'],
        values='순액',
        aggfunc='sum',
        fill_value=0
    )

    print(f"   카드 현황: {len(card_status)}행")
else:
    card_status = pd.DataFrame()
    print("   카드 데이터 없음")

# 8. 카드미반영 상세
print("8. 카드미반영 상세 분석 중...")

df_card_missing = df[df['증빙유형'] == 88.5].copy()

if len(df_card_missing) > 0:
    card_missing_detail = df_card_missing[['회계일자', '거래처명', '순액', '공제구분', '전표상태', '계정과목']].copy()
    card_missing_detail = card_missing_detail.sort_values('회계일자')
    print(f"   카드미반영: {len(card_missing_detail)}건, 총 {card_missing_detail['순액'].sum():,.0f}원")
else:
    card_missing_detail = pd.DataFrame()
    print("   카드미반영 없음")

# 9. Excel 출력
print("9. Excel 출력 중...")

excel_path = OUTPUT_DIR / "분석결과.xlsx"

with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    # 기본 피벗
    pivot_basic.to_excel(writer, sheet_name='기본피벗')

    # 월별 추이
    monthly_trend.to_excel(writer, sheet_name='월별추이')

    # 거래처 TOP 10
    trade_top10.to_excel(writer, sheet_name='거래처TOP', index=False)

    # 증빙유형별
    evidence_analysis.to_excel(writer, sheet_name='증빙유형별')

    # 카드 현황
    if len(card_status) > 0:
        card_status.to_excel(writer, sheet_name='카드현황')

    # 카드미반영 상세
    if len(card_missing_detail) > 0:
        card_missing_detail.to_excel(writer, sheet_name='카드미반영', index=False)

print(f"   Excel 저장: {excel_path}")

# 10. JSON 출력
print("10. JSON 출력 중...")

# JSON 직렬화를 위한 변환
def df_to_dict(df):
    """DataFrame을 JSON 직렬화 가능한 dict로 변환"""
    result = df.copy()
    # MultiIndex 처리
    if isinstance(result.index, pd.MultiIndex):
        result = result.reset_index()
    # int64/float64 -> Python native
    for col in result.columns:
        if result[col].dtype in ['int64', 'float64']:
            result[col] = result[col].apply(lambda x: int(x) if pd.notna(x) and x == int(x) else float(x) if pd.notna(x) else None)
    return result.to_dict(orient='records')

json_output = {
    "meta": {
        "회사명": "example",
        "기간": "2024",
        "총건수": len(df),
        "생성일시": datetime.now().isoformat()
    },
    "기본피벗": df_to_dict(pivot_basic.reset_index()),
    "월별추이": df_to_dict(monthly_trend.reset_index()),
    "거래처TOP": df_to_dict(trade_top10),
    "증빙유형별": df_to_dict(evidence_analysis.reset_index()),
    "카드미반영": df_to_dict(card_missing_detail) if len(card_missing_detail) > 0 else []
}

json_path = OUTPUT_DIR / "분석결과.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(json_output, f, ensure_ascii=False, indent=2)

print(f"   JSON 저장: {json_path}")

# 11. 요약 출력
print("\n" + "="*60)
print("분석 완료!")
print("="*60)

print(f"\n[데이터 요약]")
print(f"  - 총 건수: {len(df):,}건")
print(f"  - 기간: 2024년 {df['월'].min()}월 ~ {df['월'].max()}월")

print(f"\n[손익 요약]")
for idx, row in monthly_trend.iterrows():
    print(f"  - {idx}: {row['합계']:,.0f}원")

print(f"\n[출력 파일]")
print(f"  - Excel: {excel_path}")
print(f"  - JSON: {json_path}")
