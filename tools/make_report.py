import os, sys
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, 'docs', '202444085_김철중_기말프로젝트_보고서.docx')
FIG = os.path.join(ROOT, 'figures')
RES = os.path.join(ROOT, 'results')
FONT = '맑은 고딕'

cv = pd.read_csv(os.path.join(RES, 'model_cv_result.csv'), encoding='utf-8-sig')
imb = pd.read_csv(os.path.join(RES, 'imbalance_result.csv'), encoding='utf-8-sig')
fin = pd.read_csv(os.path.join(RES, 'final_summary.csv'), encoding='utf-8-sig', index_col=0).iloc[:, 0]
fin = pd.to_numeric(fin, errors='coerce')
fi =pd.read_csv(os.path.join(RES, 'feature_importance.csv'), encoding='utf-8-sig', index_col=0).iloc[:, 0]
th = pd.read_csv(os.path.join(RES, 'threshold_table.csv'), encoding='utf-8-sig')
rep = pd.read_csv(os.path.join(RES, 'imbalance_cv5_folds.csv'), encoding='utf-8-sig')
wins = pd.read_csv(os.path.join(RES, 'imbalance_cv5_wins.csv'), encoding='utf-8-sig', index_col=0)
extra = pd.read_csv(os.path.join(RES, 'extra_validation.csv'), encoding='utf-8-sig', index_col=0)
tcap = pd.read_csv(os.path.join(RES, 'time_validation_capture.csv'), encoding='utf-8-sig')
tv = extra[extra['분석'] == '시간 기반 검증']
seg = extra[extra['분석'] == '업종 분리'].set_index('세부')
sens = extra[extra['분석'] == '민감도']
wide_fi = pd.read_csv(os.path.join(RES, 'wide_definition_importance.csv'), encoding='utf-8-sig', index_col=0).iloc[:, 0]

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin = sec.bottom_margin = Cm(2.2)


def set_font(run_or_style, size=None, bold=None, color=None):
    f = run_or_style.font
    f.name = FONT
    rpr = run_or_style.element.get_or_add_rPr() if hasattr(run_or_style.element, 'get_or_add_rPr') else run_or_style.element.rPr
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts'); rpr.append(rfonts)
    for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        rfonts.set(qn(a), FONT)
    if size: f.size = Pt(size)
    if bold is not None: f.bold = bold
    if color: f.color.rgb = RGBColor.from_string(color)


normal = doc.styles['Normal']
set_font(normal, 10.5)
normal.paragraph_format.space_after = Pt(4)
normal.paragraph_format.line_spacing = 1.4
for name, size in [('Heading 1', 14), ('Heading 2', 11.5)]:
    st = doc.styles[name]
    set_font(st, size, True, '1F3864')
    st.paragraph_format.space_before = Pt(12 if name == 'Heading 1' else 8)
    st.paragraph_format.space_after = Pt(4)
    st.paragraph_format.keep_with_next = True


def P(text='', bold_prefix=None, align=None, size=None, italic=False, color=None, after=None):
    p = doc.add_paragraph()
    if bold_prefix:
        r = p.add_run(bold_prefix); set_font(r, size, True)
    r = p.add_run(text); set_font(r, size, None, color); r.italic = italic
    if align: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    return p


