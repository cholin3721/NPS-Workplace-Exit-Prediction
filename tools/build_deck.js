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

// ── 숫자: tools/deck_numbers.py 가 results/*.csv 에서 만든 값 ──────────────
const N = JSON.parse(require('fs').readFileSync(path.join(ROOT, 'tools', 'deck_numbers.json'), 'utf8'));
const pct1 = (x) => (x * 100).toFixed(1) + '%';
const fi = N.samplers.indexOf('FI-SMOTE');
const winF1 = N.wins['FI-SMOTE > SMOTE'].F1;

// 1. Title ----------------------------------------------------------------
pres.addSection({ title: '도입' });
let s = pres.addSlide({ masterName: 'TITLE_DARK', sectionTitle: '도입' });
s.addText('국민연금 가입 사업장 데이터로 본\n사업장 탈퇴 3개월 조기 예측', { placeholder: 'title' });
s.addText('데이터분석 기말대체 프로젝트\n인하공업전문대학 컴퓨터정보공학과 202444085 김철중', { placeholder: 'body' });
s.addNotes('안녕하세요, 202444085 김철중입니다. 국민연금 가입 사업장 공공데이터로 3개월 안에 국민연금 가입을 탈퇴할 사업장, 즉 폐업하거나 문을 닫을 사업장을 미리 찾아낼 수 있는지 분석했습니다.');

// 2. Problem + related work ------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '도입' });
s.addText('재무제표보다 빠른 탈퇴 신호를 찾을 수 있을까', { placeholder: 'title' });
bullets(s, [
  '폐업 위험은 보통 재무제표로 보지만, 갱신이 느리고 소규모 사업장은 공개되지 않는다',
  '국민연금공단은 전국 사업장의 가입자 수·고지금액·입퇴사자 수를 매월 공개한다',
  { text: '질문: 지금 가입된 사업장 중 3개월 안에 탈퇴할 곳을 미리 찾을 수 있는가?', bold: true },
], { x: 0.5, y: 1.05, w: 5.4, h: 2.6 });
card(s, 6.2, 1.05, 3.3, 1.2, HEX.lt2, 'stat card 1');
stat(s, 6.4, 1.1, 2.9, '59만 곳', '매월 공개되는 가입 사업장', C.accent2, 'stat 1', 30);
card(s, 6.2, 2.4, 3.3, 1.2, HEX.lt2, 'stat card 2');
stat(s, 6.4, 2.45, 2.9, '0.40%', '3개월 안에 탈퇴하는 비율', C.accent1, 'stat 2', 30);
card(s, 0.5, 3.85, 9.0, 1.2, HEX.dk2, 'related card');
s.addText([
  { text: '기존 폐업 예측 연구  ', options: { bold: true, color: HEX.accent3, fontSize: 13 } },
  { text: '전자결제 이용 사업자(2023) · 소상공인 도소매 설문(2023) · 서울 치킨집(2018) — 특정 업종·플랫폼·1회성 자료', options: { color: HEX.lt1, fontSize: 12, breakLine: true } },
  { text: '본 연구  ', options: { bold: true, color: HEX.accent4, fontSize: 13 } },
  { text: '누구나 받을 수 있는 월별 공개 데이터로 전 업종·전국을 다루고, 인원·급여 흐름 변수를 만듦', options: { color: HEX.lt1, fontSize: 12 } },
], { x: 0.75, y: 3.9, w: 8.5, h: 1.1, valign: 'middle', margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: 'related text' });
s.addNotes('폐업 위험은 보통 재무제표로 판단하지만 갱신이 느리고 소규모 사업장은 공개되지도 않습니다. 반면 국민연금 사업장 데이터는 59만 곳의 인원과 급여 흐름을 매달 공개합니다. 기존 연구는 특정 업종이나 플랫폼에 한정됐는데, 저는 공개 데이터로 전 업종·전국을 다뤘고 이 데이터로 탈퇴를 예측한 연구는 찾지 못했습니다.');

