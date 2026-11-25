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
const fiIdx = N.samplers.indexOf('FI-SMOTE');
const top5 = Math.round(N.final['Recall@상위5%'] * 100);
const top5Time = Math.round(N.time['Recall@상위5%'] * 100);
const top5NoCon = Math.round(N.seg['건설업 제외']['Recall@상위5%'] * 100);
const PLAIN = { '신규진입': '최근 3개월 내 새로 등록', '업력': '회사 나이(업력)', '가입자수': '직원 수', '취득률': '입사자 비율',
  '고지금액증감률_3개월': '월급 총액 변화(3개월)', '업종대분류': '업종', '상실률': '퇴사자 비율', '1인당고지금액': '1인당 월급 수준' };
const SAMPLER_PLAIN = { '없음': '그대로', 'SMOTE': 'SMOTE', 'ADASYN': 'ADASYN', 'FI-SMOTE': 'FI-SMOTE\n(직접 만든 방법)' };

function sourceNote(slide, text) {
  slide.addText(text, { x: 0.5, y: 4.95, w: 9.0, h: 0.25, fontSize: 9, color: C.accent5, margin: 0, isTextBox: true, objectName: 'source note' });
}

// 1. 표지 -------------------------------------------------------------------
pres.addSection({ title: '왜' });
let s = pres.addSlide({ masterName: 'TITLE_DARK', sectionTitle: '왜' });
s.addText('회사가 문 닫기 전에,\n미리 알 수 있을까?', { placeholder: 'title' });
s.addText('국민연금 가입 사업장 데이터로 본 사업장 탈퇴 3개월 조기 예측\n데이터분석 기말 프로젝트 · 202444085 김철중', { placeholder: 'body' });
s.addNotes('안녕하세요, 김철중입니다. 제 주제는 "회사가 문 닫기 전에 미리 알 수 있을까"입니다. 국민연금 공개 데이터로 3개월 안에 문을 닫거나 국민연금에서 빠질 회사를 미리 찾아보았습니다.');

// 2. 왜 필요한가 ------------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '왜' });
s.addText('회사가 문을 닫으면, 피해는 직원에게 먼저 온다', { placeholder: 'title' });
const why = [
  ['97.6만 명', '2025년 폐업한 사업자\n하루 약 2,700곳', C.text2],
  ['2조 679억 원', '2025년 밀린 월급\n(임금체불액, 역대 최대)', C.accent1],
  ['26.2만 명', '2025년 월급을\n제때 못 받은 노동자', C.accent2],
];
why.forEach((w, i) => {
  const x = 0.5 + i * 3.05;
  card(s, x, 1.05, 2.85, 1.9, HEX.lt2, 'why card ' + (i + 1));
  stat(s, x + 0.2, 1.2, 2.5, w[0], w[1], w[2], 'why stat ' + (i + 1), 26);
});
card(s, 0.5, 3.15, 9.0, 1.6, HEX.dk2, 'why message card');
s.addText([
  { text: '터진 다음에 수습하면 늦다', options: { bold: true, fontSize: 16, color: HEX.accent4, breakLine: true } },
  { text: '정부가 밀린 월급을 대신 준 돈(대지급금) 6,845억 원 중 회사로부터 돌려받은 건 26%뿐. 위험한 회사를 미리 알면 점검·상담으로 피해를 줄일 수 있다.', options: { fontSize: 14, color: HEX.lt1 } },
], { x: 0.75, y: 3.2, w: 8.5, h: 1.5, valign: 'middle', margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: 'why message' });
sourceNote(s, '출처: 국세청 국세통계(연합뉴스 2026.7.6 보도), 고용노동부 임금체불 현황(경향신문 2026.2.20 보도)');
s.addNotes('왜 이 연구가 필요한지부터 말씀드리겠습니다. 작년에만 97만 명, 하루에 2,700곳 정도가 문을 닫았습니다. 회사가 어려워지면 가장 먼저 피해를 보는 건 직원입니다. 작년에 밀린 월급이 2조 원이 넘고, 26만 명이 월급을 제때 못 받았습니다. 정부가 대신 준 돈도 4분의 1만 돌려받았습니다. 그래서 터진 뒤에 수습하는 것보다, 위험한 회사를 미리 알아서 점검하고 상담하는 게 중요하다고 생각했습니다.');

