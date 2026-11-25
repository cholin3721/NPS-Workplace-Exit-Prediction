import nbformat as nbf
import sys

cells = []
def md(s): cells.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s): cells.append(nbf.v4.new_code_cell(s.strip()))

md(r"""
# 국민연금 가입 사업장 데이터로 본 사업장 탈퇴 3개월 조기 예측
### 데이터분석 기말대체 프로젝트 · 202444085 김철중

**문제:** 지금 국민연금에 가입되어 있는 사업장 중 **3개월 안에 가입을 탈퇴할 사업장**(폐업·휴업·공사 현장 종료 등)을 미리 찾을 수 있을까?

- 데이터: 공공데이터포털 「국민연금공단_국민연금 가입 사업장 내역」 월별 CSV (2026-03, 04, 06, 07, 10월분)
- 기준월(T): **2026-07** → 정답(label): **2026-10** 파일에서 가입상태가 '탈퇴(2)'로 바뀌었는가
- 분석 흐름 (1주차 데이터과학 방법론): 데이터 수집 → 정제/병합 → EDA → 모델링 → 불균형 처리 → 튜닝 → 해석·제언
""")

md("## 1. 라이브러리 불러오기")
code(r"""
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time, os, sys

# 한글 폰트 (11주차: Matplotlib 한글 폰트 설정)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
sns.set_style('whitegrid', {'font.family': 'Malgun Gothic'})

os.makedirs('figures', exist_ok=True)
os.makedirs('results', exist_ok=True)
def save(name):
    plt.tight_layout()
    plt.savefig(f'figures/{name}.png', dpi=150, bbox_inches='tight')
""")

md(r"""
## 2. 데이터 불러오기 및 정제 (3~5주차)
월별 파일은 약 59만 행, 22개 열이다. 같은 사업장을 여러 달에 걸쳐 연결해야 하므로
**사업자등록번호(앞 6자리) + 사업장명 + 법정동코드 + 업종코드**를 키로 사용한다.
키가 중복되는 행은 어느 사업장인지 구분할 수 없으므로 모두 제거한다 (3주차 `duplicated`).
""")
code(r"""
cols = ['자료생성년월','사업장명','사업자번호','가입상태','우편번호','지번주소','도로명주소',
        '법정동코드','행정동코드','시도코드','시군구코드','읍면동코드','사업장형태','업종코드',
        '업종명','적용일자','재등록일자','탈퇴일자','가입자수','고지금액','신규취득자수','상실가입자수']
KEY = ['사업자번호','사업장명','법정동코드','업종코드']

def load_month(ym):
    df = pd.read_csv(f'data/raw/nps_{ym}.csv', encoding='cp949', names=cols, header=0, dtype=str)
    before = len(df)
    df = df[~df.duplicated(KEY, keep=False)]          # 키 중복 행 제거
    for c in ['가입자수','고지금액','신규취득자수','상실가입자수']:
        df[c] = pd.to_numeric(df[c])
    print(f'{ym}: {before:,}행 → 중복 제거 후 {len(df):,}행')
    return df

t = time.time()
base = load_month('202607')   # 기준월 T
m1   = load_month('202606')   # T-1
m3   = load_month('202604')   # T-3
m4   = load_month('202603')   # T-4
fut  = load_month('202610')   # T+3 (정답 확인용)
print(f'불러오기 {time.time()-t:.0f}초')
""")
code(r"""
base.info()
""")
code(r"""
base.isnull().sum()
""")
md(r"""
결측치는 `재등록일자`, `탈퇴일자`에만 있다. 이 두 값은 "해당 없음"이라는 의미이므로 삭제하지 않고
`재등록 여부` 같은 변수로 바꿔서 쓴다 (3주차 이상데이터 처리: ③ 변수화).
""")

md(r"""
## 3. 데이터 병합과 정답(label) 만들기 (4~5주차 `merge`)
- 기준월(2026-07)에 **가입상태 = 1(등록)** 인 사업장만 대상으로 한다.
- 3개월 뒤(2026-10) 파일에서 가입상태가 **2(탈퇴)** 이면 `탈퇴=1`, 여전히 1이면 `탈퇴=0`.
- 2026-10 파일에서 아예 사라진 사업장은 탈퇴인지, 공개 범위(법인 3인·개인 10인 이상)에서 빠진 것인지,
  사업장명 변경인지 알 수 없으므로 분석에서 제외한다.
""")
code(r"""
base = base[base['가입상태'] == '1']

def lag_cols(df, tag):
    out = df[KEY + ['가입자수','고지금액','신규취득자수','상실가입자수']].copy()
    return out.rename(columns={c: c + tag for c in ['가입자수','고지금액','신규취득자수','상실가입자수']})

df = base.merge(lag_cols(m1, '_m1'), on=KEY, how='left')
df = df.merge(lag_cols(m3, '_m3'), on=KEY, how='left')
df = df.merge(lag_cols(m4, '_m4'), on=KEY, how='left')
df = df.merge(fut[KEY + ['가입상태']].rename(columns={'가입상태': '가입상태_3개월후'}), on=KEY, how='left')

print('기준월 등록 사업장:', f'{len(df):,}')
print(df['가입상태_3개월후'].fillna('사라짐').value_counts())

df = df[df['가입상태_3개월후'].notna()].copy()
df['탈퇴'] = (df['가입상태_3개월후'] == '2').astype(int)
print('\n분석 대상:', f'{len(df):,}', '/ 탈퇴 비율:', round(df['탈퇴'].mean() * 100, 3), '%')
""")