// 3. Data -------------------------------------------------------------------
pres.addSection({ title: '데이터' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '데이터' });
s.addText('월별 파일을 사업장 단위로 연결해 정답을 만든다', { placeholder: 'title' });
const steps = [['2026-03', 'T-4'], ['2026-04', 'T-3'], ['2026-06', 'T-1'], ['2026-07', '기준월 T'], ['2026-10', 'T+3 정답']];
steps.forEach((st, i) => {
  const x = 0.5 + i * 1.85;
  const isT = i === 3, isY = i === 4;
  const fill = isT ? HEX.dk2 : isY ? HEX.accent1 : HEX.lt2;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.05, w: 1.6, h: 0.85, rectRadius: 0.08, fill: { color: fill }, line: { color: fill }, objectName: 'month box ' + (i + 1) });
  s.addText([{ text: st[0], options: { bold: true, fontSize: 14, breakLine: true } }, { text: st[1], options: { fontSize: 11 } }],
    { x, y: 1.05, w: 1.6, h: 0.85, align: 'center', valign: 'middle', margin: 0, color: (isT || isY) ? HEX.lt1 : HEX.dk2, isTextBox: true, objectName: 'month text ' + (i + 1) });
  if (i < 4) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 1.63, y: 1.36, w: 0.2, h: 0.24, fill: { color: HEX.accent5 }, line: { color: HEX.accent5 }, objectName: 'arrow ' + (i + 1) });
});
bullets(s, [
  '연결 키: 사업자번호 6자리 + 사업장명 + 법정동·업종코드',
  '정답: 기준월에 "등록"인 사업장이 3개월 뒤 "탈퇴"로 바뀌면 1',
  '3개월 뒤 파일에서 사라진 40,135곳은 제외 (민감도 분석으로 따로 확인)',
  '파생변수 17개: 업력, 1인당 고지금액, 상실·취득률, 인원 증감률, 신규진입 등',
], { x: 0.5, y: 2.15, w: 6.0, h: 2.9, fontSize: 13 });
card(s, 6.8, 2.15, 2.7, 2.9, HEX.lt2, 'count card');
stat(s, 7.0, 2.3, 2.4, '513,541', '분석 대상 사업장', C.text2, 'count total', 32);
stat(s, 7.0, 3.5, 2.4, '2,033', '3개월 내 탈퇴 (0.40%)', C.accent1, 'count exit', 32);
s.addNotes('사업장 고유번호가 없어서 사업자번호 앞자리, 이름, 주소·업종 코드를 묶어 같은 사업장을 연결했습니다. 2026년 7월에 등록 상태인 사업장이 10월에 탈퇴로 바뀌었으면 1로 정의했고, 과거 시점을 붙여 인원 증감률 같은 변수 17개를 만들었습니다. 51만 곳 중 2,033곳, 0.4%가 탈퇴했습니다.');

// 4. EDA --------------------------------------------------------------------
pres.addSection({ title: 'EDA' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'EDA' });
s.addText('작고 젊은 사업장, 그리고 건설 현장이 위험하다', { placeholder: 'title' });
s.addImage({ path: FIG('02_size_age_rate.png'), x: 0.5, y: 1.0, w: 5.9, h: 1.93, objectName: 'size age chart', altText: '가입자 규모별, 업력별 3개월 내 탈퇴율 그래프' });
bullets(s, [
  '1~4명 0.62% · 100명+ 0.04%',
  '업력 1년 미만 2.98% · 20년+ 0.05%',
  '가입자 0명 사업장 77% 탈퇴',
], { x: 6.6, y: 1.05, w: 2.9, h: 1.9, fontSize: 12 });
card(s, 0.5, 3.15, 4.4, 1.9, HEX.lt2, 'accuracy trap card');
s.addText([
  { text: '정확도의 함정', options: { bold: true, color: HEX.accent1, fontSize: 15, breakLine: true } },
  { text: '전부 "유지"라고 찍어도 정확도 99.6% → Precision·Recall·F1·PR-AUC로 평가 (1주차 FDS 예시)', options: { color: HEX.dk1, fontSize: 13 } },
], { x: 0.7, y: 3.25, w: 4.0, h: 1.7, valign: 'middle', margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: 'accuracy trap text' });
card(s, 5.1, 3.15, 4.4, 1.9, HEX.lt2, 'construction card');
s.addText([
  { text: '건설·공사업 13.9% → 49.0%', options: { bold: true, color: HEX.accent1, fontSize: 15, breakLine: true } },
  { text: '전체 사업장 중 비중 → 탈퇴 중 비중. 현장마다 등록했다가 공사가 끝나면 탈퇴 → "탈퇴"는 폐업 + 현장 종료 + 휴업', options: { color: HEX.dk1, fontSize: 13 } },
], { x: 5.3, y: 3.25, w: 4.0, h: 1.7, valign: 'middle', margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: 'construction text' });
s.addNotes('규모가 작을수록, 업력이 짧을수록 탈퇴율이 뚜렷하게 높았습니다. 탈퇴가 0.4%뿐이라 전부 유지라고 찍어도 정확도가 99.6%라서, 정확도 대신 Precision, Recall, F1, PR-AUC로 평가했습니다. 또 탈퇴의 절반이 건설·공사업이었는데, 공사 현장마다 사업장을 등록하기 때문입니다. 그래서 여기서 탈퇴는 폐업만이 아니라 현장 종료도 포함합니다.');

