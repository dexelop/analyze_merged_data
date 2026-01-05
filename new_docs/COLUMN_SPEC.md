# 컬럼 스펙

> 위하고(WEHAGO) 스마트A JSON 데이터의 컬럼 정의
>
> **중요도 범례**: ★★★ 업무 필수 / ★★ 업무 참고 / ★ 참고용 / - 미사용·무시 / ? 미정리

---

## 1. 분개장 (분개장_code 시트)

### 핵심 컬럼 ★★★

| 컬럼명 | 한글 | 설명 |
|--------|------|------|
| `da_date` | 회계일자 | YYYYMMDD (예: 20240101) |
| `cd_acctit` | 계정코드 | 5자리 계정과목 코드 |
| `nm_acctit` | 계정과목 | 계정과목 이름 |
| `mn_bungae1` | 차변금액 | |
| `mn_bungae2` | 대변금액 | |
| `nm_gubun_bungae` | 분개구분 | 차변, 대변, 출금, 입금, 결차, 결대 |
| `no_exter2` | 증빙유형 | → CODE_REFERENCE.md 참조 |
| `nm_trade` | 거래처명 | |
| `cd_trade` | 거래처코드 | 거래처 고유 코드 |
| `no_acct` | 전표번호 | 해당 일자의 전표 일련번호 |

### 참고 컬럼 ★★

| 컬럼명 | 한글 | 설명 |
|--------|------|------|
| `year` | 년도 | 회계년도 |
| `month` | 월 | 회계일자의 '월' |
| `day` | 일 | 회계일자의 '일' |
| `nm_remark` | 적요 | 거래 내용 메모 |
| `cd_remark` | 적요코드 | 표준 적요 코드 |
| `ty_gubn` | 차대구분코드 | 매입매출(1,2), 일반전표(3,4) |
| `nm_gubun_prn` | 전표출력구분 | 입금, 출금, 대체 등 |
| `nm_yuh` | 전표유형구분 | 일반전표, 매입전표, 매출전표 등 |
| `nm_ctrade` | 관련거래처 | 카드사, 은행 등 결제 관련 |
| `dt_insert` | 입력일시 | 데이터 입력 실제 시간 |

### 기타 컬럼 ★

| 컬럼명 | 한글 | 설명 |
|--------|------|------|
| `nm_dept` | 부서명 | 귀속 부서 |
| `nm_emp` | 사원명 | 기표/귀속 사원 |
| `nm_field` | 현장명 | 건설 현장 관리 시 사용 |
| `nm_project` | 프로젝트명 | 프로젝트별 관리 시 |
| `nm_bjoh` | 보조원장 | 보조부 관리 항목 |
| `nm_finance` | 금융기관 | 예적금/차입금 관련 |
| `yn_holiday` | 공휴일여부 | 0/1 |
| `sq_acttax2` | 입력순서 | 추가 입력 시 뒤에 추가됨 |
| `key_acctit` | 데이터키 | DB 고유 식별 키 |
| `ty_bungae` | 0/3 | 일반전표 vs 그 외 구분 (?) |

---

## 2. 매입매출전표 (매입매출전표_code 시트)

### 핵심 컬럼 ★★★

| 컬럼명 | 한글 | 설명 |
|--------|------|------|
| `da_date` | 거래일자 | |
| `no_acct` | 전표번호 | PK |
| `ty_mth` | 매입매출구분 | 1=매출, 2=매입 |
| `ty_mth2` | 유형코드 | → CODE_REFERENCE.md 참조 |
| `nm_trade` | 거래처명 | |
| `cd_trade` | 거래처코드 | |
| `no_bisocial` | 사업자등록번호 | |
| `mn_mnam` | 공급가액 | |
| `mn_vat` | 부가세 | |
| `mn_sum` | 합계금액 | |

### 참고 컬럼 ★★

| 컬럼명 | 한글 | 설명 |
|--------|------|------|
| `ty_bungae` | 분개유형 | 현금, 외상, 혼합 |
| `ty_taxgubun` | 세금구분 | 과세/면세/영세 등 |
| `no_taxbill` | 세금계산서번호 | |
| `no_ntsappr` | 국세청승인번호 | |
| `cd_taxbill` | 세금계산서코드 | |
| `dt_send` | 전송일자 | 전자세금계산서 전송일 (전자 여부 판단) |
| `sq_acttax1` | 반영순서 | 입력순 필터링 시 활용 |
| `nm_good` | 품명 | |
| `nm_jepum` | 품목명 | |
| `qt_qty` | 수량 | |
| `unit` | 단위 | |
| `cd_notdedct` | 불공제사유코드 | |
| `nm_ctrade` | 카드사이름 | |
| `cd_ctrade` | 카드거래처코드 | |
| `mn_cardsail` | 카드매출금액 | |
| `mn_cardvat` | 카드부가세 | |
| `no_exterd` | 입력원천 | 0=수기입력 |
| `da_singo_year` | 신고연도 | |
| `da_singo_mon` | 신고월 | |
| `ym_report` | 신고년월 | |
| `cd_emp` | 담당사원코드 | |
| `cd_dept` | 부서코드 | |
| `nm_dept` | 부서명 | |
| `nm_memo` | 적요/메모 | |