md(r"""
## 4. 파생변수 만들기 (5주차 함수 매핑·연산)
| 변수 | 의미 |
|---|---|
| 1인당고지금액 | 고지금액 ÷ 가입자수 (급여 수준의 대리 지표) |
| 상실률 / 취득률 | 이번 달 상실(퇴사)·취득(입사) 인원 ÷ 가입자수 |
| 업력 | 2026-07-31 − 적용일자 (년) |
| 인원증감률_1/3/4개월 | (현재 가입자수 − n개월 전 가입자수) ÷ n개월 전 가입자수 |
| 고지금액증감률_3개월 | 3개월 동안 고지금액 변화율 (급여 축소·휴직 신호) |
| 최근상실자합 | 이번 달 + 지난 달 상실자 수 |
| 신규진입 | 3개월 전 파일에 없던 사업장 |
""")
code(r"""
df['1인당고지금액'] = np.where(df['가입자수'] > 0, df['고지금액'] / df['가입자수'], 0)
df['상실률'] = np.where(df['가입자수'] > 0, df['상실가입자수'] / df['가입자수'], 0)
df['취득률'] = np.where(df['가입자수'] > 0, df['신규취득자수'] / df['가입자수'], 0)
df['업력'] = (pd.Timestamp('2026-07-31') - pd.to_datetime(df['적용일자'], errors='coerce')).dt.days / 365.25
df['재등록여부'] = df['재등록일자'].notna().astype(int)
df['법인여부'] = (df['사업장형태'] == '1').astype(int)
df['신규진입'] = df['가입자수_m3'].isna().astype(int)

def rate(now, before):
    return (now - before) / before.replace(0, np.nan)

df['인원증감률_1개월'] = rate(df['가입자수'], df['가입자수_m1'])
df['인원증감률_3개월'] = rate(df['가입자수'], df['가입자수_m3'])
df['인원증감률_4개월'] = rate(df['가입자수'], df['가입자수_m4'])
df['고지금액증감률_3개월'] = rate(df['고지금액'], df['고지금액_m3'])
df['최근상실자합'] = df['상실가입자수'] + df['상실가입자수_m1'].fillna(0)

df['시도코드'] = df['시도코드'].astype(int)
df['업종대분류'] = df['업종코드'].str[:2].astype(int)

FEATURES = ['가입자수','1인당고지금액','신규취득자수','상실가입자수','상실률','취득률','업력',
            '재등록여부','법인여부','신규진입','인원증감률_1개월','인원증감률_3개월',
            '인원증감률_4개월','고지금액증감률_3개월','최근상실자합','시도코드','업종대분류']

X = df[FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0)   # 비교 대상이 없으면 변화 0으로 처리
y = df['탈퇴']
X.describe().T.round(2)
""")

md("## 5. 탐색적 데이터 분석 EDA (7주차: 관찰 → 요약통계 → 시각화)")
md("### 5-1. 클래스 불균형과 '정확도의 함정' (1주차 FDS 예시)")
code(r"""
print(y.value_counts())
plt.figure(figsize=(5, 5))
plt.pie(y.value_counts(), labels=['유지', '3개월 내 탈퇴'], autopct='%.2f%%',
        colors=['#9ecae1', '#e6550d'], startangle=90, explode=[0, 0.15])
plt.title('기준월 등록 사업장의 3개월 후 상태')
save('01_class_ratio')
plt.show()

# 모든 사업장을 '유지'라고 찍기만 해도 정확도는?
print('전부 0으로 예측했을 때 정확도:', round((y == 0).mean() * 100, 2), '%  → 하지만 탈퇴 사업장은 하나도 못 찾음')
""")
md(r"""
탈퇴 비율이 약 0.4%밖에 안 되므로, 아무것도 학습하지 않고 전부 "유지"라고 해도 정확도가 99.6%가 나온다.
그래서 이 프로젝트는 **정확도 대신 Precision, Recall, F1, PR-AUC(Average Precision)** 를 주 평가지표로 쓴다.
""")

md("### 5-2. 규모·업력별 탈퇴율")
code(r"""
df['규모구간'] = pd.cut(df['가입자수'], bins=[-1, 0, 4, 9, 29, 99, 10**7],
                    labels=['0명', '1~4명', '5~9명', '10~29명', '30~99명', '100명+'])
df['업력구간'] = pd.cut(df['업력'], bins=[-1, 1, 3, 5, 10, 20, 100],
                    labels=['1년 미만', '1~3년', '3~5년', '5~10년', '10~20년', '20년+'])

size_rate = df.groupby('규모구간')['탈퇴'].agg(['mean', 'size'])
age_rate = df.groupby('업력구간')['탈퇴'].agg(['mean', 'size'])
print(size_rate, '\n', age_rate)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].bar(size_rate.index.astype(str)[1:], size_rate['mean'][1:] * 100, color='#3182bd')
ax[0].set_title('가입자 규모별 3개월 내 탈퇴율 (%)')
ax[0].set_ylabel('탈퇴율 (%)')
ax[1].plot(age_rate.index.astype(str), age_rate['mean'] * 100, marker='o', color='#e6550d')
ax[1].set_title('업력별 3개월 내 탈퇴율 (%)')
save('02_size_age_rate')
plt.show()
print('※ 가입자 0명인 등록 사업장의 탈퇴율:', round(size_rate.loc['0명', 'mean'] * 100, 1), '% (n =', size_rate.loc['0명', 'size'], ')')
""")