// 3. 그런데 미리 알기 어렵다 -------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '왜' });
s.addText('그런데 지금은 미리 알기가 어렵다', { placeholder: 'title' });
card(s, 0.5, 1.05, 4.4, 2.0, HEX.lt2, 'old way card');
s.addText([
  { text: '지금까지: 재무제표', options: { bold: true, fontSize: 16, color: HEX.accent5, breakLine: true } },
  { text: '1년에 한 번 나온다 → 알았을 땐 이미 늦음', options: { fontSize: 14, color: HEX.dk1, breakLine: true } },
  { text: '작은 회사는 아예 공개하지 않는다', options: { fontSize: 14, color: HEX.dk1 } },
], { x: 0.7, y: 1.15, w: 4.0, h: 2.1, valign: 'top', margin: 0, paraSpaceAfter: 8, isTextBox: true, objectName: 'old way text' });
card(s, 5.1, 1.05, 4.4, 2.0, HEX.lt2, 'new way card');
s.addText([
  { text: '이 프로젝트: 국민연금 데이터', options: { bold: true, fontSize: 16, color: HEX.accent2, breakLine: true } },
  { text: '매달 공개, 전국 59만 개 회사', options: { fontSize: 14, color: HEX.dk1, breakLine: true } },
  { text: '직원 수·월급 총액·입사자·퇴사자', options: { fontSize: 14, color: HEX.dk1, breakLine: true } },
  { text: '→ 회사의 "월간 건강검진표"', options: { fontSize: 14, bold: true, color: HEX.accent2 } },
], { x: 5.3, y: 1.15, w: 4.0, h: 2.1, valign: 'top', margin: 0, paraSpaceAfter: 8, isTextBox: true, objectName: 'new way text' });
card(s, 0.5, 3.3, 9.0, 1.3, HEX.accent1, 'question card');
s.addText('질문: 이 건강검진표만 보고, 3개월 안에 문 닫을 회사를 미리 골라낼 수 있을까?',
  { x: 0.75, y: 3.35, w: 8.5, h: 1.2, fontSize: 17, bold: true, color: HEX.lt1, valign: 'middle', margin: 0, isTextBox: true, objectName: 'question text' });
s.addNotes('그런데 지금은 미리 알기가 어렵습니다. 보통 재무제표를 보는데, 1년에 한 번 나오고 작은 회사는 공개도 안 합니다. 반면 국민연금 데이터는 59만 개 회사의 직원 수, 월급 총액, 입사자와 퇴사자 수를 매달 공개합니다. 회사의 월간 건강검진표인 셈이죠. 그래서 이 건강검진표만으로 3개월 안에 문 닫을 회사를 골라낼 수 있는지 확인해 봤습니다. 이런 방식의 연구는 찾지 못했습니다.');

