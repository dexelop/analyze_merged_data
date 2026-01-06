# -*- coding: utf-8 -*-
"""
회계 데이터 인사이트 차트 생성 스크립트
30개 차트를 통한 데이터 시각화

전문가 에이전트:
- 🎨 디자인 전문가: 색상, 레이아웃
- 📊 차트 전문가: matplotlib/seaborn
- 📈 데이터분석 전문가: 통계적 인사이트
- 💰 회계 전문가: 재무제표 해석
- 🐼 pandas 전문가: 데이터 전처리
- ✅ 품질검수 전문가: 정확성, 한글 인코딩
"""

import json
import warnings
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
import numpy as np

warnings.filterwarnings('ignore')

# ============================================================
# 한글 폰트 설정 (디자인 전문가)
# ============================================================
def setup_korean_font():
    """한글 폰트 설정"""
    # Windows 기본 한글 폰트
    font_candidates = [
        'Malgun Gothic',
        'NanumGothic',
        'NanumBarunGothic',
        'AppleGothic',
        'Gulim'
    ]

    available_fonts = [f.name for f in fm.fontManager.ttflist]

    for font in font_candidates:
        if font in available_fonts:
            plt.rcParams['font.family'] = font
            plt.rcParams['axes.unicode_minus'] = False
            print(f"   폰트 설정: {font}")
            return font

    # 폰트를 찾지 못한 경우
    print("   경고: 한글 폰트를 찾지 못했습니다.")
    return None

# ============================================================
# 컬러 팔레트 (디자인 전문가)
# ============================================================
COLORS = {
    'primary': '#2E86AB',      # 파랑
    'secondary': '#A23B72',    # 자주
    'success': '#28A745',      # 초록
    'warning': '#F18F01',      # 주황
    'danger': '#C73E1D',       # 빨강
    'info': '#17A2B8',         # 청록
    'light': '#F8F9FA',        # 밝은 회색
    'dark': '#343A40',         # 어두운 회색
}

# 손익분류별 색상
PL_COLORS = {
    '매출': '#2E86AB',
    '매출원가': '#A23B72',
    '판관비': '#F18F01',
    '영업외수익': '#28A745',
    '영업외비용': '#C73E1D',
    '고정자산': '#6C757D',
    '유동고정자산-기타': '#17A2B8',
    '유동부채': '#E83E8C',
    '자본': '#6610F2',
    '카드미반영': '#FD7E14',
}

# 증빙유형별 색상
EVIDENCE_COLORS = {
    0: '#6C757D',    # 수기
    1: '#17A2B8',    # 현금조정
    5: '#6610F2',    # 결산분개
    40: '#E83E8C',   # 원천세
    86: '#2E86AB',   # 세금계산서
    87: '#28A745',   # 영세율
    88: '#F18F01',   # 카드
    88.5: '#C73E1D', # 카드미반영
    89: '#A23B72',   # 현금영수증
    90: '#343A40',   # 통장자동
}

EVIDENCE_NAMES = {
    0: '수기', 1: '현금조정', 5: '결산분개', 40: '원천세',
    86: '세금계산서', 87: '영세율', 88: '카드', 88.5: '카드미반영',
    89: '현금영수증', 90: '통장자동'
}