md("### 5-3. 업종별 탈퇴율 (사업장 1,000곳 이상 업종)")
code(r"""
ind = df.groupby('업종명')['탈퇴'].agg(['mean', 'size'])
ind = ind[ind['size'] >= 1000].sort_values('mean', ascending=False)
top = ind.head(15).sort_values('mean')

plt.figure(figsize=(9, 6))
plt.barh(top.index, top['mean'] * 100, color='#e6550d')
plt.axvline(df['탈퇴'].mean() * 100, color='gray', linestyle='--', label='전체 평균')
plt.title('탈퇴율 상위 15개 업종 (%)')
plt.legend()
save('03_industry_top15')
plt.show()
ind.head(15)
""")
code(r"""
# 탈퇴율 상위 업종이 대부분 건설·공사업 → 건설업 비중 확인
df['건설업'] = df['업종명'].fillna('').str.contains('공사|건설').astype(int)
print('전체 사업장 중 건설·공사업 비중:', round(df['건설업'].mean() * 100, 1), '%')
print('탈퇴 사업장 중 건설·공사업 비중:', round(df.loc[df['탈퇴'] == 1, '건설업'].mean() * 100, 1), '%')
print('신규진입(3개월 내 등록) 사업장의 탈퇴율:', round(df.loc[df['신규진입'] == 1, '탈퇴'].mean() * 100, 2), '%',
      '/ 기존 사업장:', round(df.loc[df['신규진입'] == 0, '탈퇴'].mean() * 100, 2), '%')
""")
md(r"""
건설·공사업은 공사 현장마다 사업장을 따로 등록했다가 공사가 끝나면 탈퇴하는 경우가 많다.
따라서 이 데이터의 '탈퇴'는 **폐업뿐 아니라 현장 종료·휴업·이전**까지 포함한다는 점을 해석할 때 주의해야 한다.
""")

md("### 5-4. 지역별 탈퇴율")
code(r"""
sido_name = {11:'서울', 26:'부산', 27:'대구', 28:'인천', 29:'광주', 30:'대전', 31:'울산', 36:'세종',
             41:'경기', 42:'강원', 43:'충북', 44:'충남', 45:'전북', 46:'전남', 47:'경북', 48:'경남',
             50:'제주', 51:'강원', 52:'전북'}
df['시도'] = df['시도코드'].map(sido_name)
sido = df.groupby('시도')['탈퇴'].agg(['mean', 'size'])
sido = sido[sido['size'] >= 1000].sort_values('mean', ascending=False)

plt.figure(figsize=(10, 4))
sns.barplot(x=sido.index, y=sido['mean'] * 100, color='#3182bd')
plt.title('시도별 3개월 내 탈퇴율 (%)')
plt.ylabel('탈퇴율 (%)')
save('04_sido_rate')
plt.show()
""")

md("### 5-5. 탈퇴 여부에 따른 변수 분포 (12주차 seaborn boxplot)")
code(r"""
sample = df.sample(50000, random_state=42)
sample = pd.concat([sample, df[df['탈퇴'] == 1]]).drop_duplicates()
sample['상태'] = sample['탈퇴'].map({0: '유지', 1: '탈퇴'})

fig, ax = plt.subplots(1, 3, figsize=(15, 4))
sns.boxplot(data=sample, x='상태', y='1인당고지금액', ax=ax[0], showfliers=False)
ax[0].set_title('1인당 고지금액')
sns.boxplot(data=sample, x='상태', y='업력', ax=ax[1], showfliers=False)
ax[1].set_title('업력 (년)')
sns.boxplot(data=sample, x='상태', y=sample['인원증감률_3개월'].clip(-1, 1), ax=ax[2], showfliers=False)
ax[2].set_title('3개월 인원 증감률')
save('05_boxplots')
plt.show()

df.groupby('탈퇴')[['가입자수','1인당고지금액','업력','상실률','인원증감률_3개월','고지금액증감률_3개월']].median()
""")

md("### 5-6. 상관관계 히트맵 (7주차·12주차)")
code(r"""
corr = pd.concat([X, y], axis=1).corr()
plt.figure(figsize=(12, 10))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0, annot_kws={'size': 7})
plt.title('변수 간 상관계수')
save('06_corr_heatmap')
plt.show()
corr['탈퇴'].drop('탈퇴').sort_values()
""")
md(r"""
탈퇴와 단순 선형 상관이 큰 변수는 거의 없다(|r| < 0.1). 즉 하나의 변수로 설명되는 문제가 아니라
**여러 신호의 조합**을 봐야 하는 문제이므로, 비선형 관계를 잡는 트리 기반 앙상블 모델이 유리할 것으로 예상된다.
""")

md(r"""
## 6. 학습/테스트 분리 (6주차)
탈퇴 비율을 유지하도록 `stratify=y` 로 8:2 분할한다. 테스트셋은 마지막 평가 전까지 쓰지 않는다.
""")
code(r"""
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
print(X_train.shape, X_test.shape, '/ 학습 탈퇴 수:', y_train.sum(), '/ 테스트 탈퇴 수:', y_test.sum())
""")

