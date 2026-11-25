"""results/*.csv 에서 발표자료에 들어갈 숫자를 모아 tools/deck_numbers.json 으로 저장"""
import json, os, sys
import pandas as pd

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = lambda f: os.path.join(ROOT, 'results', f)

cv = pd.read_csv(R('model_cv_result.csv'), encoding='utf-8-sig').sort_values('average_precision')
fin = pd.to_numeric(pd.read_csv(R('final_summary.csv'), encoding='utf-8-sig', index_col=0).iloc[:, 0], errors='coerce')
fi = pd.read_csv(R('feature_importance.csv'), encoding='utf-8-sig', index_col=0).iloc[:, 0]
rep = pd.read_csv(R('imbalance_cv5_folds.csv'), encoding='utf-8-sig')
wins = pd.read_csv(R('imbalance_cv5_wins.csv'), encoding='utf-8-sig', index_col=0)
cap = pd.read_csv(R('time_validation_capture.csv'), encoding='utf-8-sig')
extra = pd.read_csv(R('extra_validation.csv'), encoding='utf-8-sig', index_col=0)

order = ['없음', 'SMOTE', 'ADASYN', 'FI-SMOTE']
g = rep.groupby('불균형처리')
mean = g[['PR-AUC', 'F1', 'MCC', 'Recall']].mean().loc[order]
std = g[['PR-AUC', 'F1', 'MCC', 'Recall']].std().loc[order]

tv = extra[extra['분석'] == '시간 기반 검증']
seg = extra[extra['분석'] == '업종 분리'].set_index('세부')
sens = extra[extra['분석'] == '민감도']

out = {
    'models': cv['model'].tolist(), 'model_prauc': cv['average_precision'].round(3).tolist(),
    'samplers': order,
    'cv5_f1': mean['F1'].round(3).tolist(), 'cv5_f1_std': std['F1'].round(3).tolist(),
    'cv5_mcc': mean['MCC'].round(3).tolist(), 'cv5_mcc_std': std['MCC'].round(3).tolist(),
    'cv5_prauc': mean['PR-AUC'].round(3).tolist(), 'cv5_prauc_std': std['PR-AUC'].round(3).tolist(),
    'wins': {k: {m: int(v) for m, v in row.items()} for k, row in wins.iterrows()},
    'final': {k: round(float(fin[k]), 3) for k in ['PR-AUC', 'ROC-AUC', 'F1', 'MCC', 'Recall@상위5%', 'Precision', 'Recall']},
    'cap_pcts': cap['상위 %'].tolist(),
    'cap_random': cap['무작위 분할(%)'].round(1).tolist(),
    'cap_time': cap['시간 기반(%)'].round(1).tolist(),
    'time': {c: round(float(tv.iloc[1][c]), 3) for c in ['PR-AUC', 'ROC-AUC', 'F1', 'MCC', 'Recall@상위5%']},
    'seg': {name: {c: round(float(seg.loc[name, c]), 3) for c in ['PR-AUC', 'ROC-AUC', 'F1', 'Recall@상위5%', '탈퇴율(%)']}
            for name in seg.index},
    'wide': {c: round(float(sens.iloc[1][c]), 3) for c in ['PR-AUC', 'ROC-AUC', 'Recall@상위5%', '탈퇴율(%)']},
    'fi_names': fi.index[:6][::-1].tolist(), 'fi_values': fi.values[:6][::-1].round(3).tolist(),
}
json.dump(out, open(os.path.join(ROOT, 'tools', 'deck_numbers.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