// 4. 어떻게 했나 -------------------------------------------------------------
pres.addSection({ title: '어떻게' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '어떻게' });
s.addText('어떻게 했나: 회사마다 "위험 점수"를 매긴다', { placeholder: 'title' });
const flow = [
  ['1', '매달 파일 연결', '5개월치 파일을\n같은 회사끼리 연결'],
  ['2', '특징 17개 만들기', '회사 나이, 직원 수,\n입·퇴사, 월급 총액 변화'],
  ['3', '정답 붙이기', '3개월 뒤 국민연금에서\n빠졌는지(탈퇴) 확인'],
  ['4', '위험 점수 학습', '머신러닝이 패턴을 배워\n회사별 점수 계산'],
];
flow.forEach((f, i) => {
  const x = 0.5 + i * 2.3;
  card(s, x, 1.05, 2.1, 2.45, i === 3 ? HEX.dk2 : HEX.lt2, 'flow card ' + (i + 1));
  s.addText([
    { text: f[0], options: { bold: true, fontSize: 26, color: i === 3 ? HEX.accent4 : HEX.accent1, breakLine: true } },
    { text: f[1], options: { bold: true, fontSize: 15, color: i === 3 ? HEX.lt1 : HEX.dk2, breakLine: true } },
    { text: f[2], options: { fontSize: 12, color: i === 3 ? HEX.accent3 : HEX.dk1 } },
  ], { x: x + 0.15, y: 1.15, w: 1.8, h: 2.25, valign: 'top', margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: 'flow text ' + (i + 1) });
  if (i < 3) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.12, y: 2.15, w: 0.16, h: 0.24, fill: { color: HEX.accent5 }, line: { color: HEX.accent5 }, objectName: 'flow arrow ' + (i + 1) });
});
card(s, 0.5, 3.7, 9.0, 1.15, HEX.lt2, 'data size card');
s.addText([
  { text: '513,541곳', options: { bold: true, fontSize: 22, color: HEX.dk2 } },
  { text: '  을 분석했고, 그중 3개월 안에 탈퇴한 곳은  ', options: { fontSize: 15, color: HEX.dk1 } },
  { text: '2,033곳 (0.4%)', options: { bold: true, fontSize: 22, color: HEX.accent1 } },
], { x: 0.75, y: 3.75, w: 8.5, h: 1.05, valign: 'middle', margin: 0, isTextBox: true, objectName: 'data size text' });
s.addNotes('방법은 네 단계입니다. 매달 나오는 파일 다섯 개를 같은 회사끼리 이어 붙이고, 회사 나이, 직원 수, 입사·퇴사, 월급 총액 변화 같은 특징을 만들었습니다. 그리고 3개월 뒤에 국민연금에서 빠졌는지를 정답으로 붙여서, 머신러닝이 회사마다 위험 점수를 매기도록 학습시켰습니다. 51만 곳 중 3개월 안에 빠진 곳은 2,033곳, 0.4%였습니다.');

// 5. 데이터에서 본 것 --------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '어떻게' });
s.addText('데이터를 보니: 작고, 새로 생긴 회사가 위험했다', { placeholder: 'title' });
s.addImage({ path: FIG('02_size_age_rate.png'), x: 0.5, y: 1.0, w: 5.9, h: 1.93, objectName: 'size age chart', altText: '직원 수별, 회사 나이별 3개월 내 탈퇴율 그래프' });
s.addText('왼쪽: 직원 수별 탈퇴율 · 오른쪽: 회사 나이별 탈퇴율', { x: 0.5, y: 2.95, w: 5.9, h: 0.25, fontSize: 10, color: C.accent5, margin: 0, isTextBox: true, objectName: 'chart caption' });
const finds = [
  ['직원 1~4명', '100명 이상 회사보다\n탈퇴율 약 16배'],
  ['생긴 지 1년 미만', '20년 넘은 회사보다\n탈퇴율 약 60배'],
];
finds.forEach((f, i) => {
  const y = 1.0 + i * 1.12;
  card(s, 6.6, y, 2.9, 1.0, HEX.lt2, 'find card ' + (i + 1));
  s.addText([{ text: f[0], options: { bold: true, fontSize: 14, color: HEX.accent1, breakLine: true } }, { text: f[1], options: { fontSize: 12, color: HEX.dk1 } }],
    { x: 6.75, y: y + 0.05, w: 2.65, h: 0.9, valign: 'middle', margin: 0, isTextBox: true, objectName: 'find text ' + (i + 1) });
});
card(s, 0.5, 3.35, 9.0, 1.5, HEX.lt2, 'construction card');
s.addText([
  { text: '탈퇴한 곳의 절반(49%)은 건설·공사 현장', options: { bold: true, fontSize: 15, color: HEX.accent1, breakLine: true } },
  { text: '건설사는 공사 현장마다 사업장을 따로 등록했다가 공사가 끝나면 탈퇴한다. 그래서 여기서 "탈퇴"는 폐업만이 아니라 공사 종료·휴업도 포함한다는 점에 주의했다.', options: { fontSize: 13, color: HEX.dk1 } },
], { x: 0.75, y: 3.4, w: 8.5, h: 1.4, valign: 'middle', margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: 'construction text' });
s.addNotes('데이터를 먼저 살펴봤더니, 직원이 1~4명인 작은 회사는 100명 이상 회사보다 탈퇴율이 16배, 생긴 지 1년이 안 된 회사는 20년 넘은 회사보다 60배 높았습니다. 그리고 탈퇴한 곳의 절반이 건설 현장이었는데, 공사가 끝나면 현장 사업장을 정리하기 때문입니다. 그래서 여기서 말하는 탈퇴에는 폐업뿐 아니라 공사 종료도 들어 있다는 점을 염두에 뒀습니다.');