md(r"""
## 7. 모델 비교: 층화 5-겹 교차검증 (7·9·10주차)
교안에서 배운 분류 알고리즘을 같은 조건에서 비교한다. 시간 절약을 위해 학습셋에서
탈퇴 비율을 유지한 15만 행을 뽑아 교차검증한다.
SVM은 15만 행에서 학습 시간이 지나치게 길어 제외했다.
""")
code(r"""
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

X_cv, _, y_cv, _ = train_test_split(X_train, y_train, train_size=150000, stratify=y_train, random_state=42)

models = {
    'LogisticRegression': make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    'DecisionTree': DecisionTreeClassifier(max_depth=8, random_state=42),
    'RandomForest': RandomForestClassifier(n_estimators=100, min_samples_leaf=3, n_jobs=-1, random_state=42),
    'AdaBoost': AdaBoostClassifier(random_state=42),
    'XGBoost': XGBClassifier(n_estimators=300, max_depth=5, learning_rate=0.05, n_jobs=-1, random_state=42),
    'LightGBM': LGBMClassifier(n_estimators=300, learning_rate=0.05, verbose=-1, random_state=42),
}
models['Voting(soft)'] = VotingClassifier(
    estimators=[('rf', models['RandomForest']), ('xgb', models['XGBoost']), ('lgbm', models['LightGBM'])],
    voting='soft')

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'average_precision']

rows = []
for name, model in models.items():
    t = time.time()
    s = cross_validate(model, X_cv, y_cv, cv=skf, scoring=scoring, n_jobs=1)
    row = {'model': name}
    for m in scoring:
        row[m] = s['test_' + m].mean()
    row['PR-AUC std'] = s['test_average_precision'].std()
    row['time(s)'] = time.time() - t
    rows.append(row)
    print(f'{name:20s} PR-AUC={row["average_precision"]:.4f}  ROC-AUC={row["roc_auc"]:.4f}  ({row["time(s)"]:.0f}s)')

cv_result = pd.DataFrame(rows).set_index('model').sort_values('average_precision', ascending=False)
cv_result.to_csv('results/model_cv_result.csv', encoding='utf-8-sig')
cv_result.round(4)
""")
code(r"""
fig, ax = plt.subplots(1, 2, figsize=(13, 4))
cv_result['accuracy'].plot(kind='bar', ax=ax[0], color='#9ecae1', ylim=(0.99, 1.0))
ax[0].set_title('정확도(accuracy): 모두 99.6% 근처 → 비교 불가')
cv_result[['average_precision', 'roc_auc']].plot(kind='bar', ax=ax[1], color=['#e6550d', '#3182bd'])
ax[1].set_title('PR-AUC / ROC-AUC (5-fold 평균)')
for a in ax: a.tick_params(axis='x', rotation=30)
save('07_model_compare')
plt.show()
""")
md(r"""
정확도로는 모든 모델이 99.6%대로 차이가 없다. 확률 순위를 평가하는 PR-AUC·ROC-AUC로 보면 차이가 드러난다.
PR-AUC 기준으로 **Voting(soft) ≈ RandomForest > XGBoost > LightGBM** 순이며, 무작위로 고를 때의 기준선(탈퇴 비율 0.004)보다
약 45배 높다. 단일 결정트리와 로지스틱 회귀는 앙상블보다 크게 낮다.
또 임계값 0.5에서는 대부분 모델의 Recall이 매우 낮다. 소수 클래스(탈퇴)를 거의 "유지"로 예측해 버리는
**다수결 편향** 때문이며, 다음 단계에서 불균형 처리로 이를 완화한다.
""")