### 미정리 컬럼 ?

| 컬럼명 | 비고 |
|--------|------|
| `sq_pacttax1` | #N/A |
| `ty_liquor` | #N/A |
| `nm_memosub` | #N/A |
| `yn_beforebiz` | #N/A |
| `gj_gubun` | #N/A |
| `ty_mark` | #N/A |
| `nm_field` | #N/A |
| `cd_jepum` | #N/A |
| `rt_exchange` | #N/A |
| `boksu` | #N/A |
| `p_da_date` | #N/A |
| `cd_trsu` | #N/A |
| `cd_field` | #N/A |
| `yn_bjoh` | #N/A |
| `ty_finstatus` | #N/A |
| `ty_copy` | #N/A |
| `nm_krname` | #N/A |
| `nm_linecolor` | #N/A |
| `key_natcurr` | #N/A |
| `dt_upsend` | #N/A |
| `id_jeonja` | #N/A |
| `ty_bizgb2` | #N/A |
| `cd_pjt` | #N/A |
| `no_exp` | #N/A |
| `rmk_elcmd` | #N/A |
| `ty_bizgb1` | #N/A |
| `no_case` | #N/A |
| `cd_result` | #N/A |
| `str_6` | #N/A |

### 추적/참조 컬럼 (p_ prefix)

| 컬럼명 | 설명 |
|--------|------|
| `p_no_acct` | 참조전표번호 |
| `p_no_stsappr` | 추적/참조용 |
| `p_rmk_elcmd` | 추적/참조용 |
| `p_cd_elcmdrsn` | 추적/참조용 |

---

## 3. 신용카드 자동전표 (신용카드자동_code_claude 시트)

### 업무 필수 컬럼 ★★★

| 컬럼명 | 한글 | 타입 | 핵심값 |
|--------|------|------|--------|
| `ty_jungstat` | 전표상태 | int | 1=확정가능, 2=전표확정, 3=확정제외, 4=중복, 5=미추천, 6=삭제 |
| `ty_gongjea` | 공제구분 | int | 1=불공제, 2=공제 |
| `nm_acctit_cha` | 계정과목명_차변 | str | "미추천"=미처리 |
| `nm_acctit_dae` | 계정과목명_대변 | str | |
| `nm_trade` | 거래처명 | str | |
| `bisocial_no` | 사업자번호 | str | 10자리 |
| `mn_total` | 총금액 | int | 음수=환불 |
| `da_sbook` | 거래일자 | str | YYYYMMDD |

### 업무 참고 컬럼 ★★

| 컬럼명 | 한글 | 타입 | 비고 |
|--------|------|------|------|
| `cd_acctit_cha` | 차변_계정코드 | str | 20% NULL |
| `cd_acctit_dae` | 대변_계정코드 | str | |
| `cd_ctrade` | 신용카드_거래처코드 | | |
| `cd_trade` | 거래처코드 | | |
| `bizcate` | 업종 | str | 신규거래처 분류용 |
| `bizcond` | 업태 | str | |
| `mn_mnam` | 공급가액 | int | |
| `mn_vat` | 부가세 | int | 8% NULL |
| `freetax` | 면세여부 | int | 0/1 |

### 참고용 컬럼 ★

| 컬럼명 | 한글 | 비고 |
|--------|------|------|
| `sq_sbook` | 전표번호 | PK |
| `ty_biz` | 사업자유형 | 1~4 |
| `cnt_recommend_cha` | AI 추천 차변 후보 수 | 0~3 |
| `cnt_recommend_dae` | AI 추천 대변 후보 수 | 0~2 |
| `yn_holiday` | 휴일여부 | 0~2 |
| `ty_mth` | 유형 | 일반/매입 |
| `ty_mth2` | 세부유형 | |
| `chk_dupl_mth2` | 중복체크_method | |
| `chk_duplcha` | 추천여부(차변) | |
| `chk_dupldae` | 추천여부(대변) | |
| `cnt_chagubun` | 차변 라인수 | |
| `cnt_daegubun` | 대변 라인수 | |
| `elec_confirm` | 전자세금계산서 중복 | |
| `no_bisocial_ai` | 사업자등록번호_ai | |
| `no_closed_business` | 사업자등록번호 | |
| `provider` | 대량발권 업체 | 철도, 항공 등 |
| `ty_trade` | | |

### 미사용/무시 가능 컬럼 -

| 컬럼명 | 비고 |
|--------|------|
| `mn_service` | 전체 NULL |
| `nm_remark` | 전체 NULL |
| `sq_group` | 전체 NULL |
| `nm_dnf` | 전체 빈값 |
| `new_date` | 전체 "0" |
| `gj_gubun` | 전체 "0" |
| `jasan` | 전체 0 |