// 5. Model compare --------------------------------------------------------
pres.addSection({ title: '모델링' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '모델링' });
s.addText('7개 알고리즘 비교 — 앙상블이 우세', { placeholder: 'title' });
s.addChart(pres.charts.BAR, [{ name: 'PR-AUC', labels: N.models, values: N.model_prauc }], Object.assign({
  x: 0.5, y: 1.0, w: 5.8, h: 4.05, barDir: 'bar', chartColors: [HEX.accent2], showValue: true, dataLabelPosition: 'outEnd',
  dataLabelFormatCode: '0.000', valAxisHidden: true, showLegend: false, showTitle: true, title: 'PR-AUC (층화 5-겹 교차검증 평균)', titleFontSize: 12, titleColor: HEX.dk2,
  valAxisMaxVal: 0.22, objectName: 'model prauc chart',
}, axis));
bullets(s, [
  '정확도는 모두 99.6% 근처라 비교 불가',
  'PR-AUC는 Voting·RandomForest 최고, 무작위의 약 45배',
  '임계값 0.5에서는 Recall 대부분 10% 미만 → 다수결 편향',
], { x: 6.5, y: 1.1, w: 3.0, h: 3.9, fontSize: 13 });
s.addNotes('교안의 분류 알고리즘 7개를 층화 5-겹 교차검증으로 비교했습니다. 정확도는 모두 99.6%로 같아서 PR-AUC로 비교했고, Voting과 랜덤포레스트가 가장 좋았습니다. 하지만 임계값 0.5에서는 탈퇴를 거의 못 잡아서 불균형 처리를 적용했습니다.');

// 6. Imbalance (5-fold) ----------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '모델링' });
s.addText('불균형 처리: FI-SMOTE가 F1·MCC를 가장 높였다', { placeholder: 'title' });
s.addChart(pres.charts.BAR, [
  { name: 'F1', labels: N.samplers, values: N.cv5_f1 },
  { name: 'MCC', labels: N.samplers, values: N.cv5_mcc },
], Object.assign({
  x: 0.5, y: 1.0, w: 5.8, h: 4.05, barDir: 'col', barGrouping: 'clustered', chartColors: [HEX.accent1, HEX.dk2],
  showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.000', valAxisHidden: true,
  showLegend: true, legendPos: 'b', showTitle: true, title: 'RandomForest, 층화 5-겹 반복 평균 (임계값 0.5)', titleFontSize: 12, titleColor: HEX.dk2,
  objectName: 'imbalance cv5 chart',
}, axis));
bullets(s, [
  'FI-SMOTE: 본인이 1학기에 제안한 기법 — 중요 변수는 원본 근처, 나머지는 자유롭게 보간',
  `5-겹 평균 F1 ${N.cv5_f1[fi].toFixed(3)} (±${N.cv5_f1_std[fi].toFixed(3)}) — 5번 모두 SMOTE·ADASYN보다 F1·MCC·PR-AUC 높음`,
  `순위 지표 PR-AUC는 오버샘플링 없음(${N.cv5_prauc[0].toFixed(3)})이 더 높음 → 효과는 놓치던 탈퇴를 더 잡는 것`,
], { x: 6.5, y: 1.1, w: 3.0, h: 3.9, fontSize: 12 });
s.addNotes(`불균형 처리로 SMOTE, ADASYN, 제가 1학기에 제안한 FI-SMOTE를 비교했습니다. 한 번의 분할만으로는 우연일 수 있어서 5-겹으로 다섯 번 반복했습니다. FI-SMOTE는 F1과 MCC 평균이 가장 높았고, 다섯 번 중 ${winF1}번 SMOTE보다 F1이 높았습니다. 다만 순위 지표인 PR-AUC는 오버샘플링을 안 한 경우와 비슷해서, 효과는 임계값에서 놓치던 탈퇴를 더 잡아내는 데 있다고 봤습니다.`);