// 6. 어려웠던 점 -------------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '어떻게' });
s.addText('어려웠던 점: 1,000곳 중 4곳을 찾는 문제', { placeholder: 'title' });
card(s, 0.5, 1.05, 4.4, 1.75, HEX.lt2, 'trap card');
s.addText([
  { text: '"다 괜찮다"고만 해도 정답률 99.6%', options: { bold: true, fontSize: 15, color: HEX.accent1, breakLine: true } },
  { text: '그래서 정답률 대신 "문 닫을 회사를 몇 곳 찾았나"로 평가했다', options: { fontSize: 13, color: HEX.dk1 } },
], { x: 0.7, y: 1.1, w: 4.0, h: 1.65, valign: 'middle', margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: 'trap text' });
card(s, 0.5, 2.95, 4.4, 1.9, HEX.lt2, 'fismote card');
s.addText([
  { text: '해결: 예시를 늘려서 학습 (FI-SMOTE)', options: { bold: true, fontSize: 15, color: HEX.accent2, breakLine: true } },
  { text: '탈퇴한 회사 예시가 너무 적어서, 진짜와 비슷한 가상 예시를 만들어 학습시켰다. 1학기에 직접 만든 방법 (원리는 다음 장)', options: { fontSize: 13, color: HEX.dk1 } },
], { x: 0.7, y: 3.0, w: 4.0, h: 1.8, valign: 'middle', margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: 'fismote text' });
s.addChart(pres.charts.BAR, [{ name: 'F1', labels: N.samplers.map((x) => SAMPLER_PLAIN[x]), values: N.cv5_f1 }], Object.assign({
  x: 5.1, y: 1.0, w: 4.4, h: 3.85, barDir: 'col', chartColors: [HEX.accent3, HEX.accent3, HEX.accent3, HEX.accent1],
  showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.00', valAxisHidden: true, valAxisMaxVal: 0.25, showLegend: false,
  showTitle: true, title: '탈퇴 회사를 맞힌 정도 (F1, 5번 반복 평균)', titleFontSize: 12, titleColor: HEX.dk2, objectName: 'sampler f1 chart',
}, axis));
s.addNotes(`어려웠던 점은 탈퇴하는 회사가 1,000곳 중 4곳밖에 안 된다는 겁니다. 그래서 "다 괜찮다"고만 말해도 정답률이 99.6%가 나옵니다. 그래서 정답률 대신 문 닫을 회사를 몇 곳이나 찾았는지로 평가했습니다. 또 탈퇴 예시가 너무 적어서, 제가 1학기에 만든 FI-SMOTE로 진짜와 비슷한 가상 예시를 만들어 학습시켰습니다. 다섯 번 반복해서 비교했는데, 다른 방법들보다 매번 더 잘 찾았습니다. 알고리즘은 교안에서 배운 7개를 비교해서 랜덤포레스트를 골랐습니다.`);

