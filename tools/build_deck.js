const pptxgen = require('pptxgenjs');
const path = require('path');
const { applyTheme } = require(process.env.SKILL_DIR + '/scripts/apply_theme.js');

const ROOT = process.argv[2];
const FIG = (f) => path.join(ROOT, 'figures', f);
const OUT = path.join(ROOT, 'docs', '202444085_김철중_기말프로젝트_발표.pptx');

const THEME = {
  name: 'NPS Exit',
  headFontFace: 'Malgun Gothic',
  bodyFontFace: 'Malgun Gothic',
  colors: {
    dk1: '1F2329', lt1: 'FFFFFF', dk2: '17263C', lt2: 'EEF2F7',
    accent1: 'E6550D', accent2: '3182BD', accent3: '9ECAE1', accent4: 'FDAE6B',
    accent5: '6B7785', accent6: '2E7D32', hlink: '3182BD', folHlink: '6B7785',
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9'; // 10 x 5.625 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = '국민연금 사업장 탈퇴 조기 예측';
pres.author = '김철중';
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: 'TITLE_DARK',
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 1.45, w: 8.8, h: 1.5, fontSize: 30, bold: true, color: C.background1, valign: 'top', align: 'left' }, text: '' } },
    { placeholder: { options: { name: 'body', type: 'body', x: 0.6, y: 3.15, w: 8.8, h: 1.4, fontSize: 15, color: C.accent3, valign: 'top' }, text: '' } },
  ],
});
pres.defineSlideMaster({
  title: 'CONTENT',
  background: { color: C.background1 },
  margin: [0.4, 0.5, 0.45, 0.5],
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.28, w: 9.0, h: 0.6, fontSize: 24, bold: true, color: C.text2, valign: 'middle', align: 'left', margin: 0 }, text: '' } },
    { text: { text: '202444085 김철중 · 데이터분석 기말 프로젝트', options: { x: 0.5, y: 5.25, w: 5, h: 0.25, fontSize: 9, color: C.accent5, margin: 0 } } },
  ],
  slideNumber: { x: 9.1, y: 5.22, w: 0.4, h: 0.3, fontSize: 9, color: C.accent5, align: 'right' },
});

const axis = {
  catAxisLabelColor: HEX.accent5, valAxisLabelColor: HEX.accent5,
  catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', dataLabelFontFace: '+mn-lt',
  legendFontFace: '+mn-lt', titleFontFace: '+mn-lt',
  catAxisLabelFontSize: 11, valAxisLabelFontSize: 10, dataLabelFontSize: 10, legendFontSize: 11,
  valGridLine: { color: 'DDE3EA', size: 0.5 }, catGridLine: { style: 'none' },
  dataLabelColor: HEX.dk1,
};

function card(slide, x, y, w, h, fill, name) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.08, objectName: name });
}
function stat(slide, x, y, w, big, small, color, name, size) {
  slide.addText(big, { x, y, w, h: 0.75, fontSize: size || 36, fit: 'shrink', bold: true, color, margin: 0, isTextBox: true, objectName: name + ' value' });
  slide.addText(small, { x, y: y + 0.75, w, h: 0.6, fontSize: 12, color: C.text1, margin: 0, valign: 'top', isTextBox: true, objectName: name + ' label' });
}
function bullets(slide, items, opts) {
  slide.addText(items.map((t, i) => {
    const runs = typeof t === 'string' ? { text: t } : t;
    return { text: runs.text, options: { bullet: true, breakLine: i < items.length - 1, bold: runs.bold || false, paraSpaceAfter: 6 } };
  }), Object.assign({ fontSize: 14, color: C.text1, valign: 'top', isTextBox: true }, opts));
}