// 7. Final result ---------------------------------------------------------
pres.addSection({ title: '결과' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '결과' });
s.addText(`상위 5%만 점검해도 탈퇴 사업장의 ${Math.round(N.final['Recall@상위5%'] * 100)}%를 찾는다`, { placeholder: 'title' });
const pctLabels = N.cap_pcts.map((p) => p + '%');
s.addChart(pres.charts.LINE, [
  { name: '모델 위험 점수 순', labels: pctLabels, values: N.cap_random },
  { name: '무작위 점검', labels: pctLabels, values: N.cap_pcts },
], Object.assign({
  x: 0.5, y: 1.0, w: 5.8, h: 4.05, chartColors: [HEX.accent1, 'A0A8B3'], lineSize: 2.5, lineDataSymbol: 'circle', lineDataSymbolSize: 7,
  showValue: true, dataLabelPosition: 't', dataLabelFormatCode: '0"%"', valAxisMaxVal: 100, valAxisLabelFormatCode: '0"%"',
  showLegend: true, legendPos: 'b', showTitle: true, title: '점검 대상(위험 점수 상위 %)별 탈퇴 사업장 포착률', titleFontSize: 12, titleColor: HEX.dk2,
  objectName: 'capture chart',
}, axis));
card(s, 6.5, 1.05, 3.0, 1.3, HEX.lt2, 'final stat card 1');
stat(s, 6.7, 1.15, 2.6, Math.round(N.cap_random[0]) + '배', '상위 1% 점검 시 무작위 대비 효율', C.accent1, 'lift stat');
card(s, 6.5, 2.5, 3.0, 2.55, HEX.lt2, 'final metrics card');
s.addText([
  { text: '최종 모델', options: { bold: true, fontSize: 13, color: HEX.dk2, breakLine: true } },
  { text: 'RandomForest (GridSearchCV) + FI-SMOTE', options: { fontSize: 11, color: HEX.accent5, breakLine: true } },
  { text: `F1 ${N.final.F1.toFixed(3)} · MCC ${N.final.MCC.toFixed(3)}`, options: { fontSize: 13, color: HEX.dk1, breakLine: true } },
  { text: `ROC-AUC ${N.final['ROC-AUC'].toFixed(3)} · PR-AUC ${N.final['PR-AUC'].toFixed(3)}`, options: { fontSize: 13, color: HEX.dk1, breakLine: true } },
  { text: '테스트셋 102,709곳 (탈퇴 407곳)', options: { fontSize: 11, color: HEX.accent5 } },
], { x: 6.7, y: 2.6, w: 2.7, h: 2.35, valign: 'top', margin: 0, paraSpaceAfter: 5, isTextBox: true, objectName: 'final metrics text' });
s.addNotes(`튜닝한 랜덤포레스트에 FI-SMOTE를 적용한 최종 모델은 테스트셋에서 F1 ${N.final.F1.toFixed(2)}, ROC-AUC ${N.final['ROC-AUC'].toFixed(2)}였습니다. 개별 사업장을 정확히 맞히기는 어렵지만, 위험 점수 순으로 줄을 세우면 상위 1%만 점검해도 탈퇴 사업장의 ${Math.round(N.cap_random[0])}%를 찾습니다. 무작위보다 ${Math.round(N.cap_random[0])}배 효율적입니다.`);

// 8. Robustness ------------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '결과' });
s.addText('과거로 학습해도, 건설업을 빼도 통하는가', { placeholder: 'title' });
s.addChart(pres.charts.LINE, [
  { name: '무작위 분할 (7월 안에서 8:2)', labels: pctLabels, values: N.cap_random },
  { name: '시간 기반 (4월 학습 → 7월 평가)', labels: pctLabels, values: N.cap_time },
], Object.assign({
  x: 0.5, y: 1.0, w: 5.8, h: 4.05, chartColors: [HEX.accent1, HEX.accent2], lineSize: 2.5, lineDataSymbol: 'circle', lineDataSymbolSize: 7,
  showValue: false, valAxisMaxVal: 100, valAxisLabelFormatCode: '0"%"',
  showLegend: true, legendPos: 'b', showTitle: true, title: '탈퇴 사업장 포착률 비교 (점검 대상 상위 %)', titleFontSize: 12, titleColor: HEX.dk2,
  objectName: 'robust capture chart',
}, axis));
const segNoCon = N.seg['건설업 제외'];
const rows = [
  ['시간 기반 검증', `상위 5% 포착 ${pct1(N.time['Recall@상위5%'])} · ROC-AUC ${N.time['ROC-AUC'].toFixed(3)}`],
  ['건설업 제외', `상위 5% 포착 ${pct1(segNoCon['Recall@상위5%'])} · ROC-AUC ${segNoCon['ROC-AUC'].toFixed(3)}`],
  ['사라진 곳도 탈퇴로', `탈퇴율 ${N.wide['탈퇴율(%)'].toFixed(1)}% · ROC-AUC ${N.wide['ROC-AUC'].toFixed(3)}`],
];
rows.forEach((r, i) => {
  const y = 1.05 + i * 1.35;
  card(s, 6.5, y, 3.0, 1.2, HEX.lt2, 'robust card ' + (i + 1));
  s.addText([{ text: r[0], options: { bold: true, fontSize: 13, color: HEX.accent2, breakLine: true } }, { text: r[1], options: { fontSize: 12, color: HEX.dk1 } }],
    { x: 6.65, y: y + 0.08, w: 2.75, h: 1.05, valign: 'middle', margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: 'robust text ' + (i + 1) });
});
s.addNotes(`결과가 믿을 만한지 세 가지로 확인했습니다. 첫째, 4월 기준 데이터로 학습하고 7월 기준으로 평가하는 시간 기반 검증에서 상위 5% 포착률이 ${pct1(N.time['Recall@상위5%'])}였습니다. 둘째, 건설업을 빼고 평가해도 상위 5% 포착률이 ${pct1(segNoCon['Recall@상위5%'])}였습니다. 셋째, 파일에서 사라진 사업장까지 탈퇴로 봐도 ROC-AUC ${N.wide['ROC-AUC'].toFixed(2)}로 예측이 됐습니다.`);