md(r"""
## 8. 불균형 처리 기법 비교: SMOTE · ADASYN · FI-SMOTE
소수 클래스를 늘리는 오버샘플링은 **학습셋에만** 적용하고, 테스트셋은 원본 그대로 평가한다
(테스트셋까지 늘리면 정보 누수가 생김).
- `class_weight`: 샘플을 만들지 않고 소수 클래스 오차에 가중치를 주는 방법
- SMOTE / ADASYN: imbalanced-learn 라이브러리 (교안 외 기법)
- **FI-SMOTE**: 본인이 1학기에 제안한 기법. 특성 중요도가 높은 변수는 원본 근처에서, 낮은 변수는 자유롭게 보간
- 모든 오버샘플링은 소수 클래스를 다수 클래스의 10%까지 늘린다 (`sampling_strategy=0.1`)
""")
code(r"""
from imblearn.over_sampling import SMOTE, ADASYN
from sklearn.metrics import (f1_score, precision_score, recall_score, roc_auc_score,
                             average_precision_score, matthews_corrcoef)
sys.path.append('src')
from fi_smote import fi_smote_resample

def recall_at_top(y_true, prob, pct):
    # 위험 점수 상위 pct% 사업장만 점검했을 때 실제 탈퇴 사업장 중 몇 %를 찾는가
    n = int(len(prob) * pct / 100)
    top = np.argsort(prob)[::-1][:n]
    return np.asarray(y_true)[top].sum() / np.asarray(y_true).sum()

def evaluate(y_true, prob, th=0.5):
    pred = (prob >= th).astype(int)
    return {'PR-AUC': average_precision_score(y_true, prob), 'ROC-AUC': roc_auc_score(y_true, prob),
            'Precision': precision_score(y_true, pred, zero_division=0), 'Recall': recall_score(y_true, pred),
            'F1': f1_score(y_true, pred), 'MCC': matthews_corrcoef(y_true, pred),
            'Recall@상위5%': recall_at_top(y_true, prob, 5)}

samplers = {
    '없음': None,
    'class_weight': 'weight',
    'SMOTE': SMOTE(sampling_strategy=0.1, random_state=42),
    'ADASYN': ADASYN(sampling_strategy=0.1, random_state=42),
    'FI-SMOTE': 'fi',
}

def make_model(name, weight=False):
    if name == 'LightGBM':
        return LGBMClassifier(n_estimators=300, learning_rate=0.05, verbose=-1, random_state=42,
                              class_weight='balanced' if weight else None)
    return RandomForestClassifier(n_estimators=100, min_samples_leaf=3, n_jobs=-1, random_state=42,
                                  class_weight='balanced_subsample' if weight else None)

res_rows = []
for s_name, sampler in samplers.items():
    t = time.time()
    if sampler is None or sampler == 'weight':
        Xr, yr = X_train, y_train
    elif sampler == 'fi':
        Xr, yr = fi_smote_resample(X_train, y_train, sampling_strategy=0.1, random_state=42)
    else:
        Xr, yr = sampler.fit_resample(X_train, y_train)
    for m_name in ['LightGBM', 'RandomForest']:
        model = make_model(m_name, weight=(sampler == 'weight'))
        model.fit(Xr, yr)
        prob = model.predict_proba(X_test)[:, 1]
        row = {'모델': m_name, '불균형처리': s_name, '학습행수': len(yr)}
        row.update(evaluate(y_test, prob))
        res_rows.append(row)
    print(f'{s_name:12s} 완료 ({time.time()-t:.0f}s, 학습 {len(yr):,}행)')

imb_result = pd.DataFrame(res_rows)
os.makedirs('results', exist_ok=True)
imb_result.to_csv('results/imbalance_result.csv', index=False, encoding='utf-8-sig')
imb_result.round(4)
""")
code(r"""
fig, ax = plt.subplots(1, 3, figsize=(16, 4))
for i, metric in enumerate(['PR-AUC', 'F1', 'Recall@상위5%']):
    pv = imb_result.pivot(index='불균형처리', columns='모델', values=metric).loc[list(samplers)]
    pv.plot(kind='bar', ax=ax[i], color=['#3182bd', '#e6550d'])
    ax[i].set_title(metric)
    ax[i].tick_params(axis='x', rotation=0)
save('08_imbalance_compare')
plt.show()
""")
md(r"""
**해석**
- 오버샘플링 3종(SMOTE, ADASYN, FI-SMOTE) 중에서는 두 모델 모두 **FI-SMOTE의 PR-AUC가 가장 높다.**
  SMOTE·ADASYN은 오히려 원본(없음)보다 PR-AUC가 떨어졌는데, 무작위 보간이 경계에 노이즈를 만든 것으로 보인다.
- RandomForest + FI-SMOTE는 임계값 0.5에서 **F1(0.22)과 MCC(0.22)가 전체 조합 중 1위**다.
- 다만 순위 지표인 PR-AUC 자체는 오버샘플링을 하지 않은 RandomForest가 가장 높았다.
  오버샘플링의 효과는 주로 "임계값 0.5에서 놓치던 탈퇴 사업장을 더 잡아내는 것(Recall 상승)"에 있다는 뜻이다.
- 이는 FI-SMOTE 논문(극단적 불균형에서 F1·MCC 1위, AUC는 SMOTE 계열과 비슷)과 같은 경향이다.
""")

md(r"""
### 8-2. 한 번의 분할로 결론을 내도 될까? — 층화 5-겹 반복 검증
위 비교는 테스트셋 한 개(탈퇴 407곳)의 결과라 우연일 수 있다. 학습셋을 층화 5-겹으로 나눠
**RandomForest × {없음, SMOTE, ADASYN, FI-SMOTE}** 를 5번 반복하고, 평균과 표준편차, 그리고 FI-SMOTE가 이긴 횟수를 센다.
(오버샘플링은 매번 학습 fold에만 적용)
""")
code(r"""
rep_rows = []
skf5 = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
t = time.time()
for k, (tr, va) in enumerate(skf5.split(X_train, y_train)):
    Xa, ya = X_train.iloc[tr], y_train.iloc[tr]
    Xv, yv = X_train.iloc[va], y_train.iloc[va]
    for s_name in ['없음', 'SMOTE', 'ADASYN', 'FI-SMOTE']:
        if s_name == '없음':
            Xr, yr = Xa, ya
        elif s_name == 'FI-SMOTE':
            Xr, yr = fi_smote_resample(Xa, ya, sampling_strategy=0.1, random_state=k)
        else:
            Xr, yr = samplers[s_name].fit_resample(Xa, ya)
        m = make_model('RandomForest')
        m.fit(Xr, yr)
        r = evaluate(yv, m.predict_proba(Xv)[:, 1])
        r.update({'fold': k + 1, '불균형처리': s_name})
        rep_rows.append(r)
    print(f'fold {k+1} 완료 ({time.time()-t:.0f}s)')

rep = pd.DataFrame(rep_rows)
rep.to_csv('results/imbalance_cv5_folds.csv', index=False, encoding='utf-8-sig')
metrics5 = ['PR-AUC', 'F1', 'MCC', 'Recall', 'Precision', 'Recall@상위5%']
rep_summary = rep.groupby('불균형처리')[metrics5].agg(['mean', 'std']).loc[['없음', 'SMOTE', 'ADASYN', 'FI-SMOTE']]
rep_summary.to_csv('results/imbalance_cv5_summary.csv', encoding='utf-8-sig')
rep_summary.round(4)
""")
code(r"""
# fold별로 FI-SMOTE가 다른 방법보다 높았던 횟수 (5번 중)
wins = {}
for other in ['없음', 'SMOTE', 'ADASYN']:
    a = rep[rep['불균형처리'] == 'FI-SMOTE'].set_index('fold')
    b = rep[rep['불균형처리'] == other].set_index('fold')
    wins[f'FI-SMOTE > {other}'] = {m: int((a[m] > b[m]).sum()) for m in ['PR-AUC', 'F1', 'MCC']}
wins = pd.DataFrame(wins).T
wins.to_csv('results/imbalance_cv5_wins.csv', encoding='utf-8-sig')

fig, ax = plt.subplots(1, 3, figsize=(15, 4))
order = ['없음', 'SMOTE', 'ADASYN', 'FI-SMOTE']
for i, m in enumerate(['PR-AUC', 'F1', 'MCC']):
    sns.boxplot(data=rep, x='불균형처리', y=m, order=order, ax=ax[i],
                palette=['#bdbdbd', '#9ecae1', '#6baed6', '#e6550d'])
    sns.stripplot(data=rep, x='불균형처리', y=m, order=order, ax=ax[i], color='black', size=4)
    ax[i].set_title(f'{m} (RandomForest, 5-fold)')
    ax[i].set_xlabel('')
save('08b_imbalance_cv5')
plt.show()
wins
""")