// 1. Title ----------------------------------------------------------------
pres.addSection({ title: '도입' });
let s = pres.addSlide({ masterName: 'TITLE_DARK', sectionTitle: '도입' });
s.addText('국민연금 가입 사업장 데이터로 본\n사업장 탈퇴(폐업) 3개월 조기 예측', { placeholder: 'title' });
s.addText('데이터분석 기말대체 프로젝트\n인하공업전문대학 컴퓨터정보공학과 202444085 김철중', { placeholder: 'body' });
s.addNotes('안녕하세요, 202444085 김철중입니다. 국민연금 가입 사업장 공공데이터로 3개월 안에 탈퇴, 즉 폐업하거나 문을 닫을 사업장을 미리 찾아낼 수 있는지 분석했습니다.');

// 2. Problem --------------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '도입' });
s.addText('재무제표보다 빠른 폐업 신호를 찾을 수 있을까', { placeholder: 'title' });
bullets(s, [
  '폐업 위험은 보통 재무제표로 보지만, 1년·분기 단위로만 갱신되고 소규모 사업장은 공개되지 않는다',
  '국민연금공단은 전국 사업장의 가입자 수·고지금액·입퇴사자 수를 매월 공개한다',
  { text: '질문: 지금 가입된 사업장 중 3개월 안에 탈퇴할 곳을 미리 찾을 수 있는가?', bold: true },
], { x: 0.5, y: 1.15, w: 5.3, h: 3.6 });
card(s, 6.2, 1.15, 3.3, 1.75, HEX.lt2, 'stat card 1');
stat(s, 6.45, 1.3, 2.9, '59만 곳', '매월 공개되는 국민연금\n가입 사업장 수', C.accent2, 'stat 1');
card(s, 6.2, 3.05, 3.3, 1.75, HEX.lt2, 'stat card 2');
stat(s, 6.45, 3.2, 2.9, '0.40%', '3개월 안에 탈퇴하는 비율\n(극단적 불균형)', C.accent1, 'stat 2');
s.addNotes('폐업 위험은 보통 재무제표로 판단하지만 갱신이 느리고 소규모 사업장은 공개되지도 않습니다. 반면 국민연금 사업장 데이터는 59만 곳의 인원과 급여 흐름을 매달 공개합니다. 그래서 이 데이터만으로 3개월 안의 탈퇴를 예측할 수 있는지 봤습니다. 탈퇴 비율은 0.4%로 매우 불균형한 문제입니다.');

// 3. Related work ---------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '도입' });
s.addText('기존 연구와 차별점', { placeholder: 'title' });
const rel = [
  ['공현정 외 (2023)', '전자결제 이용 사업자', '결제·재무 정보\n특정 플랫폼 가입자만'],
  ['박준식 외 (2023)', '소상공인 도소매업', '2019 실태조사 설문\n1회성 자료'],
  ['Bang 외 (2018)', '서울 치킨집', '인허가 데이터\n단일 업종·지역'],
];
rel.forEach((r, i) => {
  const x = 0.5 + i * 2.35;
  card(s, x, 1.15, 2.15, 1.6, HEX.lt2, 'related card ' + (i + 1));
  s.addText([
    { text: r[0], options: { bold: true, fontSize: 13, color: HEX.dk2, breakLine: true } },
    { text: r[1], options: { fontSize: 12, color: HEX.accent2, breakLine: true } },
    { text: r[2], options: { fontSize: 11, color: HEX.dk1 } },
  ], { x: x + 0.15, y: 1.25, w: 1.9, h: 1.4, valign: 'top', margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: 'related text ' + (i + 1) });
});
card(s, 7.55, 1.15, 1.95, 1.6, HEX.dk2, 'this study card');
s.addText([
  { text: '본 연구', options: { bold: true, fontSize: 14, color: HEX.lt1, breakLine: true } },
  { text: '국민연금 월별\n공개 데이터\n전 업종·전국\n패널 + FI-SMOTE', options: { fontSize: 11, color: HEX.accent3 } },
], { x: 7.7, y: 1.25, w: 1.7, h: 1.4, valign: 'top', margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: 'this study text' });
bullets(s, [
  '누구나 받을 수 있는 공공데이터만으로 전 업종·전국 사업장을 다룸',
  '매월 갱신되는 특성을 살려 "최근 인원 증감", "최근 신규 등록" 같은 흐름 변수를 만듦',
  'KoreaScience·KCI 검색 결과 이 데이터로 탈퇴를 예측한 머신러닝 연구는 찾지 못함',
], { x: 0.5, y: 3.0, w: 9.0, h: 2.0, fontSize: 14 });
s.addNotes('기존 폐업 예측 연구는 전자결제 플랫폼 가입자, 소상공인 설문, 서울 치킨집처럼 대상이 한정되어 있었습니다. 저는 공공데이터만으로 전 업종과 전국을 다루고, 매달 갱신된다는 점을 이용해 시간 흐름 변수를 만들었습니다. 이 데이터로 탈퇴를 예측한 연구는 찾지 못했습니다.');

