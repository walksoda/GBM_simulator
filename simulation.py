import numpy as np
from typing import Tuple

def calculate_effective_parameters(
    mu: float,
    sigma: float,
    crash_lambda: float,
    crash_size: float,
    T: float = 1.0,
    num_steps: int = 252
) -> Tuple[float, float]:
    """
    暴落を考慮した実効的なリターンとボラティリティを計算し、補正値を返す
    
    パラメータ:
    mu: 目標期待リターン(年率)
    sigma: 目標ボラティリティ(年率)
    crash_lambda: 暴落の発生頻度(年率)
    crash_size: 暴落の大きさ(%)
    T: 期間(年)
    num_steps: 時間ステップ数
    
    戻り値:
    補正後のmu, 補正後のsigma
    """
    if crash_lambda <= 0 or crash_size <= 0:
        return mu, sigma
    
    # 暴落による期待値の減少を計算
    expected_crashes_per_year = crash_lambda
    expected_total_crash_effect = (1 - crash_size) ** expected_crashes_per_year
    
    # 暴落による追加ボラティリティを計算
    # 暴落によるジャンプの分散を考慮
    crash_variance = crash_lambda * crash_size**2
    
    # リターンの補正
    # ln(1+r) ≈ r の近似を使用
    adjusted_mu = mu - np.log(expected_total_crash_effect)
    
    # ボラティリティの補正
    # 通常のボラティリティと暴落による変動を独立と仮定
    adjusted_sigma = np.sqrt(sigma**2 - crash_variance)
    
    return adjusted_mu, adjusted_sigma

def generate_gbm_path(
    S0: float,
    mu: float,
    sigma: float,
    T: float = 1.0,
    num_steps: int = 252,
    num_paths: int = 1000,
    monthly_investment: float = 0.0,
    bonus_investment: float = 0.0,
    investment_years: float = None,
    crash_lambda: float = 0.0,
    crash_size: float = 0.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    幾何ブラウン運動のパス生成(暴落を含む)
    
    パラメータ:
    S0: 初期価格
    mu: 期待リターン(年率)
    sigma: ボラティリティ(年率)
    T: 期間(年)
    num_steps: 時間ステップ数
    num_paths: シミュレーションパス数
    monthly_investment: 月次積立額
    bonus_investment: ボーナス積立額
    investment_years: 積立期間(年)
    crash_lambda: 暴落の発生頻度(年率)
    crash_size: 暴落の大きさ(%)
    
    戻り値:
    t: 時間軸配列
    paths: 生成されたパスの配列
    """
    # 暴落を考慮したパラメータの補正
    adjusted_mu, adjusted_sigma = calculate_effective_parameters(
        mu, sigma, crash_lambda, crash_size, T, num_steps
    )
    
    dt = T / num_steps
    t = np.linspace(0, T, num_steps + 1)
    
    # ドリフト項と拡散項の計算(補正後のパラメータを使用)
    drift = (adjusted_mu - 0.5 * adjusted_sigma**2) * dt
    diffusion = adjusted_sigma * np.sqrt(dt)
    
    # ランダムな正規分布を生成
    random_numbers = np.random.normal(
        loc=0.0, 
        scale=1.0, 
        size=(num_steps, num_paths)
    )
    
    # 対数リターンを計算
    log_returns = drift + diffusion * random_numbers
    
    # 累積積を計算(初期値含む)
    log_paths = np.vstack([
        np.zeros(num_paths),
        np.cumsum(log_returns, axis=0)
    ])
    
    # 価格パスを計算
    paths = S0 * np.exp(log_paths)
    
    # 暴落の発生をシミュレート
    if crash_lambda > 0 and crash_size > 0:
        # 日次の暴落確率を計算 (年率から日次に変換)
        daily_crash_prob = crash_lambda / 252
        
        # 各時点、各パスで暴落発生を判定
        crash_occurs = np.random.random(size=(num_steps, num_paths)) < daily_crash_prob
        
        # 暴落期間中フラグ(10営業日)を管理する配列
        in_crash_period = np.zeros((num_steps + 1, num_paths), dtype=bool)
        crash_progress = np.zeros((num_steps + 1, num_paths))
        
        # 永続的な暴落の影響を管理する配列
        permanent_crash_effect = np.ones((num_steps + 1, num_paths))
        
        # 各時点での暴落の影響を計算
        for step in range(num_steps):
            # 新規暴落発生のパスを特定
            new_crash_paths = np.where(crash_occurs[step] & ~in_crash_period[step])[0]
            
            if len(new_crash_paths) > 0:
                # 暴落開始時点での価格を保存
                crash_start_prices = paths[step, new_crash_paths]
                
                # 暴落期間のフラグと進行度を設定
                for i in range(10):  # 10営業日
                    if step + i < num_steps + 1:
                        in_crash_period[step + i, new_crash_paths] = True
                        crash_progress[step + i, new_crash_paths] = i / 9  # 0から1まで
                
                # 永続的な暴落の影響を設定
                # 10営業日後以降の全期間に対して影響を適用
                if step + 10 < num_steps + 1:
                    permanent_crash_effect[step+10:, new_crash_paths] *= (1 - crash_size)
        
        # 暴落の影響を価格に反映
        # 暴落進行中の期間は徐々に価格を下げる
        current_crash_effect = crash_progress * crash_size
        paths *= (1 - current_crash_effect)
        
        # 永続的な暴落の影響を反映
        paths *= permanent_crash_effect
    
    # 積立投資の反映
    if monthly_investment > 0 or bonus_investment > 0:
        # 投資期間の設定(指定がない場合は全期間)
        investment_end_step = num_steps + 1
        if investment_years is not None:
            investment_end_step = min(int(investment_years * 252) + 1, num_steps + 1)
        
        # 月次積立の反映
        if monthly_investment > 0:
            # 毎月の積立日を特定(21営業日ごと)
            monthly_indices = np.arange(21, investment_end_step, 21)
            for idx in monthly_indices:
                # 積立時点での価格で購入できる数量を計算
                units = monthly_investment / paths[idx-1, :]
                # その後のリターンを反映
                additional_paths = monthly_investment * (paths[idx:, :] / paths[idx-1, :])
                paths[idx:, :] += additional_paths
        
        # ボーナス積立の反映(6月と12月)
        if bonus_investment > 0:
            # 6月(126営業日)と12月(252営業日)の積立
            bonus_indices = np.arange(126, investment_end_step, 252)
            for idx in bonus_indices:
                # 積立時点での価格で購入できる数量を計算
                units = bonus_investment / paths[idx-1, :]
                # その後のリターンを反映
                additional_paths = bonus_investment * (paths[idx:, :] / paths[idx-1, :])
                paths[idx:, :] += additional_paths
    
    return t, paths
