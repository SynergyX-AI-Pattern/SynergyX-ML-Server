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

    # --- 그래프 본체 ---
    plt.plot(df["date"], df["actual"],
             label="Actual", color="black",
             linewidth=2.0, solid_capstyle="round")
    plt.plot(df["date"], df["predicted"],
             label="Predicted", color="orange",
             linestyle="--", linewidth=2.0)

    plt.fill_between(df["date"],
                     df["predicted"] * 0.97,
                     df["predicted"] * 1.03,
                     color="orange", alpha=0.12)

    # --- 제목/축/범례 스타일 ---
    plt.title("Stock Price Prediction",
              fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Date", fontsize=12, labelpad=8)
    plt.ylabel("Price", fontsize=12, labelpad=8)
    plt.legend(fontsize=10, frameon=False, loc="upper left")

    # --- 격자선 정리 ---
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tick_params(axis="x", labelrotation=0, labelsize=9)
    plt.tick_params(axis="y", labelsize=9)
    plt.box(False)  # 그래프 테두리 제거

    # --- 성능지표 표시 박스 ---
    text = "\n".join([f"{k}: {v}" for k, v in metrics.items()])
    plt.gcf().text(0.78, 0.35, text,
                   fontsize=10,
                   fontweight="medium",
                   color="#222222",
                   bbox=dict(facecolor="white",
                             edgecolor="#dddddd",
                             alpha=0.8,
                             boxstyle="round,pad=0.4"))

    # --- 고해상도 저장 설정 ---
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(
        buf,
        format="png",
        dpi=350,  # 고해상도
        bbox_inches="tight",
        pad_inches=0.15
    )
    plt.close()
    buf.seek(0)
    return buf


# === 3. 예측 오차 분포 그래프 ===
def plot_error_distribution(df: pd.DataFrame):
    import io
    import numpy as np
    import matplotlib.pyplot as plt

    df["error_pct"] = abs(df["predicted"] - df["actual"]) / df["actual"] * 100

    # 오차 구간별 비율
    bins = [1, 3, 5, 10]
    counts = [(df["error_pct"] <= b).mean() * 100 for b in bins]

    # 색상 팔레트
    colors = ["#0046FF", "#73C8D2", "#9BB4C0", "#FF9013"]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(
        [f"±{b}%" for b in bins],
        counts,
        color=colors,
        width=0.5,  # 막대 폭 조정
        edgecolor="white",  # 막대 사이 경계선
        linewidth=1.5,
        alpha=0.95
    )

    # 막대 위에 수치 표시
    for bar, val in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 1.5,
                 f"{val:.1f}%",
                 ha='center', va='bottom',
                 fontsize=11, fontweight="bold",
                 color="#222222")

    # 제목/레이블
    plt.title("Prediction Error Distribution", fontsize=14, fontweight="bold", pad=10)
    plt.xlabel("Error Range (%)", fontsize=12, labelpad=8)
    plt.ylabel("Data Ratio (%)", fontsize=12, labelpad=8)

    # 격자선 & 축 스타일
    plt.grid(axis='y', linestyle="--", alpha=0.35)
    plt.ylim(0, 100)
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)
    plt.box(False)  # 테두리 제거

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=350)  # 고해상도
    plt.close()
    buf.seek(0)
    return buf