// 4. Data & label ---------------------------------------------------------
pres.addSection({ title: '데이터' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '데이터' });
s.addText('5개월치 월별 파일을 사업장 단위로 연결', { placeholder: 'title' });
const steps = [['2026-03', 'T-4'], ['2026-04', 'T-3'], ['2026-06', 'T-1'], ['2026-07', '기준월 T'], ['2026-10', 'T+3 정답']];
steps.forEach((st, i) => {
  const x = 0.5 + i * 1.85;
  const isT = i === 3, isY = i === 4;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.15, w: 1.6, h: 0.9, rectRadius: 0.08,
    fill: { color: isT ? HEX.dk2 : isY ? HEX.accent1 : HEX.lt2 }, line: { color: isT ? HEX.dk2 : isY ? HEX.accent1 : HEX.lt2 }, objectName: 'month box ' + (i + 1) });
  s.addText([{ text: st[0], options: { bold: true, fontSize: 14, breakLine: true } }, { text: st[1], options: { fontSize: 11 } }],
    { x, y: 1.15, w: 1.6, h: 0.9, align: 'center', valign: 'middle', margin: 0, color: (isT || isY) ? HEX.lt1 : HEX.dk2, isTextBox: true, objectName: 'month text ' + (i + 1) });
  if (i < 4) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 1.63, y: 1.48, w: 0.2, h: 0.24, fill: { color: HEX.accent5 }, line: { color: HEX.accent5 }, objectName: 'arrow ' + (i + 1) });
});
bullets(s, [
  '연결 키: 사업자번호 6자리 + 사업장명 + 법정동·업종코드',
  '정답: 기준월에 "등록"인 사업장이 3개월 뒤 "탈퇴(2)"로 바뀌면 1',
  '3개월 뒤 파일에서 사라진 40,135곳은 사유를 알 수 없어 제외',
  '파생변수 17개: 업력, 1인당 고지금액, 상실률·취득률, 1/3/4개월 인원 증감률, 신규진입 여부 등',
], { x: 0.5, y: 2.3, w: 6.0, h: 2.8, fontSize: 13 });
card(s, 6.8, 2.35, 2.7, 2.6, HEX.lt2, 'count card');
stat(s, 7.0, 2.5, 2.4, '513,541', '분석 대상 사업장', C.text2, 'count total');
stat(s, 7.0, 3.6, 2.4, '2,033', '3개월 내 탈퇴 (0.40%)', C.accent1, 'count exit');
s.addNotes('사업장 고유번호가 없어서 사업자번호 앞자리, 이름, 주소 코드, 업종 코드를 묶어 같은 사업장을 연결했습니다. 2026년 7월을 기준월로, 10월에 탈퇴 상태로 바뀌었으면 1로 정의했습니다. 과거 3개 시점을 붙여 인원 증감률 같은 변수 17개를 만들었고, 최종 51만 곳 중 2,033곳이 탈퇴했습니다.');

