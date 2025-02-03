import argparse
import matplotlib.pyplot as plt
from simulation import generate_gbm_path
from config_loader import load_config
import numpy as np

def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(
        description='幾何ブラウン運動シミュレーション'
    )
    parser.add_argument(
        '-c', '--config',
        type=str,
        default='config.yaml',
        help='設定ファイルのパス'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='result.png',
        help='出力画像ファイル名'
    )
    args = parser.parse_args()

    try:
        # 設定ファイルの読み込み
        config = load_config(args.config)
        
        # シミュレーション実行
        t, paths = generate_gbm_path(
            S0=config['initial_price'],
            mu=config['expected_return'],
            sigma=config['volatility'],
            T=config.get('time_horizon', 1.0),
            num_steps=config.get('num_steps', 252),
            num_paths=config.get('num_paths', 1000),
            monthly_investment=config.get('monthly_investment', 0.0),
            bonus_investment=config.get('bonus_investment', 0.0),
            investment_years=config.get('investment_years', None),
            crash_lambda=config.get('crash_lambda', 0.0),
            crash_size=config.get('crash_size', 0.0)
        )

        # 可視化
        plt.figure(figsize=(12, 6))
        plt.plot(t, paths[:, :100], alpha=0.5, linewidth=1)
        
        # 統計量の計算
        final_prices = paths[-1, :]
        mean_price = np.mean(final_prices)
        std_dev = np.std(final_prices)
        min_price = np.min(final_prices)
        max_price = np.max(final_prices)
        median_price = np.median(final_prices)
        
        # パーセンタイルの計算
        percentile_5 = np.percentile(final_prices, 5)
        percentile_95 = np.percentile(final_prices, 95)
        
        # 元本割れ確率の計算
        initial_investment = config['initial_price']
        below_principal = np.sum(final_prices < initial_investment) / len(final_prices) * 100
        
        plt.title(
            f"幾何ブラウン運動シミュレーション (暴落あり)\n"
            f"平均: ¥{mean_price:,.0f}  中央値: ¥{median_price:,.0f}\n"
            f"標準偏差: ¥{std_dev:,.0f}  元本割れ確率: {below_principal:.1f}%\n"
            f"5-95パーセンタイル: ¥{percentile_5:,.0f} - ¥{percentile_95:,.0f}"
        )
        plt.xlabel('経過年数')
        plt.ylabel('資産額 (円)')
        plt.grid(True)
        plt.savefig(args.output)
        plt.close()
        
        print(f"シミュレーション結果を {args.output} に保存しました")
        print(f"\n統計情報:")
        print(f"平均終値: ¥{mean_price:,.0f}")
        print(f"中央値: ¥{median_price:,.0f}")
        print(f"標準偏差: ¥{std_dev:,.0f}")
        print(f"最小値: ¥{min_price:,.0f}")
        print(f"最大値: ¥{max_price:,.0f}")
        print(f"元本割れ確率: {below_principal:.1f}%")
        print(f"5パーセンタイル: ¥{percentile_5:,.0f}")
        print(f"95パーセンタイル: ¥{percentile_95:,.0f}")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()