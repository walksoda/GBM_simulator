import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config_loader import load_config
from simulation import generate_gbm_path

# 設定の読み込み
config = load_config('config.yaml')

# Streamlit UI設定
st.set_page_config(page_title="GBMシミュレーター", layout="wide")
st.title("幾何ブラウン運動シミュレーション")

# プロットのスタイル設定
plt.style.use('default')
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.family'] = 'MS Gothic'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.formatter.useoffset'] = False

# サイドバーでパラメータ設定
with st.sidebar:
    st.header("シミュレーションパラメータ")
    
    # 基本パラメータ
    st.subheader("基本パラメータ")
    initial_price = st.number_input("初期価格 (円)", value=config['initial_price'])
    expected_return = st.number_input("期待リターン(年率)", 0.0, 0.5, config['expected_return'], step=0.001, format="%.3f")
    volatility = st.number_input("ボラティリティ(年率)", 0.0, 1.0, config['volatility'], step=0.001, format="%.3f")
    time_horizon = st.slider("期間(年)", 1, 20, config['time_horizon'])
    num_paths = st.number_input("シミュレーションパス数", 100, 10000, 1000, step=100,
                                help="直接数値を入力してください(100〜10,000)", format="%d")
    
    # 積立設定
    st.subheader("積立設定")
    monthly_investment = st.number_input("毎月の積立金額 (円)", 0, 1000000, config['monthly_investment'], step=1000)
    bonus_investment = st.number_input("ボーナス積立金額 (円/回)", 0, 10000000, config['bonus_investment'], step=10000,
                                    help="6月と12月の年2回積立")
    investment_years = st.slider("積立期間(年)", 0, time_horizon, config['investment_years'],
                               help="0の場合は積立なし")
    
    # 暴落設定
    st.subheader("暴落設定")
    enable_crash = st.checkbox("暴落シミュレーションを有効にする", value=True)
    crash_lambda = st.number_input(
        "暴落頻度(年率)",
        0.0, 1.0, config.get('crash_lambda', 0.1), step=0.01,
        help="0.1は10年に1回の頻度",
        format="%.2f",
        disabled=not enable_crash
    )
    crash_size = st.number_input(
        "暴落の大きさ",
        0.0, 1.0, config.get('crash_size', 0.3), step=0.01,
        help="0.3は30%の暴落",
        format="%.2f",
        disabled=not enable_crash
    )

# シミュレーション実行ボタン
if st.button("シミュレーション実行"):
    with st.spinner("シミュレーション実行中..."):
        # シミュレーション実行
        t, paths = generate_gbm_path(
            initial_price,
            expected_return,
            volatility,
            time_horizon,
            config['num_steps'],
            num_paths,
            monthly_investment,
            bonus_investment,
            investment_years if investment_years > 0 else None,
            crash_lambda if enable_crash else 0.0,
            crash_size if enable_crash else 0.0
        )
        
        # データの間引き(表示用)
        steps_per_year = config['num_steps'] // time_horizon
        display_steps = np.arange(0, len(t), max(1, steps_per_year // 12))  # 月次程度に間引き
        t_display = t[display_steps]
        paths_display = paths[display_steps, :]
        
        # グラフ描画
        plt.close('all')
        fig, ax = plt.subplots()
        
        # 元金の推移を計算
        principal = np.zeros_like(t)
        principal[0] = initial_price
        if monthly_investment > 0 or bonus_investment > 0:
            investment_end_step = len(t)
            if investment_years is not None and investment_years > 0:
                investment_end_step = min(int(investment_years * 252) + 1, len(t))
            
            # 月次積立の反映
            monthly_indices = np.arange(21, investment_end_step, 21)
            principal[monthly_indices] += monthly_investment
            
            # ボーナス積立の反映(6月と12月)
            bonus_indices = np.arange(126, investment_end_step, 252)
            principal[bonus_indices] += bonus_investment
        
        principal = np.cumsum(principal)
        principal_display = principal[display_steps]
        
        # 表示するパス数を制限
        num_display_paths = min(100, paths.shape[1])
        displayed_paths = np.random.choice(paths.shape[1], num_display_paths, replace=False)
        
        # 信頼区間の計算(90%と95%)
        percentiles_90 = np.percentile(paths_display, [5, 95], axis=1)
        percentiles_95 = np.percentile(paths_display, [2.5, 97.5], axis=1)

        # 95%信頼区間(薄い色で表示)
        ax.fill_between(t_display,
                       percentiles_95[0],
                       percentiles_95[1],
                       color='lightblue',
                       alpha=0.3,
                       label='95%信頼区間')

        # 90%信頼区間(濃い色で表示)
        ax.fill_between(t_display,
                       percentiles_90[0],
                       percentiles_90[1],
                       color='blue',
                       alpha=0.3,
                       label='90%信頼区間')

        # 中央値の線
        median_line = np.median(paths_display, axis=1)
        ax.plot(t_display, median_line,
               'r--',
               lw=2,
               label='中央値')

        # 個別のパスは薄く表示
        for i in displayed_paths:
            ax.plot(t_display, paths_display[:, i],
                    lw=0.8,
                    alpha=0.4,
                    color='gray')

        # 元金を最前面に表示
        ax.plot(t_display, principal_display,
               'k-',
               lw=2,
               label='元金')
        
        ax.legend()
        title = "幾何ブラウン運動シミュレーション"
        if enable_crash:
            title += f"\n(年率{crash_lambda:.2f}の頻度で10営業日かけて{crash_size*100:.0f}%暴落)"
        ax.set_title(title)
        ax.set_xlabel("時間 (年)")
        ax.set_ylabel("価格 (円)")
        
        # 横軸を整数年のみ表示
        ax.set_xticks(np.arange(0, time_horizon + 1))
        ax.grid(True)
        
        # グラフの余白を調整
        plt.tight_layout()
        
        # 結果表示
        st.pyplot(fig)
        
        # 統計情報表示(5年刻み)
        st.subheader("5年刻み統計情報")
        
        # 5年刻みでデータ抽出(時系列順に)
        year_steps = np.array(sorted(np.arange(0, time_horizon + 1, 5)))
        year_indices = (year_steps * 252).astype(int)
        year_indices = np.clip(year_indices, 0, paths.shape[0]-1)
        
        # 統計データ計算
        stats_data = []
        for idx, year in zip(year_indices, year_steps):
            prices = paths[idx, :]
            principal_value = principal[idx]
            below_principal = np.sum(prices < principal_value) / len(prices) * 100
            stats = {
                "経過年数": f"{year}年",
                "元金": f"{principal_value:,.0f}円",
                "平均": f"{np.mean(prices):,.0f}円",
                "最小値": f"{np.min(prices):,.0f}円",
                "25%タイル": f"{np.percentile(prices, 25):,.0f}円",
                "中央値": f"{np.median(prices):,.0f}円",
                "75%タイル": f"{np.percentile(prices, 75):,.0f}円",
                "最大値": f"{np.max(prices):,.0f}円",
                "元本割れ確率": f"{below_principal:.1f}%"
            }
            stats_data.append(stats)
        
        # テーブル表示用CSS
        st.markdown("""
            <style>
            .stDataFrame {font-size: 0.8em;}
            .stDataFrame td, .stDataFrame th {
                padding: 0.3rem 0.5rem !important;
                white-space: nowrap !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # テーブル表示
        st.dataframe(pd.DataFrame(stats_data), hide_index=True)