// 5. EDA size/age ---------------------------------------------------------
pres.addSection({ title: 'EDA' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'EDA' });
s.addText('작고 젊은 사업장일수록 탈퇴율이 높다', { placeholder: 'title' });
s.addImage({ path: FIG('02_size_age_rate.png'), x: 0.5, y: 1.05, w: 5.9, h: 1.93, objectName: 'size age chart', altText: '가입자 규모별, 업력별 3개월 내 탈퇴율 그래프' });
bullets(s, [
  '1~4명 0.62% vs 100명+ 0.04% (16배)',
  '업력 1년 미만 2.98% vs 20년+ 0.05% (60배)',
  '가입자 0명인 등록 사업장 93곳 → 77% 탈퇴',
], { x: 6.6, y: 1.05, w: 2.9, h: 2.2, fontSize: 12 });
card(s, 0.5, 3.45, 9.0, 1.5, HEX.lt2, 'accuracy trap card');
s.addText([
  { text: '정확도의 함정  ', options: { bold: true, color: HEX.accent1, fontSize: 15 } },
  { text: '전부 "유지"라고 찍어도 정확도는 99.6% — 그래서 정확도 대신 Precision·Recall·F1·PR-AUC로 평가한다 (1주차 FDS 예시와 같은 상황)', options: { color: HEX.dk1, fontSize: 13 } },
], { x: 0.75, y: 3.55, w: 8.5, h: 1.3, valign: 'middle', margin: 0, isTextBox: true, objectName: 'accuracy trap text' });
s.addNotes('EDA 결과 규모가 작을수록, 업력이 짧을수록 탈퇴율이 뚜렷하게 높았습니다. 그리고 탈퇴가 0.4%뿐이라 전부 유지라고 찍어도 정확도가 99.6%가 나옵니다. 그래서 정확도 대신 Precision, Recall, F1, PR-AUC로 평가했습니다.');

// 6. EDA industry ---------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'EDA' });
s.addText('탈퇴 사업장의 절반은 건설·공사업', { placeholder: 'title' });
s.addImage({ path: FIG('03_industry_top15.png'), x: 0.5, y: 1.2, w: 5.4, h: 3.58, objectName: 'industry chart', altText: '탈퇴율 상위 15개 업종 막대그래프' });
card(s, 6.2, 1.05, 3.3, 1.6, HEX.lt2, 'construction card');
stat(s, 6.4, 1.15, 3.0, '13.9% → 49.0%', '전체 사업장 중 비중 → 탈퇴 사업장 중 비중', C.accent1, 'construction stat', 26);
bullets(s, [
  '공사 현장마다 사업장을 등록했다가 공사가 끝나면 탈퇴',
  '최근 3개월 신규 등록 사업장 탈퇴율 1.31% (기존 0.25%의 5배)',
  '"탈퇴" = 폐업 + 현장 종료 + 휴업 → 해석 시 주의',
], { x: 6.2, y: 2.85, w: 3.3, h: 2.2, fontSize: 12 });
s.addNotes('업종별로 보면 상위 15개 업종이 거의 다 건설, 공사업이었습니다. 전체의 14%인 건설업이 탈퇴의 49%를 차지합니다. 공사 현장마다 사업장을 등록했다가 공사가 끝나면 탈퇴하기 때문으로, 이 데이터의 탈퇴는 폐업뿐 아니라 현장 종료도 포함한다는 점을 주의해야 합니다.');