// 6-2. FI-SMOTE 원리 ----------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '어떻게' });
s.addText('FI-SMOTE: 가상 예시를 "진짜처럼" 만드는 방법', { placeholder: 'title' });
const steps3 = [
  ['1', '중요한 특징부터 고른다', '랜덤포레스트로 "탈퇴를 가르는 데 중요한 특징"을 먼저 찾는다 (예: 회사 나이, 직원 수)'],
  ['2', '헷갈리는 회사 위주로 만든다', '멀쩡한 회사와 비슷해서 구분이 어려운 탈퇴 회사 주변에 예시를 더 많이 만든다'],
  ['3', '중요한 건 그대로, 나머지는 자유롭게', '새 예시를 만들 때 중요한 특징은 원래 값 근처에, 덜 중요한 특징은 넓게 섞는다'],
];
steps3.forEach((st, i) => {
  const y = 1.0 + i * 1.22;
  card(s, 0.5, y, 4.5, 1.1, HEX.lt2, 'fi step card ' + (i + 1));
  s.addText(st[0], { x: 0.6, y: y + 0.15, w: 0.55, h: 0.8, fontSize: 26, bold: true, color: HEX.accent1, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: 'fi step num ' + (i + 1) });
  s.addText([{ text: st[1], options: { bold: true, fontSize: 14, color: HEX.dk2, breakLine: true } }, { text: st[2], options: { fontSize: 11, color: HEX.dk1 } }],
    { x: 1.25, y: y + 0.06, w: 3.65, h: 0.98, valign: 'middle', margin: 0, paraSpaceAfter: 3, isTextBox: true, objectName: 'fi step text ' + (i + 1) });
});
s.addText('예시: 진짜 탈퇴 회사 A와 B 사이에 새 예시 만들기', { x: 5.25, y: 1.0, w: 4.25, h: 0.3, fontSize: 12, bold: true, color: C.text2, margin: 0, isTextBox: true, objectName: 'example title' });
const H_ = (t, fill, color) => ({ text: t, options: { bold: true, fill: { color: fill }, color: color || HEX.dk2, align: 'center', fontSize: 11 } });
const D_ = (t, opts) => ({ text: t, options: Object.assign({ align: 'center', fontSize: 11, color: HEX.dk1 }, opts || {}) });
s.addTable([
  [H_('특징', HEX.lt2), H_('회사 A', HEX.lt2), H_('회사 B', HEX.lt2), H_('SMOTE', 'D9E2F3'), H_('FI-SMOTE', HEX.accent1, HEX.lt1)],
  [D_('회사 나이 ★', { bold: true }), D_('0.8년'), D_('2.0년'), D_('1.4년'), D_('0.9년', { bold: true, color: HEX.accent1 })],
  [D_('직원 수 ★', { bold: true }), D_('3명'), D_('7명'), D_('5명'), D_('3.4명', { bold: true, color: HEX.accent1 })],
  [D_('최근 입사자'), D_('0명'), D_('2명'), D_('1명'), D_('1.6명')],
  [D_('1인당 월급 수준'), D_('250만'), D_('330만'), D_('290만'), D_('265만')],
], { x: 5.25, y: 1.35, w: 4.25, colW: [1.25, 0.7, 0.7, 0.75, 0.85], rowH: 0.36, border: { type: 'solid', pt: 0.75, color: 'C9D1DC' }, margin: 0.03, objectName: 'example table' });
card(s, 5.25, 3.3, 4.25, 1.4, HEX.dk2, 'example message card');
s.addText([
  { text: 'SMOTE: 모든 특징을 똑같이 반씩 섞는다 → 탈퇴 회사의 핵심 모습(어리고 작음)이 흐려짐', options: { fontSize: 11, color: HEX.lt1, breakLine: true } },
  { text: 'FI-SMOTE: ★중요한 특징은 A 그대로, 나머지만 섞는다 → 진짜 같은 예시', options: { fontSize: 11, bold: true, color: HEX.accent4 } },
], { x: 5.4, y: 3.35, w: 3.95, h: 1.3, valign: 'middle', margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: 'example message' });
sourceNote(s, '표의 숫자는 원리를 설명하기 위한 가상값 · FI-SMOTE: 조규철·김철중, 한국컴퓨터정보학회 학술발표 2026 (신용카드 사기 0.17%에서도 효과 확인)');
s.addNotes('FI-SMOTE가 어떻게 가상 예시를 만드는지 설명드리겠습니다. 먼저 랜덤포레스트로 탈퇴를 가르는 데 중요한 특징, 예를 들어 회사 나이와 직원 수를 찾습니다. 그다음 멀쩡한 회사와 비슷해서 헷갈리는 탈퇴 회사 주변에 예시를 더 많이 만듭니다. 마지막으로 두 탈퇴 회사 사이에서 새 예시를 만들 때, 중요한 특징은 원래 값 근처에 두고 덜 중요한 특징만 넓게 섞습니다. 오른쪽 예시처럼 기존 SMOTE는 모든 특징을 똑같이 반씩 섞어서 "어리고 작은 회사"라는 탈퇴 회사의 핵심 모습이 흐려지는데, FI-SMOTE는 그 핵심을 지키면서 나머지만 다양하게 만듭니다. 이 방법은 제가 1학기에 학술대회 논문으로 제안했고, 신용카드 사기 데이터에서도 효과를 확인했습니다.');

