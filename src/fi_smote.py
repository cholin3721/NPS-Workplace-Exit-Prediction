"""
FI-SMOTE v4 (Feature-Importance Weighted Adaptive SMOTE)

출처: 본인(김철중)이 2026-1학기에 작성한 FI-SMOTE v4 연구 코드
      (github.com/cholin3721/Feature-Importance-SMOTE) 의 핵심 함수를 가져와
      이번 프로젝트에 맞게 두 가지만 바꿨다.
  1) sampling_strategy 인자 추가: 소수 클래스를 다수 클래스의 몇 배까지 늘릴지 지정
     (원본은 항상 1:1 완전 균형 → 40만 행 데이터에서는 학습 시간이 너무 길어짐)
  2) 합성 샘플 생성 루프를 벡터화해서 속도 개선 (알고리즘 결과는 동일한 방식)

알고리즘 3단계
  [1] RandomForest 특성 중요도로 중요 피처 선별 (상위 fi_percentile%)
  [2] 중요 피처 공간에서 k-NN 난이도(이웃 중 다수 클래스 비율)를 구해
      경계에 가까운 소수 샘플일수록 더 많이 합성 (ADASYN 방식)
  [3] 중요 피처는 λ ~ Beta(1, 1 + scale * w_k) 로 원본 근처에 고정,
      비중요 피처는 λ ~ Uniform(0, 1) 로 자유롭게 보간
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import NearestNeighbors


def fi_smote_resample(X_train, y_train, sampling_strategy=0.1, fi_percentile=50,
                      k_neighbors=5, fi_weight_scale=20.0, random_state=42):
    rng = np.random.RandomState(random_state)
    X_train = X_train.reset_index(drop=True)
    y_train = pd.Series(y_train).reset_index(drop=True)

    # ── [1] 특성 중요도 ───────────────────────────────────────────
    fi_model = RandomForestClassifier(n_estimators=100, random_state=random_state,
                                      n_jobs=-1)
    fi_model.fit(X_train, y_train)
    importances = fi_model.feature_importances_
    importances_norm = importances / importances.sum()
    fi_mask = importances >= np.percentile(importances, fi_percentile)
    feature_names = X_train.columns.tolist()
    important = [f for f, m in zip(feature_names, fi_mask) if m]

    X_min = X_train[y_train == 1].reset_index(drop=True)
    X_maj = X_train[y_train == 0].reset_index(drop=True)
    n_min, n_maj = len(X_min), len(X_maj)
    n_to_generate = int(n_maj * sampling_strategy) - n_min
    if n_to_generate <= 0 or n_min < 2:
        return X_train, y_train

    # 거리 계산은 중요 피처를 표준화한 공간에서 수행
    Z = X_train[important]
    Z = (Z - Z.mean()) / Z.std().replace(0, 1)
    Z_min = Z[y_train == 1].reset_index(drop=True)

    # ── [2] 난이도(경계 근접도) → 샘플별 생성 개수 ─────────────────
    nn_all = NearestNeighbors(n_neighbors=k_neighbors + 1, n_jobs=-1).fit(Z)
    _, idx = nn_all.kneighbors(Z_min)
    idx = idx[:, 1:]
    difficulty = (y_train.values[idx] == 0).mean(axis=1)
    if difficulty.sum() == 0:
        weights = np.ones(n_min) / n_min
    else:
        weights = difficulty / difficulty.sum()
    n_per = np.floor(weights * n_to_generate).astype(int)
    rest = n_to_generate - n_per.sum()
    n_per[np.argsort(weights)[::-1][:rest]] += 1

    # ── [3] 소수 클래스 내부 k-NN 과 피처별 λ 보간 ─────────────────
    k_min = min(k_neighbors + 1, n_min)
    nn_min = NearestNeighbors(n_neighbors=k_min, n_jobs=-1).fit(Z_min)
    _, idx_min = nn_min.kneighbors(Z_min)
    idx_min = idx_min[:, 1:]

    base_idx = np.repeat(np.arange(n_min), n_per)
    partner = idx_min[base_idx, rng.randint(0, idx_min.shape[1], size=len(base_idx))]
    Xa = X_min.values.astype(float)
    x_i, x_j = Xa[base_idx], Xa[partner]

    n_feat = len(feature_names)
    b_params = 1.0 + fi_weight_scale * importances_norm
    lam_imp = rng.beta(np.ones(n_feat), b_params, size=(len(base_idx), n_feat))
    lam_free = rng.uniform(0, 1, size=(len(base_idx), n_feat))
    lam = np.where(fi_mask, lam_imp, lam_free)
    synthetic = x_i + lam * (x_j - x_i)

    syn_df = pd.DataFrame(synthetic, columns=feature_names)
    X_res = pd.concat([X_train, syn_df], ignore_index=True)
    y_res = pd.concat([y_train, pd.Series(np.ones(len(syn_df), dtype=int))],
                      ignore_index=True)
    return X_res, y_res