// 7. Model compare --------------------------------------------------------
pres.addSection({ title: '모델링' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '모델링' });
s.addText('7개 알고리즘 비교 — 앙상블이 우세', { placeholder: 'title' });
const models = ['LogisticRegression', 'AdaBoost', 'DecisionTree', 'LightGBM', 'XGBoost', 'RandomForest', 'Voting(soft)'];
const prauc = [0.091, 0.098, 0.098, 0.152, 0.172, 0.183, 0.189];
s.addChart(pres.charts.BAR, [{ name: 'PR-AUC', labels: models, values: prauc }], Object.assign({
  x: 0.5, y: 1.0, w: 5.8, h: 4.05, barDir: 'bar', chartColors: [HEX.accent2], showValue: true, dataLabelPosition: 'outEnd',
  dataLabelFormatCode: '0.000', valAxisHidden: true, showLegend: false, showTitle: true, title: 'PR-AUC (층화 5-겹 교차검증 평균)', titleFontSize: 12, titleColor: HEX.dk2,
  valAxisMaxVal: 0.22, objectName: 'model prauc chart',
}, axis));
bullets(s, [
  '정확도는 모든 모델이 99.6% 근처라 비교가 안 됨',
  'PR-AUC 기준 Voting·RandomForest가 최고, 무작위 기준선(0.004)의 약 45배',
  '임계값 0.5에서는 Recall이 대부분 10% 미만 → 다수결 편향',
  'SVM은 15만 행에서 학습이 너무 느려 제외',
], { x: 6.5, y: 1.1, w: 3.0, h: 3.9, fontSize: 12 });
s.addNotes('교안에서 배운 7개 알고리즘을 층화 5-겹 교차검증으로 비교했습니다. 정확도는 모두 99.6%로 같아서 PR-AUC로 비교했고, Voting과 랜덤포레스트가 가장 좋았습니다. 다만 임계값 0.5에서는 탈퇴를 거의 못 잡아서, 다음으로 불균형 처리를 적용했습니다.');

// 8. Imbalance ------------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '모델링' });
s.addText('불균형 처리: FI-SMOTE가 F1·MCC 1위', { placeholder: 'title' });
const samp = ['없음', 'class_weight', 'SMOTE', 'ADASYN', 'FI-SMOTE'];
s.addChart(pres.charts.BAR, [
  { name: 'LightGBM', labels: samp, values: [0.143, 0.072, 0.150, 0.152, 0.150] },
  { name: 'RandomForest', labels: samp, values: [0.095, 0.174, 0.167, 0.163, 0.223] },
], Object.assign({
  x: 0.5, y: 1.0, w: 5.8, h: 4.05, barDir: 'col', barGrouping: 'clustered', chartColors: [HEX.accent3, HEX.accent1],
  showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.00', valAxisHidden: true, valAxisMaxVal: 0.26,
  showLegend: true, legendPos: 'b', showTitle: true, title: '테스트셋 F1 (임계값 0.5)', titleFontSize: 12, titleColor: HEX.dk2,
  objectName: 'imbalance f1 chart',
}, axis));
bullets(s, [
  'FI-SMOTE: 본인이 1학기에 제안한 기법 — 중요 변수는 원본 근처, 비중요 변수는 자유롭게 보간',
  'RandomForest + FI-SMOTE: F1 0.223, MCC 0.224로 10개 조합 중 1위',
  'SMOTE·ADASYN은 오히려 PR-AUC 하락 (경계 노이즈)',
  '신용카드 사기(0.17%)에서 본 효과가 다른 도메인에서도 재현',
], { x: 6.5, y: 1.1, w: 3.0, h: 3.9, fontSize: 12 });
s.addNotes('불균형 처리로 SMOTE, ADASYN, 그리고 제가 1학기에 제안한 FI-SMOTE를 비교했습니다. 일반 SMOTE와 ADASYN은 오히려 순위 성능이 떨어졌지만, FI-SMOTE는 랜덤포레스트와 결합했을 때 F1과 MCC 모두 1위였습니다. 신용카드 사기 데이터에서 본 효과가 이 데이터에서도 재현됐습니다.');

// 9. Final result ---------------------------------------------------------
pres.addSection({ title: '결과' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '결과' });
s.addText('상위 5%만 점검해도 탈퇴 사업장의 63%를 찾는다', { placeholder: 'title' });
const pct = ['1%', '2%', '3%', '5%', '10%', '20%', '30%'];
s.addChart(pres.charts.LINE, [
  { name: '모델 위험 점수 순', labels: pct, values: [37.3, 49.4, 55.8, 62.9, 69.0, 76.9, 82.8] },
  { name: '무작위 점검', labels: pct, values: [1, 2, 3, 5, 10, 20, 30] },
], Object.assign({
  x: 0.5, y: 1.0, w: 5.8, h: 4.05, chartColors: [HEX.accent1, 'A0A8B3'], lineSize: 2.5, lineDataSymbol: 'circle', lineDataSymbolSize: 7,
  showValue: true, dataLabelPosition: 't', dataLabelFormatCode: '0"%"', valAxisMaxVal: 100, valAxisLabelFormatCode: '0"%"',
  showLegend: true, legendPos: 'b', showTitle: true, title: '점검 대상(위험 점수 상위 %)별 탈퇴 사업장 포착률', titleFontSize: 12, titleColor: HEX.dk2,
  objectName: 'capture chart',
}, axis));
card(s, 6.5, 1.05, 3.0, 1.3, HEX.lt2, 'final stat card 1');
stat(s, 6.7, 1.15, 2.6, '37배', '상위 1% 점검 시 무작위 대비 효율', C.accent1, 'lift stat');
card(s, 6.5, 2.5, 3.0, 2.55, HEX.lt2, 'final metrics card');
s.addText([
  { text: '최종 모델', options: { bold: true, fontSize: 13, color: HEX.dk2, breakLine: true } },
  { text: 'RandomForest (GridSearchCV) + FI-SMOTE', options: { fontSize: 11, color: HEX.accent5, breakLine: true } },
  { text: 'F1 0.227 · MCC 0.225', options: { fontSize: 13, color: HEX.dk1, breakLine: true } },
  { text: 'ROC-AUC 0.861 · PR-AUC 0.169', options: { fontSize: 13, color: HEX.dk1, breakLine: true } },
  { text: '테스트셋 102,709곳 (탈퇴 407곳)', options: { fontSize: 11, color: HEX.accent5 } },
], { x: 6.7, y: 2.6, w: 2.7, h: 2.35, valign: 'top', margin: 0, paraSpaceAfter: 5, isTextBox: true, objectName: 'final metrics text' });
s.addNotes('튜닝한 랜덤포레스트에 FI-SMOTE를 적용한 최종 모델은 테스트셋에서 F1 0.227, ROC-AUC 0.861이었습니다. 실무적으로 의미 있는 건 이 그래프인데, 위험 점수 상위 1%만 점검해도 탈퇴 사업장의 37%, 상위 5%면 63%를 찾아냅니다. 무작위로 점검하는 것보다 37배 효율적입니다.');

// 10. Feature importance ---------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '결과' });
s.addText('무엇이 탈퇴를 알려주는가', { placeholder: 'title' });
const feats = ['업종대분류', '고지금액증감률_3개월', '취득률', '가입자수', '업력', '신규진입'];
const imp = [0.070, 0.070, 0.071, 0.100, 0.139, 0.156];
s.addChart(pres.charts.BAR, [{ name: '중요도', labels: feats, values: imp }], Object.assign({
  x: 0.5, y: 1.0, w: 5.2, h: 4.05, barDir: 'bar', chartColors: [HEX.dk2], showValue: true, dataLabelPosition: 'outEnd',
  dataLabelFormatCode: '0.000', valAxisHidden: true, valAxisMaxVal: 0.19, showLegend: false,
  showTitle: true, title: '특성 중요도 상위 6개 (최종 모델)', titleFontSize: 12, titleColor: HEX.dk2, objectName: 'importance chart',
}, axis));
const fx = [
  ['신규진입', '최근 3개월 내 등록 → 탈퇴율 5배'],
  ['업력', '하위 10% 2.26% vs 상위 10% 0.04%'],
  ['가입자수', '작을수록 위험 (1~4명 0.62%)'],
  ['취득률·고지금액 변화', '인원이 급히 들고 나거나 급여 총액이 줄면 이상 신호'],
];
fx.forEach((f, i) => {
  const y = 1.05 + i * 1.0;
  card(s, 5.95, y, 3.55, 0.88, HEX.lt2, 'factor card ' + (i + 1));
  s.addText([{ text: f[0], options: { bold: true, fontSize: 12, color: HEX.accent1, breakLine: true } }, { text: f[1], options: { fontSize: 11, color: HEX.dk1 } }],
    { x: 6.1, y: y + 0.05, w: 3.3, h: 0.78, valign: 'middle', margin: 0, isTextBox: true, objectName: 'factor text ' + (i + 1) });
});
s.addNotes('가장 중요한 변수는 최근 신규 등록 여부, 업력, 가입자 수였습니다. 최근에 등록된 사업장, 업력이 짧은 사업장, 작은 사업장일수록 위험했고, 그다음으로 입퇴사 흐름과 급여 총액 변화가 중요했습니다.');

