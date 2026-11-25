"""
메인 노트북(nps_exit_prediction.ipynb) 2~4장과 12장의 데이터 만들기 과정을 함수로 옮긴 모듈.
보충 노트북(pca_analysis.ipynb)에서 같은 데이터를 다시 만들 때 사용한다.
"""
import numpy as np
import pandas as pd

COLS = ['자료생성년월', '사업장명', '사업자번호', '가입상태', '우편번호', '지번주소', '도로명주소',
        '법정동코드', '행정동코드', '시도코드', '시군구코드', '읍면동코드', '사업장형태', '업종코드',
        '업종명', '적용일자', '재등록일자', '탈퇴일자', '가입자수', '고지금액', '신규취득자수', '상실가입자수']
KEY = ['사업자번호', '사업장명', '법정동코드', '업종코드']
NUM = ['가입자수', '고지금액', '신규취득자수', '상실가입자수']
FEATURES = ['가입자수', '1인당고지금액', '신규취득자수', '상실가입자수', '상실률', '취득률', '업력',
            '재등록여부', '법인여부', '신규진입', '인원증감률_1개월', '인원증감률_3개월',
            '인원증감률_4개월', '고지금액증감률_3개월', '최근상실자합', '시도코드', '업종대분류']


def load_month(ym, raw_dir='data/raw'):
    df = pd.read_csv(f'{raw_dir}/nps_{ym}.csv', encoding='cp949', names=COLS, header=0, dtype=str)
    df = df[~df.duplicated(KEY, keep=False)]
    for c in NUM:
        df[c] = pd.to_numeric(df[c])
    return df


def _lag(df, tag):
    return df[KEY + NUM].rename(columns={c: c + tag for c in NUM})


def _rate(now, before):
    return (now - before) / before.replace(0, np.nan)


def build_dataset(base_ym, m1_ym, m3_ym, m4_ym, fut_ym, missing_as_exit=False, raw_dir='data/raw'):
    b = load_month(base_ym, raw_dir)
    b = b[b['가입상태'] == '1']
    d = b.merge(_lag(load_month(m1_ym, raw_dir), '_m1'), on=KEY, how='left')
    d = d.merge(_lag(load_month(m3_ym, raw_dir), '_m3'), on=KEY, how='left')
    d = d.merge(_lag(load_month(m4_ym, raw_dir), '_m4'), on=KEY, how='left')
    f = load_month(fut_ym, raw_dir)
    d = d.merge(f[KEY + ['가입상태']].rename(columns={'가입상태': '가입상태_3개월후'}), on=KEY, how='left')
    if missing_as_exit:
        d['탈퇴'] = (d['가입상태_3개월후'] != '1').astype(int)
    else:
        d = d[d['가입상태_3개월후'].notna()].copy()
        d['탈퇴'] = (d['가입상태_3개월후'] == '2').astype(int)

    end = pd.Timestamp(base_ym[:4] + '-' + base_ym[4:] + '-01') + pd.offsets.MonthEnd(0)
    d['1인당고지금액'] = np.where(d['가입자수'] > 0, d['고지금액'] / d['가입자수'], 0)
    d['상실률'] = np.where(d['가입자수'] > 0, d['상실가입자수'] / d['가입자수'], 0)
    d['취득률'] = np.where(d['가입자수'] > 0, d['신규취득자수'] / d['가입자수'], 0)
    d['업력'] = (end - pd.to_datetime(d['적용일자'], errors='coerce')).dt.days / 365.25
    d['재등록여부'] = d['재등록일자'].notna().astype(int)
    d['법인여부'] = (d['사업장형태'] == '1').astype(int)
    d['신규진입'] = d['가입자수_m3'].isna().astype(int)
    d['인원증감률_1개월'] = _rate(d['가입자수'], d['가입자수_m1'])
    d['인원증감률_3개월'] = _rate(d['가입자수'], d['가입자수_m3'])
    d['인원증감률_4개월'] = _rate(d['가입자수'], d['가입자수_m4'])
    d['고지금액증감률_3개월'] = _rate(d['고지금액'], d['고지금액_m3'])
    d['최근상실자합'] = d['상실가입자수'] + d['상실가입자수_m1'].fillna(0)
    d['시도코드'] = d['시도코드'].astype(int)
    d['업종대분류'] = d['업종코드'].str[:2].astype(int)
    d['건설업'] = d['업종명'].fillna('').str.contains('공사|건설').astype(int)
    X = d[FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0)
    return X, d['탈퇴'], d