// 7. 결과 ---------------------------------------------------------------------
pres.addSection({ title: '결과' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '결과' });
s.addText(`결과: 상위 5%만 봐도 문 닫을 회사의 ${top5}%를 찾는다`, { placeholder: 'title' });
const pctLabels = N.cap_pcts.map((p) => p + '%');
s.addChart(pres.charts.LINE, [
  { name: '위험 점수 높은 순으로 살펴볼 때', labels: pctLabels, values: N.cap_random },
  { name: '아무렇게나 골라 살펴볼 때', labels: pctLabels, values: N.cap_pcts },
], Object.assign({
  x: 0.5, y: 1.0, w: 5.8, h: 3.85, chartColors: [HEX.accent1, 'A0A8B3'], lineSize: 2.5, lineDataSymbol: 'circle', lineDataSymbolSize: 7,
  showValue: true, dataLabelPosition: 't', dataLabelFormatCode: '0"%"', valAxisMaxVal: 100, valAxisLabelFormatCode: '0"%"',
  showLegend: true, legendPos: 'b', showTitle: true, title: '살펴본 회사 비율(가로) vs 찾아낸 탈퇴 회사 비율(세로)', titleFontSize: 12, titleColor: HEX.dk2,
  objectName: 'capture chart',
}, axis));
card(s, 6.5, 1.05, 3.0, 3.8, HEX.lt2, 'result card');
s.addText([
  { text: '100곳 중 5곳만 살펴보면', options: { fontSize: 14, color: HEX.dk1, breakLine: true } },
  { text: `${top5}%`, options: { bold: true, fontSize: 40, color: HEX.accent1, breakLine: true } },
  { text: '문 닫을 회사를 찾아낸다', options: { fontSize: 14, color: HEX.dk1, breakLine: true } },
  { text: ' ', options: { fontSize: 8, breakLine: true } },
  { text: `아무렇게나 고르면 5% → ${Math.round(top5 / 5)}배`, options: { bold: true, fontSize: 13, color: HEX.accent2 } },
], { x: 6.7, y: 1.15, w: 2.6, h: 3.6, valign: 'middle', margin: 0, isTextBox: true, objectName: 'result text' });
s.addNotes(`결과입니다. 모든 회사를 위험 점수 순으로 줄 세운 다음 위에서부터 살펴본다고 해 보겠습니다. 전체의 5%만 살펴봐도 실제로 문 닫을 회사의 ${top5}%를 찾아냅니다. 아무렇게나 5%를 고르면 5%밖에 못 찾으니까 약 ${Math.round(top5 / 5)}배 효율적입니다. 한 곳 한 곳을 확정하기는 어렵지만, 어디부터 살펴볼지 순서를 정하는 데는 충분히 쓸 수 있습니다.`);

// 8. 믿을 만한가 ------------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '결과' });
s.addText('믿을 만한가: 세 가지로 다시 확인했다', { placeholder: 'title' });
const checks = [
  ['지난 분기로 배워서 이번 분기에 써도', `상위 5%로 ${top5Time}% 찾음`, '4월 데이터로 학습 → 7월 데이터로 평가 (실제로 쓰는 상황)'],
  ['건설 현장을 빼고 봐도', `상위 5%로 ${top5NoCon}% 찾음`, '"건설이면 위험"만 외운 게 아니다'],
  ['"사라진 회사"까지 탈퇴로 쳐도', '예측력 유지', `기준을 바꿔도 결론이 같다 (탈퇴율 ${N.wide['탈퇴율(%)'].toFixed(1)}%)`],
];
checks.forEach((c, i) => {
  const y = 1.05 + i * 1.28;
  card(s, 0.5, y, 9.0, 1.12, HEX.lt2, 'check card ' + (i + 1));
  s.addText(String(i + 1), { x: 0.7, y: y + 0.16, w: 0.8, h: 0.8, fontSize: 28, bold: true, color: HEX.accent2, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: 'check num ' + (i + 1) });
  s.addText([{ text: c[0], options: { bold: true, fontSize: 15, color: HEX.dk2, breakLine: true } }, { text: c[2], options: { fontSize: 12, color: HEX.accent5 } }],
    { x: 1.6, y: y + 0.08, w: 4.9, h: 0.96, valign: 'middle', margin: 0, isTextBox: true, objectName: 'check text ' + (i + 1) });
  s.addText(c[1], { x: 6.6, y: y + 0.08, w: 2.75, h: 0.96, fontSize: 18, bold: true, color: HEX.accent1, align: 'right', valign: 'middle', margin: 0, isTextBox: true, objectName: 'check result ' + (i + 1) });
});
s.addNotes(`이 결과가 우연이 아닌지 세 가지로 다시 확인했습니다. 첫째, 실제로 쓸 때처럼 지난 분기 데이터로 배우고 이번 분기에 적용해도 상위 5%로 ${top5Time}%를 찾았습니다. 둘째, 건설 현장을 빼고 봐도 ${top5NoCon}%를 찾아서, 건설이면 위험하다는 것만 외운 게 아니었습니다. 셋째, 파일에서 사라진 회사까지 탈퇴로 쳐도 예측력이 유지됐습니다.`);

// 9. 신호 -----------------------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '결과' });
s.addText('무엇이 위험 신호였나', { placeholder: 'title' });
s.addChart(pres.charts.BAR, [{ name: '중요도', labels: N.fi_names.map((x) => PLAIN[x] || x), values: N.fi_values }], Object.assign({
  x: 0.5, y: 1.0, w: 5.2, h: 3.85, barDir: 'bar', chartColors: [HEX.dk2], showValue: true, dataLabelPosition: 'outEnd',
  dataLabelFormatCode: '0.00', valAxisHidden: true, valAxisMaxVal: 0.19, showLegend: false,
  showTitle: true, title: '모델이 중요하게 본 특징 TOP 6', titleFontSize: 12, titleColor: HEX.dk2, objectName: 'importance chart',
}, axis));
const fx = [
  ['최근에 새로 생긴 사업장', '기존 사업장보다 탈퇴율 5배 (공사 현장 등)'],
  ['회사 나이가 어릴수록', '어린 10% 2.3% vs 오래된 10% 0.04%'],
  ['직원이 적을수록', '1~4명 회사 탈퇴율 0.62%'],
  ['인원 급변 · 월급 총액 감소', '갑자기 들고 나거나 월급이 줄면 이상 신호'],
];
fx.forEach((f, i) => {
  const y = 1.0 + i * 0.97;
  card(s, 5.95, y, 3.55, 0.85, HEX.lt2, 'signal card ' + (i + 1));
  s.addText([{ text: f[0], options: { bold: true, fontSize: 13, color: HEX.accent1, breakLine: true } }, { text: f[1], options: { fontSize: 11, color: HEX.dk1 } }],
    { x: 6.1, y: y + 0.04, w: 3.3, h: 0.77, valign: 'middle', margin: 0, isTextBox: true, objectName: 'signal text ' + (i + 1) });
});
s.addNotes('모델이 중요하게 본 신호는 최근에 새로 생겼는지, 회사 나이, 직원 수였습니다. 최근에 생긴 사업장은 탈퇴율이 5배였고, 회사 나이가 어릴수록, 직원이 적을수록 위험했습니다. 그다음으로 사람이 갑자기 많이 들고 나거나 월급 총액이 줄어드는 것이 이상 신호였습니다.');

// 10. 결론 ---------------------------------------------------------------------
pres.addSection({ title: '결론' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '결론' });
s.addText('이렇게 쓸 수 있다', { placeholder: 'title' });
const uses = [
  ['고용센터·지자체', '매달 위험 상위 회사부터 임금체불 예방 점검·상담'],
  ['거래하는 회사·은행', '재무제표보다 먼저 거래처 위험 확인'],
  ['창업 지원 기관', '생긴 지 얼마 안 된 작은 회사에 컨설팅 연결'],
];
uses.forEach((u, i) => {
  const x = 0.5 + i * 3.05;
  card(s, x, 1.0, 2.85, 1.45, HEX.lt2, 'use card ' + (i + 1));
  s.addText([{ text: u[0], options: { bold: true, fontSize: 15, color: HEX.accent1, breakLine: true } }, { text: u[1], options: { fontSize: 13, color: HEX.dk1 } }],
    { x: x + 0.2, y: 1.1, w: 2.45, h: 1.25, valign: 'top', margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: 'use text ' + (i + 1) });
});
card(s, 0.5, 2.65, 9.0, 1.55, HEX.dk2, 'limit card');
s.addText([
  { text: '한계와 다음 단계', options: { bold: true, fontSize: 15, color: HEX.accent3, breakLine: true } },
  { text: '"탈퇴"에는 폐업 말고도 공사 종료·휴업이 섞여 있다 → 국세청 휴·폐업 정보와 합치면 "진짜 폐업"만 볼 수 있다. 두 분기만 검증했으니 1년 이상으로 늘려 보고 싶다.', options: { fontSize: 13, color: HEX.lt1 } },
], { x: 0.75, y: 2.7, w: 8.5, h: 1.45, valign: 'middle', margin: 0, paraSpaceAfter: 6, isTextBox: true, objectName: 'limit text' });
s.addText([
  { text: '코드·보고서 ', options: { bold: true, color: HEX.dk2 } },
  { text: 'github.com/cholin3721/NPS-Workplace-Exit-Prediction', options: { color: HEX.accent2 } },
  { text: '   데이터 ', options: { bold: true, color: HEX.dk2 } },
  { text: '공공데이터포털 「국민연금 가입 사업장 내역」', options: { color: HEX.accent5 } },
], { x: 0.5, y: 4.45, w: 9.0, h: 0.4, fontSize: 11, margin: 0, valign: 'middle', isTextBox: true, objectName: 'source text' });
s.addNotes('이 모델은 회사를 확정 판정하는 도구가 아니라, 어디부터 살펴볼지 순서를 정하는 도구입니다. 고용센터는 위험한 회사부터 임금체불 예방 점검을 하고, 거래하는 회사나 은행은 재무제표보다 먼저 거래처 위험을 확인하고, 창업 지원 기관은 작은 신생 회사를 도울 수 있습니다. 한계는 탈퇴에 공사 종료나 휴업이 섞여 있다는 점이라, 국세청 휴폐업 정보와 합쳐 보는 것을 다음 과제로 남기겠습니다. 감사합니다.');

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('saved', OUT);
})();