md(r"""
## 9. 하이퍼파라미터 튜닝: GridSearchCV (9주차)
불균형 처리 비교에서 **F1과 MCC가 가장 높았던 조합은 RandomForest + FI-SMOTE** 였다.
RandomForest의 주요 파라미터를 `scoring='average_precision'`(PR-AUC) 기준 3-겹 교차검증 그리드 서치로 고른다.
""")
code(r"""
from sklearn.model_selection import GridSearchCV
params = {'n_estimators': [100, 200],
          'min_samples_leaf': [1, 3, 5],
          'max_features': ['sqrt', 0.5]}
gs = GridSearchCV(RandomForestClassifier(random_state=42, n_jobs=1), params,
                  scoring='average_precision', cv=StratifiedKFold(3, shuffle=True, random_state=42), n_jobs=-1)
t = time.time()
gs.fit(X_cv, y_cv)
print('탐색 조합 수:', len(gs.cv_results_['params']), f'/ {time.time()-t:.0f}s')
print(gs.best_params_)
print('best PR-AUC (CV):', round(gs.best_score_, 4))
""")

md(r"""
## 10. 최종 모델 평가
튜닝된 파라미터의 RandomForest를 **FI-SMOTE로 늘린 전체 학습셋**으로 다시 학습하고,
한 번도 보지 않은 테스트셋으로 평가한다.
""")
code(r"""
best_sampler = 'FI-SMOTE'
Xf, yf = fi_smote_resample(X_train, y_train, sampling_strategy=0.1, random_state=42)

final = RandomForestClassifier(random_state=42, n_jobs=-1, **gs.best_params_)
final.fit(Xf, yf)
prob = final.predict_proba(X_test)[:, 1]
final_metrics = evaluate(y_test, prob)
pd.Series(final_metrics).round(4)
""")

md(r"""
### 10-1. 임계값(Threshold) 선택: Precision과 Recall의 트레이드오프 (1주차)
1주차 FDS 예시처럼, 탈퇴 위험 사업장을 **놓치는 비용(FN)** 과 **괜히 점검하는 비용(FP)** 사이에서 기준을 고른다.
""")
code(r"""
from sklearn.metrics import precision_recall_curve, confusion_matrix
prec, rec, ths = precision_recall_curve(y_test, prob)
f1s = 2 * prec * rec / (prec + rec + 1e-12)
best_i = np.argmax(f1s[:-1])
best_th = ths[best_i]
print(f'F1 최대 임계값 = {best_th:.3f} → Precision {prec[best_i]:.3f}, Recall {rec[best_i]:.3f}, F1 {f1s[best_i]:.3f}')

table = []
for th in [0.5, 0.3, 0.2, best_th, 0.1, 0.05, 0.02]:
    m = evaluate(y_test, prob, th)
    table.append({'임계값': round(th, 3), 'Precision': m['Precision'], 'Recall': m['Recall'], 'F1': m['F1'],
                  '경보 사업장 수': int((prob >= th).sum())})
th_table = pd.DataFrame(table).drop_duplicates('임계값').sort_values('임계값', ascending=False)
th_table.to_csv('results/threshold_table.csv', index=False, encoding='utf-8-sig')

fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].plot(rec, prec, color='#e6550d')
ax[0].scatter(rec[best_i], prec[best_i], color='black', zorder=5, label=f'F1 최대 (th={best_th:.2f})')
ax[0].axhline(y_test.mean(), color='gray', linestyle='--', label=f'무작위 기준선 ({y_test.mean():.4f})')
ax[0].set_xlabel('Recall'); ax[0].set_ylabel('Precision'); ax[0].set_title('Precision-Recall 곡선 (테스트셋)')
ax[0].legend()
cm = confusion_matrix(y_test, (prob >= best_th).astype(int))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax[1],
            xticklabels=['유지 예측', '탈퇴 예측'], yticklabels=['실제 유지', '실제 탈퇴'])
ax[1].set_title(f'혼동행렬 (임계값 {best_th:.2f})')
save('09_pr_curve_cm')
plt.show()
th_table.round(3)
""")