def B(text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    if bold_prefix:
        r = p.add_run(bold_prefix); set_font(r, None, True)
    r = p.add_run(text); set_font(r)
    p.paragraph_format.space_after = Pt(2)
    return p


def H(text, level=1):
    h = doc.add_heading(text, level=level)
    for r in h.runs: set_font(r, 14 if level == 1 else 11.5, True, '1F3864')
    return h


def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def T(df, caption, widths=None, highlight_rows=()):
    cap = P(caption, align=WD_ALIGN_PARAGRAPH.CENTER, size=9.5, after=2)
    cap.runs[0].bold = True
    cap.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(df.columns))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, c in enumerate(df.columns):
        cell = t.rows[0].cells[i]
        cell.text = ''
        r = cell.paragraphs[0].add_run(str(c)); set_font(r, 9, True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        shade(cell, 'D9E2F3')
    for ri, row in enumerate(df.itertuples(index=False)):
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''
            r = cells[i].paragraphs[0].add_run(str(v)); set_font(r, 9, ri in highlight_rows)
            cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if i > 0 else WD_ALIGN_PARAGRAPH.LEFT
            if ri in highlight_rows: shade(cells[i], 'FCE4D6')
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Cm(w)
    # 표가 페이지 사이에서 잘리지 않도록: 마지막 행 전까지 keep_with_next, 행 분할 금지
    for ri, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement('w:cantSplit'); trPr.append(cs)
        if ri < len(t.rows) - 1:
            for c in row.cells:
                for p in c.paragraphs: p.paragraph_format.keep_with_next = True
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
    P('', after=0)
    return t


def F(name, caption, width=15.5):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(os.path.join(FIG, name), width=Cm(width))
    c = P(caption, align=WD_ALIGN_PARAGRAPH.CENTER, size=9.5, after=8)
    c.runs[0].bold = True


f3 = lambda x: f'{x:.3f}'
f4 = lambda x: f'{x:.4f}'

# ───────────────────────── 표지/제목 ─────────────────────────
P('데이터분석 기말대체 프로젝트 최종보고서', align=WD_ALIGN_PARAGRAPH.CENTER, size=10, color='7F7F7F', after=6)
t = P('국민연금 가입 사업장 데이터를 활용한', align=WD_ALIGN_PARAGRAPH.CENTER, size=17, after=0); t.runs[0].bold = True
t = P('사업장 탈퇴 3개월 조기 예측', align=WD_ALIGN_PARAGRAPH.CENTER, size=17, after=4); t.runs[0].bold = True
P('Early Prediction of Workplace Withdrawal within Three Months Using National Pension Workplace Data',
  align=WD_ALIGN_PARAGRAPH.CENTER, size=10, italic=True, color='404040', after=8)
P('인하공업전문대학 컴퓨터정보공학과  202444085 김철중', align=WD_ALIGN_PARAGRAPH.CENTER, size=10.5, after=2)
P('2026년 2학기 데이터분석 (이수정 교수님)', align=WD_ALIGN_PARAGRAPH.CENTER, size=9.5, color='595959', after=10)

abs_text = (
    f"국민연금공단이 매월 공개하는 「국민연금 가입 사업장 내역」 5개월분을 사업장 단위로 연결하여, "
    f"기준월(2026년 7월)에 등록된 사업장 {int(fin['n_total']):,}곳 중 3개월 안에 가입을 탈퇴할 사업장을 예측하였다. "
    f"탈퇴 비율이 {fin['exit_rate']*100:.2f}%에 불과한 극단적 불균형 문제이므로 정확도 대신 Precision, Recall, F1, MCC, PR-AUC로 평가하였다. "
    f"7종의 분류 알고리즘을 층화 5-겹 교차검증으로 비교하고, SMOTE·ADASYN·FI-SMOTE 등 불균형 처리 기법을 비교한 결과, "
    f"GridSearchCV로 튜닝한 RandomForest에 FI-SMOTE를 결합한 모델이 테스트셋에서 F1 {fin['F1']:.3f}, MCC {fin['MCC']:.3f}, "
    f"ROC-AUC {fin['ROC-AUC']:.3f}를 기록하였다. 위험 점수 상위 5% 사업장만 점검해도 실제 탈퇴 사업장의 "
    f"{fin['Recall@상위5%']*100:.1f}%를 찾아낼 수 있었으며, 최근 신규 등록 여부·업력·가입자 규모가 가장 중요한 요인이었다. "
    f"층화 5-겹 반복 검증에서 FI-SMOTE는 5번 모두 SMOTE·ADASYN보다 F1·MCC·PR-AUC가 높았고, 2026년 4월 기준으로 학습해 7월 기준으로 평가한 "
    f"시간 기반 검증에서도 ROC-AUC {tv.iloc[1]['ROC-AUC']:.3f}, 상위 5% 포착률 {tv.iloc[1]['Recall@상위5%']*100:.1f}%로 성능이 유지되었다.")
p = P(abs_text, bold_prefix='요 약  ', size=9.5, after=4)
p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.right_indent = Cm(0.8)
p = P('사업장 탈퇴 예측, 폐업 예측, 국민연금, 공공데이터, 클래스 불균형, FI-SMOTE, 랜덤포레스트', bold_prefix='Keyword  ', size=9.5, after=10)
p.paragraph_format.left_indent = Cm(0.8)

# ───────────────────────── 1. 서론 ─────────────────────────
H('1. 서론 (Introduction)')
H('1.1 분석 배경 및 필요성', 2)
P('사업장의 폐업과 휴업은 근로자의 실직, 거래처의 미수금, 지역 상권의 공실로 이어진다. 그런데 폐업 위험을 판단하는 데 주로 쓰이는 '
  '재무제표는 1년 또는 분기 단위로만 갱신되고, 소규모 사업장은 아예 재무정보가 공개되지 않는 경우가 많다. '
  '반면 국민연금 가입 사업장 정보는 전국 약 59만 개 사업장의 가입자 수, 고지금액, 입·퇴사자 수를 매월 공개한다. '
  '사업장의 인원과 급여 흐름이 매달 기록되는 셈이므로, 이를 시계열로 연결하면 재무정보 없이도 사업장의 "이상 신호"를 빠르게 포착할 수 있다.')
P('본 프로젝트의 질문은 다음과 같다: ', bold_prefix=None)
q = P('"지금 국민연금에 가입된 사업장 가운데, 3개월 안에 탈퇴할 사업장을 미리 찾아낼 수 있는가?"', italic=True, after=6)
q.paragraph_format.left_indent = Cm(1)

H('1.2 기존 연구', 2)
P('폐업 예측에 머신러닝을 적용한 국내 연구는 다음과 같이 사용 데이터에 따라 나뉜다.')
rel = pd.DataFrame([
    ['공현정 외 (2023) [1]', '전자결제서비스 이용 사업자의 결제·재무 정보', '비재무정보를 추가하면 정확도 향상, XGBoost 최고'],
    ['박준식 외 (2023) [2]', '소상공인 실태조사(2019) 도소매업 설문', '여러 ML 알고리즘 + 불균형 완화 기법 적용'],
    ['Bang 외 (2018) [3]', '행정안전부 인허가 데이터(서울 치킨집)', 'FDA가 민감도·특이도 균형 최고'],
    ['본 연구', '국민연금 가입 사업장 월별 공개 데이터 (전 업종·전국)', '월별 패널로 인원·급여 흐름 변수 생성, FI-SMOTE 적용'],
], columns=['연구', '데이터', '특징'])
T(rel, '[표 1] 기존 폐업 예측 연구와 본 연구 비교', widths=[3.3, 6.3, 7], highlight_rows=(3,))
P('기존 연구는 특정 업종(치킨집, 도소매업)이나 특정 플랫폼 가입자(전자결제)에 한정되거나, 1회성 설문 자료를 사용하였다. '
  '본 연구는 누구나 내려받을 수 있는 공공데이터만으로 전 업종·전국 사업장을 다루고, 매월 갱신되는 특성을 이용해 '
  '"최근 인원 증감", "최근 신규 등록 여부" 같은 시간 흐름 변수를 만들었다는 점에서 차별화된다. '
  '선행연구 검색(KoreaScience, KCI, 교보스콜라) 결과 이 데이터를 머신러닝 기반 탈퇴 예측에 사용한 연구는 찾지 못했다.')

H('1.3 분석 목적', 2)
B('3개월 내 탈퇴 사업장을 예측하는 분류 모델을 만들고, 교안에서 배운 알고리즘들의 성능을 비교한다.')
B('탈퇴 비율 0.4%의 극단적 불균형 문제에서 오버샘플링 기법(본인이 1학기에 제안한 FI-SMOTE 포함)의 효과를 검증한다.')
B('탈퇴에 영향을 주는 주요 요인을 찾고, 고용지원 기관이나 거래 기업이 활용할 수 있는 조기 경보 방안을 제시한다.')

# ───────────────────────── 2. 데이터 및 방법 ─────────────────────────
H('2. 데이터 및 분석 방법 (Data & Methodology)')
H('2.1 데이터 개요', 2)
B('국민연금공단, 「국민연금공단_국민연금 가입 사업장 내역」, 공공데이터포털 파일데이터(CSV, 월간 갱신, 이용허락범위 제한 없음)', '출처: ')
B('가입자 수 3인 이상 법인 사업장, 10인 이상 개인 사업장(2025년 7월 이후 기준)', '공개 범위: ')
B('2026년 3·4·6·7·10월분 5개 파일 (각 약 59만 행 × 22열, 약 110MB) + 시간 기반 검증용 2025년 12월·2026년 1월분', '사용 파일: ')
B('사업장명, 사업자번호(앞 6자리), 가입상태(1 등록/2 탈퇴), 주소·법정동코드, 법인/개인, 업종코드·업종명, '
  '적용일자, 재등록일자, 탈퇴일자, 가입자 수, 당월 고지금액, 신규취득자 수, 상실가입자 수', '주요 항목: ')

H('2.2 데이터 전처리와 정답 정의', 2)
P('월별 파일에는 사업장 고유번호가 없으므로 "사업자번호 앞 6자리 + 사업장명 + 법정동코드 + 업종코드"를 결합한 키로 '
  '같은 사업장을 연결하였다. 키가 중복되는 행(월당 약 300행)은 어느 사업장인지 구분할 수 없어 제거하였다(교안 3주차 중복 데이터 처리). '
  '결측치는 재등록일자·탈퇴일자에만 있었고, "해당 없음"을 뜻하므로 삭제하지 않고 재등록 여부 변수로 바꾸었다(3주차 이상데이터 처리의 변수화).')
P('정답(label)은 다음과 같이 정의하였다.')
B('기준월 T = 2026년 7월에 가입상태가 1(등록)인 사업장 553,676곳을 대상으로 한다.')
B('3개월 뒤(2026년 10월) 파일에서 가입상태가 2(탈퇴)이면 1, 여전히 1(등록)이면 0으로 둔다.')
B('2026년 10월 파일에서 사라진 40,135곳은 실제 탈퇴인지, 공개 범위에서 빠진 것인지, 사업장명 변경인지 알 수 없으므로 제외하였다.')
P(f'최종 분석 대상은 {int(fin["n_total"]):,}곳이며, 이 중 3개월 안에 탈퇴한 사업장은 2,033곳({fin["exit_rate"]*100:.2f}%)이다.')

H('2.3 파생변수', 2)
P('과거 시점(T-1, T-3, T-4) 파일을 기준월에 병합(5주차 merge)하여 다음 17개 입력 변수를 만들었다.')
feat = pd.DataFrame([
    ['규모·급여', '가입자수, 1인당고지금액(고지금액÷가입자수), 법인여부'],
    ['인원 흐름', '신규취득자수, 상실가입자수, 취득률, 상실률, 최근상실자합(T와 T-1)'],
    ['변화율', '인원증감률(1·3·4개월), 고지금액증감률(3개월)'],
    ['이력', '업력(적용일자부터 기준월까지 년), 재등록여부, 신규진입(3개월 전 파일에 없음)'],
    ['범주', '시도코드, 업종대분류(업종코드 앞 2자리)'],
], columns=['구분', '변수'])
T(feat, '[표 2] 입력 변수 목록', widths=[2.8, 13.8])

H('2.4 탐색적 데이터 분석 (EDA)', 2)
F('01_class_ratio.png', '[그림 1] 3개월 후 상태 비율 — 전부 "유지"라고 예측해도 정확도 99.6%', width=5.5)
P('탈퇴 비율이 0.4%이므로 아무것도 학습하지 않은 모델의 정확도도 99.6%가 된다(1주차 FDS 예시와 같은 상황). '
  '따라서 정확도는 모델 비교에 쓸 수 없으며, 소수 클래스를 얼마나 잘 찾는지를 보여주는 Recall, Precision, F1, MCC와 '
  '임계값에 영향을 받지 않는 PR-AUC(Average Precision)를 주 지표로 정하였다.')
F('02_size_age_rate.png', '[그림 2] 가입자 규모별(왼쪽)·업력별(오른쪽) 3개월 내 탈퇴율', width=14.5)
P('규모가 작을수록, 업력이 짧을수록 탈퇴율이 뚜렷하게 높았다. 1~4명 사업장의 탈퇴율은 0.62%로 100명 이상 사업장(0.04%)의 약 16배이고, '
  '업력 1년 미만 사업장의 탈퇴율은 2.98%로 20년 이상 사업장(0.05%)의 약 60배였다. '
  '가입자가 0명인데 등록 상태로 남아 있는 사업장 93곳은 77.4%가 3개월 안에 탈퇴하여 가장 강한 신호를 보였다.')
F('03_industry_top15.png', '[그림 3] 탈퇴율 상위 15개 업종 (사업장 1,000곳 이상 업종)', width=11)
P('탈퇴율 상위 업종은 대부분 건설·공사업이었다. 건설·공사업은 전체 사업장의 13.9%지만 탈퇴 사업장의 49.0%를 차지하였다. '
  '건설업은 공사 현장마다 사업장을 따로 등록하고 공사가 끝나면 탈퇴하는 경우가 많기 때문이다. '
  '같은 이유로 최근 3개월 안에 새로 등록된 사업장의 탈퇴율(1.31%)이 기존 사업장(0.25%)보다 5배 이상 높았다. '
  '즉 이 데이터의 "탈퇴"는 폐업뿐 아니라 현장 종료·휴업·이전을 함께 포함한다.')
F('05_boxplots.png', '[그림 4] 탈퇴 여부에 따른 1인당 고지금액·업력·3개월 인원 증감률 분포', width=15)
F('06_corr_heatmap.png', '[그림 5] 변수 간 상관계수 히트맵', width=11)
P('탈퇴와 선형 상관계수의 절댓값이 0.1을 넘는 변수는 없었다. 하나의 변수로 설명되는 문제가 아니라 여러 신호의 조합을 봐야 하므로, '
  '비선형 관계와 변수 간 상호작용을 학습하는 트리 기반 앙상블 모델이 유리할 것으로 예상하였다.')

H('2.5 분석 기법 및 모델링', 2)
B('탈퇴 비율을 유지하도록 학습 80% / 테스트 20%로 층화 분할 (테스트 102,709곳, 탈퇴 407곳)', '데이터 분할: ')
B('로지스틱 회귀, 결정트리, 랜덤포레스트, AdaBoost, XGBoost, LightGBM, Soft Voting(RF+XGB+LGBM) — 학습셋에서 층화 추출한 15만 행으로 층화 5-겹 교차검증', '모델 비교(7·9·10주차): ')
B('없음 / class_weight / SMOTE / ADASYN / FI-SMOTE — 오버샘플링은 학습셋에만 적용하고 소수 클래스를 다수 클래스의 10%까지 증식', '불균형 처리: ')
B('학습셋을 층화 5-겹으로 나눠 RandomForest × {없음, SMOTE, ADASYN, FI-SMOTE}를 5번 반복하여 평균·표준편차·우위 횟수 비교', '반복 검증: ')
B('랜덤포레스트 n_estimators·min_samples_leaf·max_features 12개 조합, PR-AUC 기준 3-겹 교차검증 GridSearchCV (9주차)', '튜닝: ')
B('시간 기반 검증(4월 기준 학습 → 7월 기준 평가), 건설업 분리 평가, 정답 정의 민감도 분석', '추가 검증: ')
B('Precision, Recall, F1, MCC, ROC-AUC, PR-AUC, 그리고 실무 관점의 "위험 점수 상위 k% 점검 시 포착률(Recall@k%)"', '평가지표: ')
P('FI-SMOTE는 본인이 2026년 1학기에 제안한 오버샘플링 기법[7]이다. 랜덤포레스트의 특성 중요도로 중요 변수를 고른 뒤, '
  '중요 변수 공간에서 경계에 가까운 소수 샘플일수록 더 많이 합성하고(ADASYN 방식[5]), 중요 변수는 Beta(1, 1+scale×중요도) 분포의 작은 '
  '보간 계수로 원본 근처에 고정하며 비중요 변수는 Uniform(0,1)로 자유롭게 보간한다. 이번 프로젝트에서는 대용량 데이터에 맞게 '
  '증식 비율 인자를 추가하고 생성 과정을 벡터화하였다.')

# ───────────────────────── 3. 결과 ─────────────────────────
H('3. 분석 결과')
H('3.1 모델 성능 비교', 2)
cvt = cv[['model', 'accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'average_precision']].copy()
cvt.columns = ['모델', 'Accuracy', 'Precision', 'Recall', 'F1', 'ROC-AUC', 'PR-AUC']
for c in cvt.columns[1:]: cvt[c] = cvt[c].map(f4)
T(cvt, '[표 3] 층화 5-겹 교차검증 결과 (임계값 0.5, PR-AUC 순)', widths=[3.6, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1], highlight_rows=(0, 1))
F('07_model_compare.png', '[그림 6] 정확도(왼쪽)는 모든 모델이 99.6% 근처 — PR-AUC·ROC-AUC(오른쪽)로 비교')
P(f'정확도는 모든 모델이 99.58~99.62%로 차이가 없었다. PR-AUC 기준으로는 Soft Voting({cv.iloc[0]["average_precision"]:.3f})과 '
  f'랜덤포레스트({cv.iloc[1]["average_precision"]:.3f})가 가장 높았고, 무작위 기준선(0.004)의 약 45배였다. '
  '단일 결정트리와 로지스틱 회귀는 앙상블보다 크게 낮았다. 반면 임계값 0.5에서 Recall은 대부분 10% 미만이었는데, '
  '소수 클래스를 거의 "유지"로 예측하는 다수결 편향 때문이다.')

H('3.2 불균형 처리 기법 비교', 2)
it = imb[['모델', '불균형처리', 'PR-AUC', 'Precision', 'Recall', 'F1', 'MCC', 'Recall@상위5%']].copy()
for c in it.columns[2:]: it[c] = it[c].map(f3)
hl = tuple(i for i, r in imb.reset_index().iterrows() if r['불균형처리'] == 'FI-SMOTE')
T(it, '[표 4] 불균형 처리 기법별 테스트셋 성능 (임계값 0.5)', widths=[2.6, 2.6, 1.8, 1.9, 1.7, 1.6, 1.6, 2.6], highlight_rows=hl)
F('08_imbalance_compare.png', '[그림 7] 불균형 처리 기법별 PR-AUC·F1·Recall@상위5%')
B('SMOTE와 ADASYN은 오히려 원본(없음)보다 PR-AUC가 떨어졌다. 무작위 선형 보간이 결정 경계 근처에 노이즈를 만든 것으로 보인다.')
B('오버샘플링 3종 중에서는 두 모델 모두 FI-SMOTE의 PR-AUC가 가장 높았다(LightGBM 0.177, RandomForest 0.164).')
B('RandomForest + FI-SMOTE는 F1 0.223, MCC 0.224로 전체 10개 조합 중 1위였다.')
B('다만 순위 지표인 PR-AUC 자체는 오버샘플링을 하지 않은 RandomForest(0.186)가 가장 높았다. 오버샘플링의 효과는 순위를 바꾸기보다 '
  '임계값 0.5에서 놓치던 탈퇴 사업장을 더 잡아내는 데(Recall 0.05 → 0.19) 있었다. 이는 FI-SMOTE 원 논문[7]에서 F1·MCC는 1위였지만 '
  'AUC는 SMOTE 계열과 비슷했던 결과와 같은 경향이다.')
P('위 결과는 테스트셋 하나(탈퇴 407곳)에서 나온 것이므로 우연일 수 있다. 그래서 학습셋을 층화 5-겹으로 나눠 RandomForest로 5번 반복 비교하였다.')
order = ['없음', 'SMOTE', 'ADASYN', 'FI-SMOTE']
gm = rep.groupby('불균형처리')[['PR-AUC', 'F1', 'MCC', 'Recall', 'Recall@상위5%']]
mn, sd = gm.mean().loc[order], gm.std().loc[order]
r5 = pd.DataFrame({'불균형처리': order})
for c in ['PR-AUC', 'F1', 'MCC', 'Recall', 'Recall@상위5%']:
    r5[c] = [f'{m:.3f} ± {d:.3f}' for m, d in zip(mn[c], sd[c])]
T(r5, '[표 5] 층화 5-겹 반복 비교 (RandomForest, 평균 ± 표준편차, 임계값 0.5)', widths=[2.6, 2.8, 2.8, 2.8, 2.8, 2.8], highlight_rows=(3,))
F('08b_imbalance_cv5.png', '[그림 8] 5-겹 반복 비교: fold별 PR-AUC·F1·MCC 분포')
w = lambda o, m: int(wins.loc[f'FI-SMOTE > {o}', m])
B(f'FI-SMOTE는 5번 모두 SMOTE·ADASYN보다 PR-AUC, F1, MCC가 높았다 (SMOTE 대비 {w("SMOTE","PR-AUC")}/{w("SMOTE","F1")}/{w("SMOTE","MCC")}회, '
  f'ADASYN 대비 {w("ADASYN","PR-AUC")}/{w("ADASYN","F1")}/{w("ADASYN","MCC")}회). 표준편차도 가장 작아 가장 안정적이었다.')
B(f'오버샘플링 없음과 비교하면 F1은 {w("없음","F1")}/5회, MCC는 {w("없음","MCC")}/5회 높았지만 PR-AUC는 {w("없음","PR-AUC")}/5회로 낮았다. '
  '테스트셋 결과와 같은 결론이다: FI-SMOTE는 순위 성능을 유지하면서 임계값 기준의 탐지 성능(F1·MCC)을 가장 크게 높인다.')

H('3.3 최종 모델과 임계값 선택', 2)
P('GridSearchCV 결과 랜덤포레스트의 최적 파라미터는 n_estimators=200, min_samples_leaf=5, max_features="sqrt"였다(교차검증 PR-AUC 0.181). '
  '이 파라미터로 FI-SMOTE를 적용한 전체 학습셋을 다시 학습하여 테스트셋으로 평가하였다.')
fm = pd.DataFrame([[f3(fin['PR-AUC']), f3(fin['ROC-AUC']), f3(fin['Precision']), f3(fin['Recall']), f3(fin['F1']), f3(fin['MCC']),
                    f'{fin["Recall@상위5%"]*100:.1f}%']],
                  columns=['PR-AUC', 'ROC-AUC', 'Precision', 'Recall', 'F1', 'MCC', '상위 5% 포착률'])
T(fm, '[표 6] 최종 모델(RandomForest 튜닝 + FI-SMOTE) 테스트셋 성능 (임계값 0.5)')
F('09_pr_curve_cm.png', '[그림 9] Precision-Recall 곡선(왼쪽)과 F1 최대 임계값의 혼동행렬(오른쪽)')
tt = th.copy()
for c in ['Precision', 'Recall', 'F1']: tt[c] = tt[c].map(f3)
tt['경보 사업장 수'] = tt['경보 사업장 수'].map(lambda x: f'{x:,}')
T(tt, '[표 7] 임계값에 따른 Precision·Recall 트레이드오프 (테스트셋 102,709곳)', widths=[2.5, 2.8, 2.8, 2.8, 3.5])
P('임계값을 낮추면 더 많은 탈퇴 사업장을 찾지만(Recall↑) 잘못 경보하는 사업장도 늘어난다(Precision↓). '
  'F1이 최대가 되는 임계값은 0.48(F1 0.234)이었다. 1주차 교안의 FDS 예시처럼 놓치는 비용이 크다면 임계값을 0.2까지 낮춰 '
  'Recall 46%를 확보하는 운영도 가능하다.')
F('10_capture_curve.png', '[그림 10] 위험 점수 상위 k% 사업장만 점검했을 때 실제 탈퇴 사업장 포착률', width=11)
cap = pd.DataFrame([[1, '37.3%', '37.3배'], [2, '49.4%', '24.7배'], [3, '55.8%', '18.6배'], [5, '62.9%', '12.6배'],
                    [10, '69.0%', '6.9배'], [20, '76.9%', '3.8배']], columns=['점검 대상(상위 %)', '탈퇴 사업장 포착률', '무작위 대비'])
T(cap, '[표 8] 상위 k% 점검 시 포착률과 무작위 점검 대비 효율', widths=[4, 4, 4])

H('3.4 주요 영향 요인 (Feature Importance)', 2)
F('11_feature_importance.png', '[그림 11] 최종 모델의 특성 중요도', width=10.5)
top = fi.head(6)
fit = pd.DataFrame({'순위': range(1, 7), '변수': top.index, '중요도': top.values.round(3)})
T(fit, '[표 9] 특성 중요도 상위 6개', widths=[2, 6, 3])
B('최근 3개월 안에 새로 등록된 사업장의 탈퇴율은 1.31%로 기존 사업장(0.25%)의 5배였다. 공사 현장처럼 한시적으로 등록되는 사업장이 많기 때문이다.', '1순위 신규진입 (0.156): ')
B('업력 하위 10% 사업장의 탈퇴율은 2.26%, 상위 10%는 0.04%로 약 55배 차이가 났다.', '2순위 업력 (0.139): ')
B('규모가 작을수록 탈퇴율이 높았다(1~4명 0.62% vs 100명 이상 0.04%).', '3순위 가입자수 (0.100): ')
B('입사·퇴사 흐름과 급여 총액의 변화가 그다음으로 중요했다. 인원이 갑자기 들고 나거나 고지금액이 줄어드는 것이 이상 신호다.', '4~5순위 취득률·고지금액증감률: ')

H('3.5 추가 검증: 결과가 믿을 만한가', 2)
P('앞의 평가는 같은 기준월 안에서 무작위로 나눈 테스트셋을 사용했다. 실제로 쓰려면 과거로 학습한 모델이 미래에도 통해야 하고, '
  '탈퇴의 절반을 차지하는 건설업이나 정답 정의 방식이 결과를 좌우하지 않아야 한다. 이를 세 가지로 확인하였다.')
P('① 시간 기반 검증. ', bold_prefix=None).runs[0].bold = True
P('기준월 2026년 4월(과거 시점 3월·1월·2025년 12월, 정답은 7월 상태)로 데이터를 만들어 같은 방식(FI-SMOTE + 튜닝된 RandomForest)으로 학습하고, '
  '기준월 2026년 7월 전체 사업장으로 평가하였다. 두 기간의 정답 구간(4→7월, 7→10월)이 겹치지 않으므로 "지난 분기 데이터로 만든 모델을 이번 분기에 적용"하는 상황과 같다.')
tvt = tv[['PR-AUC', 'ROC-AUC', 'Precision', 'Recall', 'F1', 'MCC', 'Recall@상위5%']].copy()
for c in tvt.columns: tvt[c] = tvt[c].map(f3)
tvt.insert(0, '평가 방식', ['무작위 분할 (7월 안 8:2)', '시간 기반 (4월 학습 → 7월 평가)'])
T(tvt, '[표 10] 무작위 분할과 시간 기반 검증 비교 (임계값 0.5)', widths=[4.4, 1.7, 1.7, 1.8, 1.6, 1.5, 1.5, 2.3], highlight_rows=(1,))
F('12_time_validation.png', '[그림 12] 무작위 분할과 시간 기반 검증의 상위 k% 포착률 비교', width=11)
t5, r5_ = tv.iloc[1]['Recall@상위5%'] * 100, tv.iloc[0]['Recall@상위5%'] * 100
P(f'시간 기반 검증의 ROC-AUC는 {tv.iloc[1]["ROC-AUC"]:.3f}로 무작위 분할({tv.iloc[0]["ROC-AUC"]:.3f})과 거의 같았다. '
  f'PR-AUC({tv.iloc[1]["PR-AUC"]:.3f})와 상위 5% 포착률({t5:.1f}%)은 무작위 분할({tv.iloc[0]["PR-AUC"]:.3f}, {r5_:.1f}%)보다 조금 낮았지만, '
  f'상위 20% 이상에서는 차이가 거의 없었다. 과거 분기로 학습한 모델을 다음 분기에 그대로 써도 순위 성능이 대부분 유지된다는 뜻이다.')
P('② 건설업 분리. ', bold_prefix=None).runs[0].bold = True
sg = seg[['사업장 수', '탈퇴 수', '탈퇴율(%)', 'PR-AUC', 'ROC-AUC', 'F1', 'Recall@상위5%']].copy()
sg['사업장 수'] = sg['사업장 수'].map(lambda x: f'{int(x):,}'); sg['탈퇴 수'] = sg['탈퇴 수'].map(lambda x: f'{int(x):,}')
sg['탈퇴율(%)'] = sg['탈퇴율(%)'].map(lambda x: f'{x:.2f}')
for c in ['PR-AUC', 'ROC-AUC', 'F1', 'Recall@상위5%']: sg[c] = sg[c].map(f3)
sg = sg.reset_index().rename(columns={'세부': '구분'})
T(sg, '[표 11] 최종 모델의 업종별 테스트셋 성능 (Recall@상위5%는 각 집단 안에서 계산)', widths=[3.0, 2.1, 1.6, 1.8, 1.8, 1.9, 1.6, 2.6], highlight_rows=(2,))
nc = seg.loc['건설업 제외']
P(f'건설·공사업을 제외한 사업장에서도 ROC-AUC {nc["ROC-AUC"]:.3f}, 위험 점수 상위 5%에서 탈퇴의 {nc["Recall@상위5%"]*100:.1f}%를 찾아 '
  f'무작위(5%)의 약 {nc["Recall@상위5%"]*100/5:.0f}배 효율을 보였다. 모델이 "건설업이면 위험"만 배운 것이 아니라는 근거다. '
  '다만 건설업 안에서의 ROC-AUC가 더 높아, 현장 종료처럼 패턴이 뚜렷한 탈퇴를 더 잘 맞히는 경향은 있다.')
P('③ 정답 정의 민감도. ', bold_prefix=None).runs[0].bold = True
sn = sens[['탈퇴율(%)', 'PR-AUC', 'ROC-AUC', 'F1', 'MCC', 'Recall@상위5%']].copy()
sn['탈퇴율(%)'] = sn['탈퇴율(%)'].map(lambda x: f'{x:.2f}')
for c in ['PR-AUC', 'ROC-AUC', 'F1', 'MCC', 'Recall@상위5%']: sn[c] = sn[c].map(f3)
sn.insert(0, '정답 정의', ['좁은 정의 (명시적 탈퇴만)', '넓은 정의 (사라진 사업장 포함)'])
T(sn, '[표 12] 정답 정의에 따른 성능 비교', widths=[4.6, 1.8, 1.8, 1.8, 1.6, 1.6, 2.6])
wd = sens.iloc[1]
P(f'3개월 뒤 파일에서 사라진 사업장까지 탈퇴로 보면 탈퇴율이 {wd["탈퇴율(%)"]:.1f}%로 올라가고, PR-AUC는 {wd["PR-AUC"]:.3f}'
  f'(무작위 기준선 {wd["탈퇴율(%)"]/100:.3f}의 약 {wd["PR-AUC"]/(wd["탈퇴율(%)"]/100):.1f}배), ROC-AUC는 {wd["ROC-AUC"]:.3f}였다. '
  f'정답 정의를 바꿔도 예측력은 유지되었으며, 이때 가장 중요한 변수는 {wide_fi.index[0]}·{wide_fi.index[1]}·{wide_fi.index[2]} 순이었다. '
  '사라진 사업장은 인원이 줄어 공개 범위에서 빠진 경우가 많아, 상실률(퇴사 비율)이 중요해진 것으로 해석된다.')

# ───────────────────────── 4. 결론 ─────────────────────────
H('4. 결론')
H('4.1 결과 해석 및 의미', 2)
P('공개된 국민연금 사업장 데이터만으로 3개월 내 탈퇴 사업장을 무작위보다 훨씬 효율적으로 찾아낼 수 있었다. '
  f'최종 모델은 ROC-AUC {fin["ROC-AUC"]:.3f}, 위험 점수 상위 1%만 점검해도 탈퇴 사업장의 37%를, 상위 5%로 63%를 찾아냈다. '
  '반면 개별 사업장을 정확히 맞히는 지표(F1 0.23)는 높지 않은데, 탈퇴 여부가 데이터에 없는 요인(공사 일정, 경영 판단 등)에도 크게 좌우되기 때문이다. '
  '따라서 이 모델은 "확정 판정"보다 "점검 우선순위를 정하는 도구"로 쓰는 것이 적합하다. '
  f'이 결과는 과거 분기로 학습해 다음 분기에 적용한 시간 기반 검증(ROC-AUC {tv.iloc[1]["ROC-AUC"]:.3f}), 건설업 제외, 정답 정의 변경에서도 유지되었다.')
P('불균형 처리 측면에서는 단순 SMOTE·ADASYN이 오히려 순위 성능을 떨어뜨린 반면, 특성 중요도를 반영한 FI-SMOTE는 5-겹 반복 검증에서 '
  '5번 모두 SMOTE·ADASYN보다 PR-AUC·F1·MCC가 높았고 표준편차도 가장 작았다. 신용카드 사기(0.17%)에서 확인한 FI-SMOTE의 장점이 0.4% 수준의 다른 도메인에서도 재현된 것이다.')
H('4.2 실행 제언', 2)
B('매월 공개 데이터가 갱신될 때마다 위험 점수를 계산해 상위 1~5% 사업장을 고용지원 상담·체불 예방 점검 대상으로 우선 선정한다.', '고용센터·지자체: ')
B('거래처의 위험 점수를 외상 거래 한도나 납품 조건 결정의 보조 지표로 활용한다(재무제표 공개 전 조기 신호).', '거래 기업·금융기관: ')
B('업력 1년 미만, 1~4명 규모, 최근 인원 급변 사업장에 대해 경영 컨설팅·자금 지원을 연계한다.', '창업 지원 기관: ')
B('건설 현장 사업장은 탈퇴가 정상적인 현장 종료일 가능성이 높으므로, 실무 적용 시 건설업을 별도 모델로 분리하는 것이 바람직하다.', '모델 운영: ')
H('4.3 연구의 한계', 2)
B('"탈퇴"에는 폐업 외에 현장 종료, 휴업, 사업장 이전·통합이 섞여 있으며, 공개 데이터만으로는 구분할 수 없다.')
B('3개월 뒤 파일에서 사라진 사업장 40,135곳을 제외하였다. 이 중 일부는 실제 폐업일 수 있어 탈퇴율이 과소 추정되었을 수 있다.')
B('고지금액은 기준소득월액 상한이 적용되어 실제 급여와 다르며, 사업자번호가 6자리만 공개되어 사업장 연결 키에 오류가 있을 수 있다.')
B('시간 기반 검증은 두 분기(4→7월 학습, 7→10월 평가)만 확인하였다. 계절성과 경기 변화를 반영하려면 여러 기준월을 쌓아 학습하고 1년 이상의 기간으로 검증해야 한다.')
B('국세청 휴·폐업 조회 등 외부 정보와 결합하지 못해 "진짜 폐업"만을 정답으로 쓰지는 못했다.')

# ───────────────────────── 5. 참고문헌 ─────────────────────────
H('5. 참고문헌 및 데이터 출처')
refs = [
    '[1] 공현정, 황유진, 박성혁, "전자결제서비스 이용 사업자 폐업 예측에서 비재무정보 활용을 통한 머신러닝 모델의 정확도 향상에 관한 연구," 지능정보연구, 2023.',
    '[2] 박준식, 최진, 이성호, "머신러닝을 이용한 소상공인 창업기업의 폐업 예측모형개발: 도소매산업을 중심으로," 한국창업학회지, 제18권 제1호, pp. 31-56, 2023.',
    '[3] J. Bang, K. Son, S. J. A. Lee, H. Lee, S. Jo, "A Study on Predictive Modeling of Public Data: Survival of Fried Chicken Restaurants in Seoul," The Journal of Bigdata, 2018.',
    '[4] N. V. Chawla, K. W. Bowyer, L. O. Hall, W. P. Kegelmeyer, "SMOTE: Synthetic Minority Over-sampling Technique," Journal of Artificial Intelligence Research, Vol. 16, pp. 321-357, 2002.',
    '[5] H. He, Y. Bai, E. A. Garcia, S. Li, "ADASYN: Adaptive synthetic sampling approach for imbalanced learning," Proc. IEEE IJCNN, pp. 1322-1328, 2008.',
    '[6] L. Breiman, "Random Forests," Machine Learning, Vol. 45, No. 1, pp. 5-32, 2001.',
    '[7] 조규철, 김철중, "극한의 클래스 불균형 완화를 위한 피처 중요도 가중 기반 Beta 벡터 보간법," 한국컴퓨터정보학회 학술발표논문집, 2026.',
    '[8] 오세종, AI 시대의 파이썬 데이터분석, 한빛아카데미, 2025. / 이수정, 데이터분석 강의자료(1~12주차), 인하공업전문대학, 2026.',
]
for r in refs: P(r, size=9.5, after=2)
P('', after=2)
B('국민연금공단, 「국민연금공단_국민연금 가입 사업장 내역」, 공공데이터포털, https://www.data.go.kr/data/15083277/fileData.do', '데이터: ')
B('https://github.com/cholin3721/NPS-Workplace-Exit-Prediction', '소스코드: ')
B('Claude (Anthropic) — 주제 탐색과 선행연구 검색, 분석 코드 초안 작성, 결과 요약 및 보고서·발표자료 초안 작성에 활용. '
  '분석 설계, 정답 정의, 결과 해석은 본인이 검토하고 수정하였다.', '사용한 생성형 AI: ')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT)
print('saved', OUT)