# ============================================================
# 데이터 로드 (pandas 전문가)
# ============================================================
def load_data(json_path: Path) -> pd.DataFrame:
    """JSON 데이터 로드 및 전처리"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data['data'])

    # 기본 전처리
    df['월'] = df['월'].astype(int)
    df['회계일자'] = pd.to_datetime(df['회계일자'], format='%Y%m%d', errors='coerce')
    df['요일'] = df['회계일자'].dt.dayofweek
    df['요일명'] = df['요일'].map({0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'})

    # 증빙유형명
    df['증빙유형명'] = df['증빙유형'].map(EVIDENCE_NAMES).fillna('기타')

    # 거래처명 정리
    df['거래처명_filled'] = df['거래처명'].fillna('(미지정)')

    # 소스유형 (전표번호 기준)
    def get_source_type(row):
        if row['데이터소스'] == '카드미반영':
            return '카드미반영'
        try:
            slip_no = int(row['전표번호']) if row['전표번호'] else 0
        except:
            slip_no = 0
        return '분개장(vat)' if slip_no >= 50000 else '분개장(일반)'

    df['소스유형'] = df.apply(get_source_type, axis=1)

    return df

# ============================================================
# 금액 포맷터 (디자인 전문가)
# ============================================================
def format_krw(value, pos=None):
    """금액을 한국 원화 형식으로 포맷"""
    if abs(value) >= 1e8:
        return f'{value/1e8:.1f}억'
    elif abs(value) >= 1e4:
        return f'{value/1e4:.0f}만'
    else:
        return f'{value:,.0f}'

def format_krw_full(value):
    """금액 전체 표시"""
    return f'{value:,.0f}원'

# ============================================================
# 차트 생성 함수들 (차트 전문가 + 데이터분석 전문가 + 회계 전문가)
# ============================================================

class ChartGenerator:
    """차트 생성 클래스"""

    def __init__(self, df: pd.DataFrame, output_dir: Path):
        self.df = df
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chart_count = 0

    def save_chart(self, fig, name: str):
        """차트 저장"""
        self.chart_count += 1
        filename = f"{self.chart_count:02d}_{name}.png"
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"   [{self.chart_count:02d}] {name}")
        return filepath

    # ========== 1. 수익/비용 분석 (회계 전문가) ==========

    def chart_01_pl_overview(self):
        """손익분류별 총액 개요"""
        fig, ax = plt.subplots(figsize=(12, 6))

        data = self.df.groupby('손익분류')['순액'].sum().sort_values(ascending=True)
        colors = [PL_COLORS.get(x, COLORS['primary']) for x in data.index]

        bars = ax.barh(data.index, data.values, color=colors)
        ax.set_xlabel('금액')
        ax.set_title('손익분류별 총액 현황', fontsize=14, fontweight='bold')
        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_krw))

        # 값 표시
        for bar, val in zip(bars, data.values):
            ax.text(val + max(data.values)*0.01, bar.get_y() + bar.get_height()/2,
                   format_krw_full(val), va='center', fontsize=9)

        plt.tight_layout()
        return self.save_chart(fig, '손익분류별_총액')

    def chart_02_revenue_vs_cost(self):
        """매출 vs 비용 비교"""
        fig, ax = plt.subplots(figsize=(10, 6))

        revenue = self.df[self.df['손익분류'] == '매출']['순액'].sum()
        cost = self.df[self.df['손익분류'] == '매출원가']['순액'].sum()
        expense = self.df[self.df['손익분류'] == '판관비']['순액'].sum()

        categories = ['매출', '매출원가', '판관비']
        values = [revenue, cost, expense]
        colors = [PL_COLORS['매출'], PL_COLORS['매출원가'], PL_COLORS['판관비']]

        bars = ax.bar(categories, values, color=colors)
        ax.set_ylabel('금액')
        ax.set_title('매출 vs 원가 vs 판관비', fontsize=14, fontweight='bold')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_krw))

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, val + max(values)*0.02,
                   format_krw_full(val), ha='center', fontsize=10)

        # 매출총이익, 영업이익 라인
        gross_profit = revenue - cost
        operating_profit = gross_profit - expense
        ax.axhline(y=gross_profit, color='green', linestyle='--', label=f'매출총이익: {format_krw_full(gross_profit)}')
        ax.axhline(y=operating_profit, color='blue', linestyle='--', label=f'영업이익: {format_krw_full(operating_profit)}')
        ax.legend()

        plt.tight_layout()
        return self.save_chart(fig, '매출_원가_판관비_비교')

    def chart_03_expense_breakdown(self):
        """판관비 세부 항목 (도넛 차트)"""
        fig, ax = plt.subplots(figsize=(10, 8))

        expense_df = self.df[self.df['손익분류'] == '판관비']
        data = expense_df.groupby('계정과목')['순액'].sum().sort_values(ascending=False)

        # 상위 10개 + 기타
        top10 = data.head(10)
        if len(data) > 10:
            others = data[10:].sum()
            top10['기타'] = others

        colors = sns.color_palette('husl', len(top10))
        wedges, texts, autotexts = ax.pie(top10.values, labels=top10.index, autopct='%1.1f%%',
                                          colors=colors, pctdistance=0.75)

        # 도넛 형태
        centre_circle = plt.Circle((0, 0), 0.50, fc='white')
        ax.add_patch(centre_circle)

        ax.set_title('판관비 구성 (상위 10개 항목)', fontsize=14, fontweight='bold')

        # 중앙에 총액 표시
        total = expense_df['순액'].sum()
        ax.text(0, 0, f'총 판관비\n{format_krw_full(total)}', ha='center', va='center', fontsize=11)

        plt.tight_layout()
        return self.save_chart(fig, '판관비_구성_도넛')

    def chart_04_cost_structure(self):
        """매출원가 구조"""
        fig, ax = plt.subplots(figsize=(10, 6))

        cost_df = self.df[self.df['손익분류'] == '매출원가']
        data = cost_df.groupby('계정과목')['순액'].sum().sort_values(ascending=False)

        colors = sns.color_palette('Reds_r', len(data))
        bars = ax.barh(data.index, data.values, color=colors)
        ax.set_xlabel('금액')
        ax.set_title('매출원가 항목별 현황', fontsize=14, fontweight='bold')
        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax.invert_yaxis()

        for bar, val in zip(bars, data.values):
            ax.text(val + max(data.values)*0.01, bar.get_y() + bar.get_height()/2,
                   format_krw_full(val), va='center', fontsize=9)

        plt.tight_layout()
        return self.save_chart(fig, '매출원가_항목별')

    def chart_05_profit_margin(self):
        """월별 이익률 추이"""
        fig, ax = plt.subplots(figsize=(12, 6))

        monthly = self.df.groupby(['월', '손익분류'])['순액'].sum().unstack(fill_value=0)

        revenue = monthly.get('매출', pd.Series([0]*12))
        cost = monthly.get('매출원가', pd.Series([0]*12))
        expense = monthly.get('판관비', pd.Series([0]*12))

        gross_margin = ((revenue - cost) / revenue * 100).fillna(0)
        operating_margin = ((revenue - cost - expense) / revenue * 100).fillna(0)

        months = range(1, 13)
        ax.plot(months, gross_margin.reindex(months, fill_value=0),
                marker='o', label='매출총이익률', color=COLORS['success'], linewidth=2)
        ax.plot(months, operating_margin.reindex(months, fill_value=0),
                marker='s', label='영업이익률', color=COLORS['primary'], linewidth=2)

        ax.set_xlabel('월')
        ax.set_ylabel('이익률 (%)')
        ax.set_title('월별 이익률 추이', fontsize=14, fontweight='bold')
        ax.set_xticks(months)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return self.save_chart(fig, '월별_이익률_추이')

    # ========== 2. 월별 추이 분석 (데이터분석 전문가) ==========

    def chart_06_monthly_trend(self):
        """월별 매출/비용 추이"""
        fig, ax = plt.subplots(figsize=(14, 6))

        monthly = self.df.groupby(['월', '손익분류'])['순액'].sum().unstack(fill_value=0)

        x = np.arange(1, 13)
        width = 0.25

        if '매출' in monthly.columns:
            ax.bar(x - width, monthly['매출'].reindex(x, fill_value=0), width,
                   label='매출', color=PL_COLORS['매출'])
        if '매출원가' in monthly.columns:
            ax.bar(x, monthly['매출원가'].reindex(x, fill_value=0), width,
                   label='매출원가', color=PL_COLORS['매출원가'])
        if '판관비' in monthly.columns:
            ax.bar(x + width, monthly['판관비'].reindex(x, fill_value=0), width,
                   label='판관비', color=PL_COLORS['판관비'])

        ax.set_xlabel('월')
        ax.set_ylabel('금액')
        ax.set_title('월별 매출/원가/판관비 추이', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([f'{m}월' for m in x])
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        return self.save_chart(fig, '월별_매출원가판관비_추이')

    def chart_07_monthly_revenue(self):
        """월별 매출 상세"""
        fig, ax = plt.subplots(figsize=(12, 6))

        revenue_df = self.df[self.df['손익분류'] == '매출']
        monthly = revenue_df.groupby(['월', '계정과목'])['순액'].sum().unstack(fill_value=0)

        monthly.plot(kind='bar', stacked=True, ax=ax, colormap='Blues')

        ax.set_xlabel('월')
        ax.set_ylabel('금액')
        ax.set_title('월별 매출 구성', fontsize=14, fontweight='bold')
        ax.set_xticklabels([f'{m}월' for m in monthly.index], rotation=0)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax.legend(title='계정과목', bbox_to_anchor=(1.02, 1), loc='upper left')

        plt.tight_layout()
        return self.save_chart(fig, '월별_매출_구성')

    def chart_08_monthly_expense(self):
        """월별 판관비 상세"""
        fig, ax = plt.subplots(figsize=(14, 6))

        expense_df = self.df[self.df['손익분류'] == '판관비']
        monthly = expense_df.groupby(['월', '계정과목'])['순액'].sum().unstack(fill_value=0)

        # 상위 5개 계정 + 기타
        top_accounts = monthly.sum().nlargest(5).index.tolist()
        monthly_top = monthly[top_accounts].copy()
        monthly_top['기타'] = monthly[[c for c in monthly.columns if c not in top_accounts]].sum(axis=1)

        monthly_top.plot(kind='bar', stacked=True, ax=ax, colormap='Oranges')

        ax.set_xlabel('월')
        ax.set_ylabel('금액')
        ax.set_title('월별 판관비 구성 (상위 5개 항목)', fontsize=14, fontweight='bold')
        ax.set_xticklabels([f'{m}월' for m in monthly_top.index], rotation=0)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax.legend(title='계정과목', bbox_to_anchor=(1.02, 1), loc='upper left')

        plt.tight_layout()
        return self.save_chart(fig, '월별_판관비_구성')

    def chart_09_monthly_transaction_count(self):
        """월별 거래 건수"""
        fig, ax = plt.subplots(figsize=(12, 6))

        monthly_count = self.df.groupby('월').size()

        bars = ax.bar(monthly_count.index, monthly_count.values, color=COLORS['info'])
        ax.set_xlabel('월')
        ax.set_ylabel('거래 건수')
        ax.set_title('월별 거래 건수', fontsize=14, fontweight='bold')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels([f'{m}월' for m in range(1, 13)])

        # 평균선
        avg = monthly_count.mean()
        ax.axhline(y=avg, color=COLORS['danger'], linestyle='--', label=f'평균: {avg:.0f}건')
        ax.legend()

        for bar, val in zip(bars, monthly_count.values):
            ax.text(bar.get_x() + bar.get_width()/2, val + 5, f'{val}', ha='center', fontsize=9)

        plt.tight_layout()
        return self.save_chart(fig, '월별_거래건수')

    def chart_10_monthly_avg_amount(self):
        """월별 평균 거래 금액"""
        fig, ax = plt.subplots(figsize=(12, 6))

        monthly_avg = self.df.groupby('월')['순액'].mean()

        ax.plot(monthly_avg.index, monthly_avg.values, marker='o',
                color=COLORS['primary'], linewidth=2, markersize=8)
        ax.fill_between(monthly_avg.index, monthly_avg.values, alpha=0.3, color=COLORS['primary'])

        ax.set_xlabel('월')
        ax.set_ylabel('평균 금액')
        ax.set_title('월별 평균 거래 금액', fontsize=14, fontweight='bold')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels([f'{m}월' for m in range(1, 13)])
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return self.save_chart(fig, '월별_평균거래금액')

    # ========== 3. 거래처 분석 (회계 전문가) ==========

    def chart_11_top_traders_expense(self):
        """판관비 거래처 TOP 10"""
        fig, ax = plt.subplots(figsize=(12, 7))

        expense_df = self.df[self.df['손익분류'] == '판관비']
        top_traders = expense_df.groupby('거래처명_filled')['순액'].sum().nlargest(10)

        colors = sns.color_palette('YlOrRd_r', len(top_traders))
        bars = ax.barh(top_traders.index, top_traders.values, color=colors)
        ax.set_xlabel('금액')
        ax.set_title('판관비 거래처 TOP 10', fontsize=14, fontweight='bold')
        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax.invert_yaxis()

        for bar, val in zip(bars, top_traders.values):
            ax.text(val + max(top_traders.values)*0.01, bar.get_y() + bar.get_height()/2,
                   format_krw_full(val), va='center', fontsize=9)

        plt.tight_layout()
        return self.save_chart(fig, '판관비_거래처_TOP10')

    def chart_12_top_traders_revenue(self):
        """매출 거래처 TOP 10"""
        fig, ax = plt.subplots(figsize=(12, 7))

        revenue_df = self.df[self.df['손익분류'] == '매출']
        top_traders = revenue_df.groupby('거래처명_filled')['순액'].sum().nlargest(10)

        colors = sns.color_palette('Blues_r', len(top_traders))
        bars = ax.barh(top_traders.index, top_traders.values, color=colors)
        ax.set_xlabel('금액')
        ax.set_title('매출 거래처 TOP 10', fontsize=14, fontweight='bold')
        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax.invert_yaxis()

        for bar, val in zip(bars, top_traders.values):
            ax.text(val + max(top_traders.values)*0.01, bar.get_y() + bar.get_height()/2,
                   format_krw_full(val), va='center', fontsize=9)

        plt.tight_layout()
        return self.save_chart(fig, '매출_거래처_TOP10')

    def chart_13_trader_concentration(self):
        """거래처 집중도 (파레토)"""
        fig, ax1 = plt.subplots(figsize=(14, 6))

        expense_df = self.df[self.df['손익분류'] == '판관비']
        trader_sum = expense_df.groupby('거래처명_filled')['순액'].sum().sort_values(ascending=False)

        # 상위 20개만
        top20 = trader_sum.head(20)
        cumsum = top20.cumsum() / trader_sum.sum() * 100

        ax1.bar(range(len(top20)), top20.values, color=COLORS['primary'], alpha=0.7)
        ax1.set_xlabel('거래처 (순위)')
        ax1.set_ylabel('금액', color=COLORS['primary'])
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax1.set_xticks(range(len(top20)))
        ax1.set_xticklabels(range(1, len(top20)+1))

        ax2 = ax1.twinx()
        ax2.plot(range(len(top20)), cumsum.values, color=COLORS['danger'],
                marker='o', linewidth=2, label='누적 비율')
        ax2.set_ylabel('누적 비율 (%)', color=COLORS['danger'])
        ax2.axhline(y=80, color=COLORS['warning'], linestyle='--', alpha=0.5)

        ax1.set_title('거래처 집중도 (파레토 분석)', fontsize=14, fontweight='bold')

        plt.tight_layout()
        return self.save_chart(fig, '거래처_집중도_파레토')

    def chart_14_trader_count_by_account(self):
        """계정과목별 거래처 수"""
        fig, ax = plt.subplots(figsize=(12, 8))

        expense_df = self.df[self.df['손익분류'] == '판관비']
        trader_count = expense_df.groupby('계정과목')['거래처명_filled'].nunique().sort_values(ascending=True)

        colors = sns.color_palette('viridis', len(trader_count))
        bars = ax.barh(trader_count.index, trader_count.values, color=colors)
        ax.set_xlabel('거래처 수')
        ax.set_title('계정과목별 거래처 수 (판관비)', fontsize=14, fontweight='bold')

        for bar, val in zip(bars, trader_count.values):
            ax.text(val + 0.3, bar.get_y() + bar.get_height()/2, f'{val}', va='center', fontsize=9)

        plt.tight_layout()
        return self.save_chart(fig, '계정과목별_거래처수')

    def chart_15_trader_monthly_pattern(self):
        """주요 거래처 월별 패턴"""
        fig, ax = plt.subplots(figsize=(14, 8))

        expense_df = self.df[self.df['손익분류'] == '판관비']
        top5_traders = expense_df.groupby('거래처명_filled')['순액'].sum().nlargest(5).index

        for trader in top5_traders:
            trader_data = expense_df[expense_df['거래처명_filled'] == trader]
            monthly = trader_data.groupby('월')['순액'].sum()
            ax.plot(monthly.index, monthly.values, marker='o', label=trader[:15], linewidth=2)

        ax.set_xlabel('월')
        ax.set_ylabel('금액')
        ax.set_title('주요 거래처 월별 지출 패턴 (TOP 5)', fontsize=14, fontweight='bold')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels([f'{m}월' for m in range(1, 13)])
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return self.save_chart(fig, '주요거래처_월별패턴')

    # ========== 4. 증빙유형별 분석 (회계 전문가) ==========

    def chart_16_evidence_type_overview(self):
        """증빙유형별 금액 현황"""
        fig, ax = plt.subplots(figsize=(12, 6))

        data = self.df.groupby('증빙유형명')['순액'].sum().sort_values(ascending=True)
        colors = [EVIDENCE_COLORS.get(k, COLORS['light']) for k in
                  self.df.groupby('증빙유형명')['증빙유형'].first().reindex(data.index)]

        bars = ax.barh(data.index, data.values, color=sns.color_palette('Set2', len(data)))
        ax.set_xlabel('금액')
        ax.set_title('증빙유형별 금액 현황', fontsize=14, fontweight='bold')
        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_krw))

        for bar, val in zip(bars, data.values):
            ax.text(val + max(abs(data.values))*0.01, bar.get_y() + bar.get_height()/2,
                   format_krw_full(val), va='center', fontsize=9)

        plt.tight_layout()
        return self.save_chart(fig, '증빙유형별_금액')

    def chart_17_evidence_type_count(self):
        """증빙유형별 거래 건수"""
        fig, ax = plt.subplots(figsize=(10, 6))

        data = self.df['증빙유형명'].value_counts()

        colors = sns.color_palette('Set2', len(data))
        wedges, texts, autotexts = ax.pie(data.values, labels=data.index, autopct='%1.1f%%',
                                          colors=colors)
        ax.set_title('증빙유형별 거래 건수 비율', fontsize=14, fontweight='bold')

        plt.tight_layout()
        return self.save_chart(fig, '증빙유형별_건수비율')

    def chart_18_evidence_by_pl(self):
        """손익분류별 증빙유형 분포"""
        fig, ax = plt.subplots(figsize=(14, 7))

        pivot = self.df.pivot_table(index='손익분류', columns='증빙유형명',
                                     values='순액', aggfunc='sum', fill_value=0)

        pivot.plot(kind='bar', stacked=True, ax=ax, colormap='tab20')

        ax.set_xlabel('손익분류')
        ax.set_ylabel('금액')
        ax.set_title('손익분류별 증빙유형 분포', fontsize=14, fontweight='bold')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax.legend(title='증빙유형', bbox_to_anchor=(1.02, 1), loc='upper left')

        plt.tight_layout()
        return self.save_chart(fig, '손익분류별_증빙유형')

    def chart_19_evidence_monthly(self):
        """월별 증빙유형 추이"""
        fig, ax = plt.subplots(figsize=(14, 6))

        pivot = self.df.pivot_table(index='월', columns='증빙유형명',
                                     values='순액', aggfunc='count', fill_value=0)

        pivot.plot(kind='line', marker='o', ax=ax, linewidth=2)

        ax.set_xlabel('월')
        ax.set_ylabel('거래 건수')
        ax.set_title('월별 증빙유형 거래 건수 추이', fontsize=14, fontweight='bold')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels([f'{m}월' for m in range(1, 13)])
        ax.legend(title='증빙유형', bbox_to_anchor=(1.02, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return self.save_chart(fig, '월별_증빙유형_추이')

    # ========== 5. 카드/현금 분석 (회계 전문가) ==========

    def chart_20_card_vs_cash(self):
        """카드 vs 현금 거래 비교"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # 금액 기준 (절대값 사용 - 파이차트는 음수 불가)
        card_amount = abs(self.df[self.df['증빙유형'] == 88]['순액'].sum())
        cash_amount = abs(self.df[self.df['증빙유형'] == 89]['순액'].sum())
        tax_amount = abs(self.df[self.df['증빙유형'] == 86]['순액'].sum())
        other_amount = abs(self.df[~self.df['증빙유형'].isin([88, 89, 86])]['순액'].sum())

        amounts = [card_amount, cash_amount, tax_amount, other_amount]
        labels = ['카드', '현금영수증', '세금계산서', '기타']
        colors = [COLORS['warning'], COLORS['success'], COLORS['primary'], COLORS['light']]

        # 0인 값 필터링
        non_zero = [(a, l, c) for a, l, c in zip(amounts, labels, colors) if a > 0]
        if non_zero:
            amounts_nz, labels_nz, colors_nz = zip(*non_zero)
            axes[0].pie(amounts_nz, labels=labels_nz, autopct='%1.1f%%', colors=colors_nz)
        axes[0].set_title('결제수단별 금액 비율', fontsize=12, fontweight='bold')

        # 건수 기준
        card_count = len(self.df[self.df['증빙유형'] == 88])
        cash_count = len(self.df[self.df['증빙유형'] == 89])
        tax_count = len(self.df[self.df['증빙유형'] == 86])
        other_count = len(self.df[~self.df['증빙유형'].isin([88, 89, 86])])

        counts = [card_count, cash_count, tax_count, other_count]
        # 0인 값 필터링
        non_zero_cnt = [(c, l, co) for c, l, co in zip(counts, labels, colors) if c > 0]
        if non_zero_cnt:
            counts_nz, labels_nz, colors_nz = zip(*non_zero_cnt)
            axes[1].pie(counts_nz, labels=labels_nz, autopct='%1.1f%%', colors=colors_nz)
        axes[1].set_title('결제수단별 건수 비율', fontsize=12, fontweight='bold')

        plt.suptitle('결제수단별 거래 분석', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        return self.save_chart(fig, '결제수단별_비교')

    def chart_21_card_missing_analysis(self):
        """카드미반영 현황"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        card_missing = self.df[self.df['증빙유형'] == 88.5]

        if len(card_missing) > 0:
            # 월별 카드미반영
            monthly = card_missing.groupby('월')['순액'].sum()
            axes[0].bar(monthly.index, monthly.values, color=COLORS['danger'])
            axes[0].set_xlabel('월')
            axes[0].set_ylabel('금액')
            axes[0].set_title('월별 카드미반영 금액', fontsize=12, fontweight='bold')
            axes[0].yaxis.set_major_formatter(plt.FuncFormatter(format_krw))
            axes[0].set_xticks(range(1, 13))

            # 거래처별 TOP 10
            top_traders = card_missing.groupby('거래처명_filled')['순액'].sum().nlargest(10)
            axes[1].barh(top_traders.index, top_traders.values, color=COLORS['danger'])
            axes[1].set_xlabel('금액')
            axes[1].set_title('카드미반영 거래처 TOP 10', fontsize=12, fontweight='bold')
            axes[1].xaxis.set_major_formatter(plt.FuncFormatter(format_krw))
            axes[1].invert_yaxis()
        else:
            axes[0].text(0.5, 0.5, '카드미반영 데이터 없음', ha='center', va='center', fontsize=12)
            axes[1].text(0.5, 0.5, '카드미반영 데이터 없음', ha='center', va='center', fontsize=12)

        plt.suptitle(f'카드미반영 분석 (총 {len(card_missing)}건, {format_krw_full(card_missing["순액"].sum())})',
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        return self.save_chart(fig, '카드미반영_분석')

    def chart_22_card_deduction_status(self):
        """카드 공제/불공제 현황"""
        fig, ax = plt.subplots(figsize=(10, 6))

        card_df = self.df[self.df['증빙유형'] == 88]

        if '공제구분' in card_df.columns and len(card_df) > 0:
            deduction = card_df.groupby('공제구분')['순액'].sum().abs()  # 절대값 사용
            deduction = deduction[deduction > 0]  # 0보다 큰 값만

            if len(deduction) > 0:
                colors = [COLORS['success'], COLORS['danger'], COLORS['light']][:len(deduction)]
                wedges, texts, autotexts = ax.pie(deduction.values, labels=deduction.index,
                                                  autopct='%1.1f%%', colors=colors)
            else:
                ax.text(0.5, 0.5, '데이터 없음', ha='center', va='center', fontsize=12)
            ax.set_title('카드 거래 공제/불공제 현황', fontsize=14, fontweight='bold')
        else:
            ax.text(0.5, 0.5, '공제구분 데이터 없음', ha='center', va='center', fontsize=12)
            ax.set_title('카드 거래 공제/불공제 현황', fontsize=14, fontweight='bold')

        plt.tight_layout()
        return self.save_chart(fig, '카드_공제구분')

    # ========== 6. 이상거래 탐지 (데이터분석 전문가) ==========

    def chart_23_outlier_detection(self):
        """이상치 탐지 (박스플롯)"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # 손익분류별 박스플롯
        expense_df = self.df[self.df['손익분류'].isin(['판관비', '매출원가'])]
        expense_df.boxplot(column='순액', by='손익분류', ax=axes[0])
        axes[0].set_title('손익분류별 금액 분포', fontsize=12)
        axes[0].set_xlabel('손익분류')
        axes[0].set_ylabel('금액')
        axes[0].yaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        plt.sca(axes[0])
        plt.xticks(rotation=0)

        # 월별 박스플롯
        self.df.boxplot(column='순액', by='월', ax=axes[1])
        axes[1].set_title('월별 금액 분포', fontsize=12)
        axes[1].set_xlabel('월')
        axes[1].set_ylabel('금액')
        axes[1].yaxis.set_major_formatter(plt.FuncFormatter(format_krw))

        plt.suptitle('이상치 탐지 (박스플롯)', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        return self.save_chart(fig, '이상치_박스플롯')

    def chart_24_large_transactions(self):
        """고액 거래 분석"""
        fig, ax = plt.subplots(figsize=(14, 7))

        # 상위 1% 거래
        threshold = self.df['순액'].abs().quantile(0.99)
        large_trans = self.df[self.df['순액'].abs() >= threshold].copy()
        large_trans = large_trans.sort_values('순액', ascending=False).head(20)

        colors = ['green' if x > 0 else 'red' for x in large_trans['순액']]
        y_labels = [f"{row['계정과목'][:10]} - {row['거래처명_filled'][:10]}"
                   for _, row in large_trans.iterrows()]

        bars = ax.barh(range(len(large_trans)), large_trans['순액'].values, color=colors)
        ax.set_yticks(range(len(large_trans)))
        ax.set_yticklabels(y_labels)
        ax.set_xlabel('금액')
        ax.set_title(f'고액 거래 TOP 20 (상위 1%: {format_krw_full(threshold)} 이상)',
                    fontsize=14, fontweight='bold')
        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax.axvline(x=0, color='black', linewidth=0.5)
        ax.invert_yaxis()

        plt.tight_layout()
        return self.save_chart(fig, '고액거래_TOP20')

    def chart_25_weekend_transactions(self):
        """주말 거래 분석"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        weekend = self.df[self.df['요일'].isin([5, 6])]  # 토, 일
        weekday = self.df[~self.df['요일'].isin([5, 6])]

        # 금액 비교
        amounts = [weekday['순액'].sum(), weekend['순액'].sum()]
        labels = ['평일', '주말']
        axes[0].pie(amounts, labels=labels, autopct='%1.1f%%',
                   colors=[COLORS['primary'], COLORS['warning']])
        axes[0].set_title('평일 vs 주말 금액 비율', fontsize=12, fontweight='bold')

        # 요일별 건수
        daily_count = self.df.groupby('요일명').size()
        order = ['월', '화', '수', '목', '금', '토', '일']
        daily_count = daily_count.reindex(order)

        colors = [COLORS['primary']]*5 + [COLORS['warning']]*2
        axes[1].bar(daily_count.index, daily_count.values, color=colors)
        axes[1].set_xlabel('요일')
        axes[1].set_ylabel('거래 건수')
        axes[1].set_title('요일별 거래 건수', fontsize=12, fontweight='bold')

        for i, v in enumerate(daily_count.values):
            axes[1].text(i, v + 5, str(v), ha='center', fontsize=9)

        plt.suptitle('주말/평일 거래 분석', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        return self.save_chart(fig, '주말평일_거래분석')

    def chart_26_amount_distribution(self):
        """금액 구간별 분포"""
        fig, ax = plt.subplots(figsize=(12, 6))

        # 금액 구간 분류
        def get_range(x):
            abs_x = abs(x)
            if abs_x < 100000:
                return '10만 미만'
            elif abs_x < 500000:
                return '10~50만'
            elif abs_x < 1000000:
                return '50~100만'
            elif abs_x < 5000000:
                return '100~500만'
            else:
                return '500만 이상'

        self.df['금액구간'] = self.df['순액'].apply(get_range)
        range_order = ['10만 미만', '10~50만', '50~100만', '100~500만', '500만 이상']
        range_count = self.df['금액구간'].value_counts().reindex(range_order)

        colors = sns.color_palette('YlOrRd', len(range_count))
        bars = ax.bar(range_count.index, range_count.values, color=colors)
        ax.set_xlabel('금액 구간')
        ax.set_ylabel('거래 건수')
        ax.set_title('금액 구간별 거래 건수 분포', fontsize=14, fontweight='bold')

        for bar, val in zip(bars, range_count.values):
            ax.text(bar.get_x() + bar.get_width()/2, val + 10, f'{val}건', ha='center', fontsize=10)

        plt.tight_layout()
        return self.save_chart(fig, '금액구간별_분포')

    # ========== 7. 기타 인사이트 (데이터분석 전문가) ==========

    def chart_27_source_type_comparison(self):
        """소스유형별 비교"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        source_amount = self.df.groupby('소스유형')['순액'].sum()
        source_count = self.df.groupby('소스유형').size()

        colors = [COLORS['primary'], COLORS['secondary'], COLORS['warning']]

        axes[0].pie(source_amount.values, labels=source_amount.index, autopct='%1.1f%%', colors=colors)
        axes[0].set_title('소스유형별 금액 비율', fontsize=12, fontweight='bold')

        axes[1].pie(source_count.values, labels=source_count.index, autopct='%1.1f%%', colors=colors)
        axes[1].set_title('소스유형별 건수 비율', fontsize=12, fontweight='bold')

        plt.suptitle('소스유형별 분석 (분개장 vat/일반/카드미반영)', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        return self.save_chart(fig, '소스유형별_비교')

    def chart_28_account_heatmap(self):
        """계정과목 × 월 히트맵"""
        fig, ax = plt.subplots(figsize=(14, 10))

        expense_df = self.df[self.df['손익분류'] == '판관비']
        pivot = expense_df.pivot_table(index='계정과목', columns='월', values='순액',
                                        aggfunc='sum', fill_value=0)

        # 총액 기준 상위 15개
        top_accounts = pivot.sum(axis=1).nlargest(15).index
        pivot = pivot.loc[top_accounts]

        sns.heatmap(pivot / 1e6, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax,
                   cbar_kws={'label': '금액 (백만원)'})
        ax.set_xlabel('월')
        ax.set_ylabel('계정과목')
        ax.set_title('계정과목별 월별 금액 히트맵 (판관비 상위 15개, 단위: 백만원)',
                    fontsize=14, fontweight='bold')
        ax.set_xticklabels([f'{m}월' for m in range(1, 13)])

        plt.tight_layout()
        return self.save_chart(fig, '계정과목_월별_히트맵')

    def chart_29_cumulative_trend(self):
        """누적 금액 추이"""
        fig, ax = plt.subplots(figsize=(14, 6))

        for pl_type in ['매출', '매출원가', '판관비']:
            pl_df = self.df[self.df['손익분류'] == pl_type]
            monthly = pl_df.groupby('월')['순액'].sum().reindex(range(1, 13), fill_value=0)
            cumsum = monthly.cumsum()
            ax.plot(cumsum.index, cumsum.values, marker='o', label=pl_type, linewidth=2)

        ax.set_xlabel('월')
        ax.set_ylabel('누적 금액')
        ax.set_title('월별 누적 금액 추이', fontsize=14, fontweight='bold')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels([f'{m}월' for m in range(1, 13)])
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return self.save_chart(fig, '누적금액_추이')

    def chart_30_summary_dashboard(self):
        """종합 대시보드"""
        fig = plt.figure(figsize=(16, 12))

        # 레이아웃 설정
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 1. 손익 요약 (KPI)
        ax1 = fig.add_subplot(gs[0, 0])
        revenue = self.df[self.df['손익분류'] == '매출']['순액'].sum()
        cost = self.df[self.df['손익분류'] == '매출원가']['순액'].sum()
        expense = self.df[self.df['손익분류'] == '판관비']['순액'].sum()
        profit = revenue - cost - expense

        ax1.text(0.5, 0.8, '매출', ha='center', fontsize=10, color='gray')
        ax1.text(0.5, 0.65, format_krw_full(revenue), ha='center', fontsize=14, fontweight='bold', color=COLORS['primary'])
        ax1.text(0.5, 0.4, '영업이익', ha='center', fontsize=10, color='gray')
        ax1.text(0.5, 0.25, format_krw_full(profit), ha='center', fontsize=14, fontweight='bold',
                color=COLORS['success'] if profit > 0 else COLORS['danger'])
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        ax1.set_title('핵심 지표', fontsize=12, fontweight='bold')

        # 2. 월별 추이
        ax2 = fig.add_subplot(gs[0, 1:])
        monthly = self.df.groupby(['월', '손익분류'])['순액'].sum().unstack(fill_value=0)
        if '매출' in monthly.columns:
            ax2.plot(monthly.index, monthly['매출'], marker='o', label='매출', linewidth=2)
        if '판관비' in monthly.columns:
            ax2.plot(monthly.index, monthly['판관비'], marker='s', label='판관비', linewidth=2)
        ax2.set_title('월별 추이', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax2.grid(True, alpha=0.3)

        # 3. 손익분류별 비율
        ax3 = fig.add_subplot(gs[1, 0])
        pl_sum = self.df.groupby('손익분류')['순액'].sum().abs()
        ax3.pie(pl_sum.values, labels=pl_sum.index, autopct='%1.0f%%', textprops={'fontsize': 8})
        ax3.set_title('손익분류 비율', fontsize=12, fontweight='bold')

        # 4. 증빙유형별 건수
        ax4 = fig.add_subplot(gs[1, 1])
        ev_count = self.df['증빙유형명'].value_counts().head(5)
        ax4.barh(ev_count.index, ev_count.values, color=COLORS['info'])
        ax4.set_title('증빙유형 TOP 5', fontsize=12, fontweight='bold')
        ax4.invert_yaxis()

        # 5. 거래처 TOP 5
        ax5 = fig.add_subplot(gs[1, 2])
        expense_df = self.df[self.df['손익분류'] == '판관비']
        top_traders = expense_df.groupby('거래처명_filled')['순액'].sum().nlargest(5)
        ax5.barh([t[:12] for t in top_traders.index], top_traders.values, color=COLORS['warning'])
        ax5.set_title('판관비 거래처 TOP 5', fontsize=12, fontweight='bold')
        ax5.xaxis.set_major_formatter(plt.FuncFormatter(format_krw))
        ax5.invert_yaxis()

        # 6. 데이터 요약
        ax6 = fig.add_subplot(gs[2, :])
        summary_text = (
            f"총 거래 건수: {len(self.df):,}건  |  "
            f"기간: 2024년 1월 ~ 12월  |  "
            f"거래처 수: {self.df['거래처명_filled'].nunique():,}개  |  "
            f"계정과목 수: {self.df['계정과목'].nunique():,}개  |  "
            f"카드미반영: {len(self.df[self.df['증빙유형'] == 88.5]):,}건"
        )
        ax6.text(0.5, 0.5, summary_text, ha='center', va='center', fontsize=11,
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
        ax6.axis('off')

        plt.suptitle('회계 데이터 종합 대시보드', fontsize=16, fontweight='bold', y=0.98)

        return self.save_chart(fig, '종합_대시보드')

    def generate_all_charts(self):
        """모든 차트 생성"""
        print("\n차트 생성 시작...")

        # 1. 수익/비용 분석
        print("\n[수익/비용 분석]")
        self.chart_01_pl_overview()
        self.chart_02_revenue_vs_cost()
        self.chart_03_expense_breakdown()
        self.chart_04_cost_structure()
        self.chart_05_profit_margin()

        # 2. 월별 추이
        print("\n[월별 추이 분석]")
        self.chart_06_monthly_trend()
        self.chart_07_monthly_revenue()
        self.chart_08_monthly_expense()
        self.chart_09_monthly_transaction_count()
        self.chart_10_monthly_avg_amount()

        # 3. 거래처 분석
        print("\n[거래처 분석]")
        self.chart_11_top_traders_expense()
        self.chart_12_top_traders_revenue()
        self.chart_13_trader_concentration()
        self.chart_14_trader_count_by_account()
        self.chart_15_trader_monthly_pattern()

        # 4. 증빙유형별 분석
        print("\n[증빙유형별 분석]")
        self.chart_16_evidence_type_overview()
        self.chart_17_evidence_type_count()
        self.chart_18_evidence_by_pl()
        self.chart_19_evidence_monthly()

        # 5. 카드/현금 분석
        print("\n[카드/현금 분석]")
        self.chart_20_card_vs_cash()
        self.chart_21_card_missing_analysis()
        self.chart_22_card_deduction_status()

        # 6. 이상거래 탐지
        print("\n[이상거래 탐지]")
        self.chart_23_outlier_detection()
        self.chart_24_large_transactions()
        self.chart_25_weekend_transactions()
        self.chart_26_amount_distribution()

        # 7. 기타 인사이트
        print("\n[기타 인사이트]")
        self.chart_27_source_type_comparison()
        self.chart_28_account_heatmap()
        self.chart_29_cumulative_trend()
        self.chart_30_summary_dashboard()

        print(f"\n총 {self.chart_count}개 차트 생성 완료!")
        print(f"저장 위치: {self.output_dir}")


# ============================================================
# 메인 실행
# ============================================================
def main():
    print("=" * 60)
    print("회계 데이터 인사이트 차트 생성")
    print("=" * 60)

    # 1. 한글 폰트 설정
    print("\n1. 환경 설정...")
    setup_korean_font()

    # 2. 데이터 로드
    print("\n2. 데이터 로드...")
    json_path = Path('input_merged_datas/더제이의원/result_2024_v01_20260106_225407.json')
    df = load_data(json_path)
    print(f"   총 {len(df):,}건 로드 완료")

    # 3. 출력 디렉토리 설정
    timestamp = datetime.now().strftime('%m-%d-%H-%M')
    output_dir = Path(f'output/더제이의원/charts_{timestamp}')

    # 4. 차트 생성
    print("\n3. 차트 생성...")
    generator = ChartGenerator(df, output_dir)
    generator.generate_all_charts()

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)


if __name__ == '__main__':
    main()
