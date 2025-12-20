# FinSight AI: Responsible Machine Learning Methodology

## 1. Problem Formulation & Academic Foundations

FinSight AI models next-period equity directional movements as a supervised binary classification problem:

$$y_t = \begin{cases} 1 & \text{if } P_{t+1} > P_t \\ 0 & \text{if } P_{t+1} \le P_t \end{cases}$$

Where $P_t$ represents the asset close price on trading day $t$.

### 1.1 The Realistic Financial ML Paradigm
In institutional quantitative finance, **the Efficient Market Hypothesis (EMH)** and high signal-to-noise ratios dictate that realistic out-of-sample directional classification accuracy for liquid equities (e.g., S&P 500 components) typically ranges between **51.5% and 57.0%**. 

> [!WARNING]
> Any platform claiming 85%+ or 95%+ directional equity prediction accuracy is almost certainly exhibiting **catastrophic look-ahead bias, random shuffle contamination, or target leakage**. FinSight AI enforces strict mathematical integrity to reflect real-world algorithmic research.

---

## 2. Prevention of Look-Ahead Bias & Data Leakage

Look-ahead bias is the cardinal sin of financial time series modeling. FinSight AI enforces five mathematical safeguards in `backend/app/ml/engine.py`:

```
Chronological Time Horizon (t = 1 to T)
[================ TRAIN PARTITION (70%) ===============] [===== TEST PARTITION (30%) =====]
t=1                                                  t=k t=k+1                           t=T
               Fit Scalers & Models --->                   Evaluate Out-of-Sample Only
```

1. **Strict Temporal Split (`shuffle=False`)**: Random train/test shuffling is forbidden. The dataset is partitioned chronologically (70% training, 30% out-of-sample evaluation).
2. **Point-in-Time Feature Engineering**: Features at time $t$ use only data available at or prior to time $t$. No future indicators (e.g., centered moving averages or future price peaks) are utilized.
3. **Isolated Preprocessing & Scaling**: Feature scalers (e.g., `StandardScaler`, `MinMaxScaler`) are fit solely on the training partition $[1, k]$ and then transformed over the test partition $[k+1, T]$. Fitting parameters over the full dataset would leak distribution parameters from the future.
4. **Non-Overlapping Return Windows**: Label returns are evaluated strictly on subsequent single-day steps to eliminate autocorrelation induced by overlapping rolling returns.
5. **Lagged Input Vectors**: All momentum, volume, and volatility signals are explicitly lagged by at least 1 day ($t-1$) relative to the prediction window.

---

## 3. Feature Engineering Pipeline

The system constructs 9 orthogonal quantitative features from raw OHLCV series:

| Feature Name | Formulation | Economic Rationale |
| :--- | :--- | :--- |
| `ret_lag_1` | $\ln(P_{t-1} / P_{t-2})$ | Short-term mean-reversion or momentum impulse |
| `ret_lag_2` | $\ln(P_{t-2} / P_{t-3})$ | Two-day autocorrelation persistence |
| `ret_lag_5` | $\ln(P_{t-1} / P_{t-6})$ | Weekly cumulative trend strength |
| `volatility_5d` | $\text{std}(r_{t-5:t-1}) \times \sqrt{252}$ | Short-term realized volatility clustering |
| `volatility_20d` | $\text{std}(r_{t-20:t-1}) \times \sqrt{252}$ | Medium-term volatility regime detection |
| `sma_ratio_20` | $P_{t-1} / \text{SMA}_{20}(P_{t-1})$ | Price deviation from 20-day mean (Bollinger basis) |
| `sma_ratio_50` | $P_{t-1} / \text{SMA}_{50}(P_{t-1})$ | Intermediate trend deviation |
| `volume_ratio_20`| $V_{t-1} / \text{SMA}_{20}(V_{t-1})$ | Volume surge indicator (institutional liquidity entry) |
| `rsi_14` | $100 - \frac{100}{1 + \text{RS}_{14}(t-1)}$ | 14-day technical overbought/oversold oscillator |

---

## 4. Model Architectures & Evaluation

### 4.1 Algorithms Implemented
1. **Regularized Logistic Regression**: Serves as the transparent linear baseline with L2 penalty, providing interpretable log-odds coefficients.
2. **Random Forest Classifier**: Ensemble of 100 decorrelated decision trees with constrained depth (`max_depth=5`) to prevent overfitting to noisy market regimes.
3. **Gradient Boosting Classifier**: Sequentially minimized pseudo-residuals (`learning_rate=0.05`, `n_estimators=100`) capturing non-linear feature interactions.

### 4.2 Comprehensive Metrics & Diagnostics
The platform reports a multi-dimensional metric suite for every training run:

```json
{
  "model_type": "RandomForest",
  "accuracy": 0.547,
  "precision": 0.562,
  "recall": 0.518,
  "f1_score": 0.539,
  "roc_auc": 0.561,
  "confusion_matrix": {
    "true_negative": 22,
    "false_positive": 14,
    "false_negative": 17,
    "true_positive": 23
  },
  "feature_importances": {
    "volatility_20d": 0.182,
    "rsi_14": 0.165,
    "sma_ratio_20": 0.141,
    "volume_ratio_20": 0.129,
    "ret_lag_1": 0.115
  }
}
```

### 4.3 Feature Importance Interpretation
The ML Lab workspace visually renders feature importances and tree splits, enabling analysts to verify that the model is making decisions aligned with quantitative economic logic rather than fitting spurious noise.