// 9. Feature importance ---------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '결과' });
s.addText('무엇이 탈퇴를 알려주는가', { placeholder: 'title' });
s.addChart(pres.charts.BAR, [{ name: '중요도', labels: N.fi_names, values: N.fi_values }], Object.assign({
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

// 10. Conclusion ----------------------------------------------------------
pres.addSection({ title: '결론' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '결론' });
s.addText('결론: "확정 판정"보다 "점검 우선순위" 도구', { placeholder: 'title' });
card(s, 0.5, 1.0, 4.4, 3.35, HEX.lt2, 'action card');
s.addText('실행 제언', { x: 0.7, y: 1.1, w: 4.0, h: 0.4, fontSize: 15, bold: true, color: C.accent1, margin: 0, isTextBox: true, objectName: 'action title' });
bullets(s, [
  '고용센터·지자체: 매월 위험 상위 1~5%를 고용지원·체불 예방 점검 대상으로',
  '거래 기업·금융: 재무제표보다 빠른 거래처 위험 보조 지표',
  '건설 현장은 별도 모델로 분리',
], { x: 0.7, y: 1.6, w: 4.0, h: 2.7, fontSize: 15 });
card(s, 5.1, 1.0, 4.4, 3.35, HEX.lt2, 'limit card');
s.addText('한계와 다음 단계', { x: 5.3, y: 1.1, w: 4.0, h: 0.4, fontSize: 15, bold: true, color: C.accent2, margin: 0, isTextBox: true, objectName: 'limit title' });
bullets(s, [
  '"탈퇴"에 폐업·현장 종료·휴업이 섞여 있음',
  '고지금액 상한, 6자리 사업자번호로 인한 연결 오류 가능',
  '여러 기준월을 쌓아 계절성 반영, 국세청 휴·폐업 정보와 결합',
], { x: 5.3, y: 1.6, w: 4.0, h: 2.7, fontSize: 15 });
s.addText([
  { text: '소스코드 ', options: { bold: true, color: HEX.dk2 } },
  { text: 'github.com/cholin3721/NPS-Workplace-Exit-Prediction', options: { color: HEX.accent2, breakLine: true } },
  { text: '데이터 ', options: { bold: true, color: HEX.dk2 } },
  { text: '공공데이터포털 「국민연금공단_국민연금 가입 사업장 내역」 · 생성형 AI(Claude) 활용 내역은 보고서 5장', options: { color: HEX.accent5 } },
], { x: 0.5, y: 4.55, w: 9.0, h: 0.6, fontSize: 11, margin: 0, valign: 'middle', isTextBox: true, objectName: 'source text' });
s.addNotes('정리하면, 공공데이터만으로 탈퇴 위험이 높은 사업장을 무작위보다 훨씬 효율적으로 골라낼 수 있었고, 과거 데이터로 학습해도 성능이 유지됐습니다. 개별 사업장을 확정하기보다는 점검 우선순위를 정하는 도구로 쓰는 게 적합합니다. 한계로는 탈퇴에 현장 종료가 섞여 있다는 점이 있어, 국세청 휴폐업 정보와 결합하는 것을 다음 과제로 남깁니다. 감사합니다.');

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('saved', OUT);
})();