// 11. Conclusion ----------------------------------------------------------
pres.addSection({ title: '결론' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '결론' });
s.addText('결론: "확정 판정"보다 "점검 우선순위" 도구', { placeholder: 'title' });
card(s, 0.5, 1.05, 4.4, 3.95, HEX.lt2, 'action card');
s.addText('실행 제언', { x: 0.7, y: 1.15, w: 4.0, h: 0.4, fontSize: 15, bold: true, color: C.accent1, margin: 0, isTextBox: true, objectName: 'action title' });
bullets(s, [
  '고용센터·지자체: 매월 위험 점수 상위 1~5%를 고용지원·체불 예방 점검 대상으로',
  '거래 기업·금융: 재무제표보다 빠른 거래처 위험 보조 지표',
  '창업 지원: 1년 미만·소규모·인원 급변 사업장 컨설팅 연계',
  '건설 현장은 별도 모델로 분리',
], { x: 0.7, y: 1.65, w: 4.0, h: 3.25, fontSize: 14 });
card(s, 5.1, 1.05, 4.4, 3.95, HEX.lt2, 'limit card');
s.addText('한계와 개선 방향', { x: 5.3, y: 1.15, w: 4.0, h: 0.4, fontSize: 15, bold: true, color: C.accent2, margin: 0, isTextBox: true, objectName: 'limit title' });
bullets(s, [
  '"탈퇴"에 폐업·현장 종료·휴업이 섞여 있음',
  '파일에서 사라진 4만 곳 제외 → 탈퇴율 과소 추정 가능',
  '고지금액 상한, 6자리 사업자번호로 인한 연결 오류 가능',
  '기준월 1개만 사용 → 여러 달로 학습하고 이후 시점으로 검증 필요',
], { x: 5.3, y: 1.65, w: 4.0, h: 3.25, fontSize: 14 });
s.addNotes('정리하면, 공공데이터만으로 탈퇴 위험이 높은 사업장을 무작위보다 훨씬 효율적으로 골라낼 수 있었습니다. 개별 사업장을 확정하기보다는 점검 우선순위를 정하는 도구로 쓰는 게 적합합니다. 한계로는 탈퇴에 현장 종료가 섞여 있다는 점과 기준월을 하나만 썼다는 점이 있어, 여러 달로 학습하고 이후 시점으로 검증하는 것을 다음 과제로 남깁니다. 감사합니다.');

// 12. Thanks --------------------------------------------------------------
s = pres.addSlide({ masterName: 'TITLE_DARK', sectionTitle: '결론' });
s.addText('감사합니다', { placeholder: 'title' });
s.addText('소스코드: github.com/cholin3721/NPS-Workplace-Exit-Prediction\n데이터: 공공데이터포털 「국민연금공단_국민연금 가입 사업장 내역」\n생성형 AI: Claude — 자료 검색, 코드·문서 초안 작성 보조', { placeholder: 'body' });
s.addNotes('질문 받겠습니다.');

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('saved', OUT);
})();