md("### 10-2. 위험 점수 상위 k% 점검 시 탈퇴 사업장 포착률 (실무 활용 관점)")
code(r"""
pcts = [1, 2, 3, 5, 10, 20, 30]
capture = [recall_at_top(y_test, prob, p) * 100 for p in pcts]
plt.figure(figsize=(7, 4))
plt.plot(pcts, capture, marker='o', color='#e6550d', label='모델 위험 점수 순')
plt.plot(pcts, pcts, linestyle='--', color='gray', label='무작위 점검')
for p, c in zip(pcts, capture):
    plt.text(p, c + 2, f'{c:.0f}%', ha='center')
plt.xlabel('점검 대상 비율 (위험 점수 상위 %)'); plt.ylabel('실제 탈퇴 사업장 포착률 (%)')
plt.title('상위 k% 사업장만 점검했을 때 찾아내는 탈퇴 사업장 비율')
plt.legend()
save('10_capture_curve')
plt.show()
pd.DataFrame({'상위 %': pcts, '포착률(%)': np.round(capture, 1), '배율(lift)': np.round(np.array(capture) / pcts, 1)})
""")

md("## 11. 주요 영향 요인: Feature Importance (7·10주차)")
code(r"""
fi = pd.Series(final.feature_importances_, index=FEATURES).sort_values(ascending=False)
fi.to_csv('results/feature_importance.csv', encoding='utf-8-sig')

plt.figure(figsize=(8, 6))
sns.barplot(x=fi.values, y=fi.index, color='#3182bd')
plt.title('최종 모델(RandomForest + FI-SMOTE) 특성 중요도')
plt.ylabel('')
save('11_feature_importance')
plt.show()
fi.round(4)
""")
code(r"""
# 상위 변수 3개의 값에 따른 실제 탈퇴율 (중요도의 '방향' 해석)
for col in fi.index[:3]:
    print('■', col)
    if df[col].nunique() <= 2:                       # 0/1 변수는 그대로 비교
        print((df.groupby(col)['탈퇴'].mean() * 100).round(3).to_string(), '\n')
    else:                                            # 연속형은 10분위로 나눠 비교
        q = pd.qcut(df[col].rank(method='first'), 10, labels=[f'{i}분위' for i in range(1, 11)])
        print((df.groupby(q)['탈퇴'].mean() * 100).round(3).to_string(), '\n')
""")

md(r"""
## 12. 추가 검증: 결과가 믿을 만한가?
앞의 평가는 같은 기준월(2026-07) 안에서 무작위로 나눈 테스트셋을 썼다. 실제로 쓰려면 **과거 데이터로 학습한 모델이 미래에도 통하는지**
확인해야 한다. 또 탈퇴의 절반이 건설업이고, 정답 정의에서 '사라진 사업장'을 제외했으므로 이 두 가지가 결과를 좌우하는지도 점검한다.

먼저 4장의 데이터 만들기 과정을 기준월만 바꿔 다시 쓸 수 있도록 함수로 묶는다.
""")
code(r"""
# 메모리 정리: 앞에서 불러온 월별 원본은 더 이상 쓰지 않음
import gc
del base, m1, m3, m4, fut, model
gc.collect()

def build_dataset(base_ym, m1_ym, m3_ym, m4_ym, fut_ym, missing_as_exit=False):
    b = load_month(base_ym)
    b = b[b['가입상태'] == '1']
    d = b.merge(lag_cols(load_month(m1_ym), '_m1'), on=KEY, how='left')
    d = d.merge(lag_cols(load_month(m3_ym), '_m3'), on=KEY, how='left')
    d = d.merge(lag_cols(load_month(m4_ym), '_m4'), on=KEY, how='left')
    f = load_month(fut_ym)
    d = d.merge(f[KEY + ['가입상태']].rename(columns={'가입상태': '가입상태_3개월후'}), on=KEY, how='left')
    if missing_as_exit:       # 사라진 사업장도 탈퇴로 간주
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
    d['인원증감률_1개월'] = rate(d['가입자수'], d['가입자수_m1'])
    d['인원증감률_3개월'] = rate(d['가입자수'], d['가입자수_m3'])
    d['인원증감률_4개월'] = rate(d['가입자수'], d['가입자수_m4'])
    d['고지금액증감률_3개월'] = rate(d['고지금액'], d['고지금액_m3'])
    d['최근상실자합'] = d['상실가입자수'] + d['상실가입자수_m1'].fillna(0)
    d['시도코드'] = d['시도코드'].astype(int)
    d['업종대분류'] = d['업종코드'].str[:2].astype(int)
    d['건설업'] = d['업종명'].fillna('').str.contains('공사|건설').astype(int)
    Xd = d[FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0)
    return Xd, d['탈퇴'], d
""")

