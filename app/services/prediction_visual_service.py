import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # macOS GUI 비활성화
import matplotlib.pyplot as plt


# === 1. 성능지표 계산 ===
def calc_metrics(df: pd.DataFrame):
    df["error"] = df["predicted"] - df["actual"]
    df["error_pct"] = abs(df["error"] / df["actual"]) * 100

    rmse = np.sqrt(np.mean(df["error"] ** 2))
    mape = np.mean(df["error_pct"])
    nrmse = rmse / df["actual"].mean() * 100
    acc_3 = np.mean(df["error_pct"] <= 3) * 100
    acc_5 = np.mean(df["error_pct"] <= 5) * 100

    return {
        "RMSE": round(rmse, 2),
        "MAPE": round(mape, 2),
        "NRMSE": round(nrmse, 2),
        "Acc ±3%": round(acc_3, 2),
        "Acc ±5%": round(acc_5, 2)
    }


# === 2. 예측 vs 실제 그래프 ===
def plot_prediction_graph(df: pd.DataFrame):
    metrics = calc_metrics(df)

    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["actual"], label="Actual", color="black", linewidth=1.6)
    plt.plot(df["date"], df["predicted"], label="Predicted", color="orange", linestyle="--", linewidth=1.4)
    plt.fill_between(df["date"],
                     df["predicted"] * 0.97,
                     df["predicted"] * 1.03,
                     color="orange", alpha=0.1)

    plt.title("Stock Price Prediction")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()

    # 오른쪽 하단에 성능지표 표시
    text = "\n".join([f"{k}: {v}" for k, v in metrics.items()])
    plt.gcf().text(0.8, 0.3, text,
                   fontsize=9,
                   bbox=dict(facecolor='white', alpha=0.5))

    # 버퍼에 저장 후 리턴
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf

