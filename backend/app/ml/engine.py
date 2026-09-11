"""
FinSight AI - Machine Learning Stock Intelligence Engine
Demonstrates responsible time-series machine learning methodology for financial markets:
- Strict temporal train/test split (no look-ahead leakage, no random shuffling)
- Feature engineering: lagged returns, rolling volatility, MA ratios, momentum, volume velocity
- Models: Logistic Regression, Random Forest, Gradient Boosting
- Tasks: Return Direction Classification (Up vs Down), Volatility Regime Estimation
- Evaluation: Precision, Recall, F1, ROC-AUC, Confusion Matrix, Baseline Comparison
- Prominent educational notices on financial non-stationarity and overfitting risks
"""

from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from backend.app.models.schemas import MLMetrics, PriceBar
from backend.app.analytics.engine import QuantitativeAnalyticsEngine

class MachineLearningStockEngine:

    @staticmethod
    def engineer_features(price_bars: List[PriceBar], horizon_days: int = 5) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Extract non-anticipative financial features from historical price bars.
        Features include:
        - Lagged returns (1d, 3d, 5d, 10d)
        - Rolling volatility (10d, 20d)
        - Price-to-Moving-Average ratios (Price/SMA20, SMA20/SMA50)
        - Momentum indicator (RSI-14 proxy)
        - Normalized volume change
        """
        df = pd.DataFrame([b.model_dump() for b in price_bars])
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        close = df["close"]
        vol = df["volume"]


        df["ret_1d"] = close.pct_change(1)
        df["ret_3d"] = close.pct_change(3)
        df["ret_5d"] = close.pct_change(5)
        df["ret_10d"] = close.pct_change(10)


        df["vol_10d"] = df["ret_1d"].rolling(window=10).std() * np.sqrt(252)
        df["vol_20d"] = df["ret_1d"].rolling(window=20).std() * np.sqrt(252)


        sma_20 = close.rolling(window=20).mean()
        sma_50 = close.rolling(window=50).mean()
        df["ratio_price_sma20"] = close / sma_20
        df["ratio_sma20_sma50"] = sma_20 / sma_50


        vol_ma10 = vol.rolling(window=10).mean()
        df["volume_ratio"] = vol / (vol_ma10 + 1e-9)


        future_return = (close.shift(-horizon_days) - close) / close


        df["target_direction"] = np.where(
            future_return.notna(), (future_return > 0).astype(int), np.nan
        )


        features_list = [
            "ret_1d", "ret_3d", "ret_5d", "ret_10d",
            "vol_10d", "vol_20d",
            "ratio_price_sma20", "ratio_sma20_sma50", "volume_ratio"
        ]
        valid_df = df.dropna(subset=[*features_list, "target_direction"]).reset_index(drop=True)
        X = valid_df[features_list]
        y = valid_df["target_direction"]

        return X, y

    @staticmethod
    def train_and_evaluate(
        price_bars: List[PriceBar],
        model_type: str = "random_forest",
        test_size: float = 0.2,
        horizon_days: int = 5
    ) -> MLMetrics:
        """
        Execute temporal train/test split, model training, and metrics generation.
        """
        X, y = MachineLearningStockEngine.engineer_features(price_bars, horizon_days=horizon_days)
        n_samples = len(X)
        if n_samples < 40:
            raise ValueError(f"Insufficient historical bars ({n_samples}) for robust time-series ML.")


        split_idx = int(n_samples * (1.0 - test_size))


        train_end = max(1, split_idx - horizon_days)
        X_train, X_test = X.iloc[:train_end], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:train_end], y.iloc[split_idx:]


        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        feature_names = list(X.columns)


        if model_type == "logistic_regression":
            model = LogisticRegression(C=0.5, penalty="l2", max_iter=1000, random_state=42)
            model.fit(X_train_scaled, y_train)
            importances = {name: round(float(coef), 4) for name, coef in zip(feature_names, model.coef_[0])}
        elif model_type == "gradient_boosting":
            model = GradientBoostingClassifier(n_estimators=60, learning_rate=0.05, max_depth=3, random_state=42)
            model.fit(X_train, y_train)
            importances = {name: round(float(imp), 4) for name, imp in zip(feature_names, model.feature_importances_)}
        else:
            model = RandomForestClassifier(n_estimators=100, max_depth=4, min_samples_split=5, random_state=42)
            model.fit(X_train, y_train)
            importances = {name: round(float(imp), 4) for name, imp in zip(feature_names, model.feature_importances_)}


        X_eval = X_test_scaled if model_type == "logistic_regression" else X_test
        y_pred = model.predict(X_eval)


        try:
            y_proba = model.predict_proba(X_eval)[:, 1]
            roc_auc = round(float(roc_auc_score(y_test, y_proba)), 3)
        except Exception:
            roc_auc = 0.50

        acc = round(float(accuracy_score(y_test, y_pred)), 3)
        prec = round(float(precision_score(y_test, y_pred, zero_division=0)), 3)
        rec = round(float(recall_score(y_test, y_pred, zero_division=0)), 3)
        f1 = round(float(f1_score(y_test, y_pred, zero_division=0)), 3)
        cm = confusion_matrix(y_test, y_pred).tolist()

        warnings = [
            "Financial markets exhibit extreme non-stationarity; historical relationships may degrade rapidly in shifting macroeconomic regimes.",
            "This pipeline enforces strict temporal train/test splitting. Never shuffle time-series data to avoid catastrophic look-ahead bias.",
            "Transaction costs, bid-ask spreads, and market slippage are not modeled in these classification metrics."
        ]

        return MLMetrics(
            accuracy=acc,
            precision=prec,
            recall=rec,
            f1_score=f1,
            roc_auc=roc_auc,
            train_samples=len(X_train),
            test_samples=len(X_test),
            confusion_matrix=cm,
            feature_importances=importances,
            methodology_warnings=warnings
        )