md(r"""
### 12-1. 시간 기반 검증: 4월 기준으로 학습 → 7월 기준으로 평가
- 학습: 기준월 **2026-04** (과거 시점 2026-03, 01, 2025-12), 정답은 2026-07 상태
- 평가: 기준월 **2026-07** 전체 사업장 (앞에서 쓴 데이터), 정답은 2026-10 상태
- 두 기간의 정답 구간(4→7월, 7→10월)이 겹치지 않으므로, 실제로 "지난 분기 데이터로 만든 모델을 이번 분기에 적용"하는 상황과 같다.
""")
code(r"""
t = time.time()
X_past, y_past, d_past = build_dataset('202604', '202603', '202601', '202512', '202607')
print(f'학습(4월 기준): {len(X_past):,}곳, 탈퇴율 {y_past.mean()*100:.3f}%  ({time.time()-t:.0f}s)')
print(f'평가(7월 기준): {len(X):,}곳, 탈퇴율 {y.mean()*100:.3f}%')

Xp, yp = fi_smote_resample(X_past, y_past, sampling_strategy=0.1, random_state=42)
oot_model = RandomForestClassifier(random_state=42, n_jobs=-1, **gs.best_params_)
oot_model.fit(Xp, yp)
prob_oot = oot_model.predict_proba(X)[:, 1]
oot = evaluate(y, prob_oot)
del oot_model, Xp, yp; gc.collect()

compare = pd.DataFrame({'무작위 분할 (7월 안에서 8:2)': final_metrics, '시간 기반 (4월 학습 → 7월 평가)': oot}).T
compare.round(4)
""")
code(r"""
cap_oot = [recall_at_top(y, prob_oot, p) * 100 for p in pcts]
plt.figure(figsize=(7, 4))
plt.plot(pcts, capture, marker='o', color='#e6550d', label='무작위 분할 테스트셋')
plt.plot(pcts, cap_oot, marker='s', color='#3182bd', label='시간 기반 (4월 학습 → 7월 평가)')
plt.plot(pcts, pcts, linestyle='--', color='gray', label='무작위 점검')
for p, c in zip(pcts, cap_oot):
    plt.text(p, c - 6, f'{c:.0f}%', ha='center', color='#3182bd')
plt.xlabel('점검 대상 비율 (위험 점수 상위 %)'); plt.ylabel('실제 탈퇴 사업장 포착률 (%)')
plt.title('시간 기반 검증에서도 포착률이 유지되는가')
plt.legend()
save('12_time_validation')
plt.show()
pd.DataFrame({'상위 %': pcts, '무작위 분할(%)': np.round(capture, 1), '시간 기반(%)': np.round(cap_oot, 1)})
""")

md(r"""
### 12-2. 건설업을 빼도 예측이 되는가
탈퇴의 절반이 건설·공사업이므로, 모델이 "건설업이면 위험"만 배운 것은 아닌지 확인한다.
최종 모델의 테스트셋 예측을 건설업 / 비건설업으로 나눠 평가한다.
""")
code(r"""
is_con = df.loc[X_test.index, '건설업'].values == 1
rows = []
for name, mask in [('전체', np.ones(len(y_test), bool)), ('건설·공사업', is_con), ('건설업 제외', ~is_con)]:
    r = evaluate(y_test[mask], prob[mask])
    r.update({'구분': name, '사업장 수': int(mask.sum()), '탈퇴 수': int(y_test[mask].sum()),
              '탈퇴율(%)': y_test[mask].mean() * 100})
    rows.append(r)
seg = pd.DataFrame(rows).set_index('구분')[['사업장 수', '탈퇴 수', '탈퇴율(%)', 'PR-AUC', 'ROC-AUC', 'F1', 'Recall@상위5%']]
seg.round(4)
""")

md(r"""
### 12-3. 민감도 분석: 사라진 사업장까지 탈퇴로 보면?
3개월 뒤 파일에서 사라진 40,135곳을 제외했었다. 이들을 모두 탈퇴로 간주(넓은 정의)해도 같은 결론이 나오는지 본다.
넓은 정의에서는 탈퇴 비율이 7%대로 올라가 불균형이 약해지므로, 오버샘플링 없이 같은 랜덤포레스트로 비교한다.
""")
code(r"""
X_w, y_w, _ = build_dataset('202607', '202606', '202604', '202603', '202610', missing_as_exit=True)
print(f'넓은 정의: {len(X_w):,}곳, 탈퇴율 {y_w.mean()*100:.2f}%')
Xw_tr, Xw_te, yw_tr, yw_te = train_test_split(X_w, y_w, test_size=0.2, stratify=y_w, random_state=42)
wide_model = RandomForestClassifier(random_state=42, n_jobs=-1, **gs.best_params_)
wide_model.fit(Xw_tr, yw_tr)
prob_w = wide_model.predict_proba(Xw_te)[:, 1]
wide = evaluate(yw_te, prob_w)
wide_fi = pd.Series(wide_model.feature_importances_, index=FEATURES).sort_values(ascending=False)
del wide_model; gc.collect()

sens = pd.DataFrame({'좁은 정의 (명시적 탈퇴만)': final_metrics, '넓은 정의 (사라짐 포함)': wide}).T
sens['탈퇴율(%)'] = [y.mean() * 100, y_w.mean() * 100]
print('넓은 정의 중요도 상위 5:', list(wide_fi.index[:5]))
sens.round(4)
""")
code(r"""
extra = pd.concat([compare.assign(분석='시간 기반 검증'), seg.reset_index().rename(columns={'구분': '세부'}).assign(분석='업종 분리'),
                   sens.assign(분석='민감도')], ignore_index=False)
extra.to_csv('results/extra_validation.csv', encoding='utf-8-sig')
pd.DataFrame({'상위 %': pcts, '무작위 분할(%)': capture, '시간 기반(%)': cap_oot}).to_csv(
    'results/time_validation_capture.csv', index=False, encoding='utf-8-sig')
wide_fi.to_csv('results/wide_definition_importance.csv', encoding='utf-8-sig')
""")

md(r"""
## 13. 결과 저장
""")
code(r"""
summary = pd.Series(final_metrics)
summary['best_threshold'] = best_th
summary['best_sampler'] = best_sampler
summary['n_total'] = len(df)
summary['exit_rate'] = y.mean()
summary.to_csv('results/final_summary.csv', encoding='utf-8-sig')
summary
""")

nb = nbf.v4.new_notebook()
nb['cells'] = cells
nb['metadata'] = {'kernelspec': {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'},
                  'language_info': {'name': 'python'}}
nbf.write(nb, sys.argv[1])
print('written', len(cells), 'cells')
