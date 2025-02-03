# GBM_simulator (幾何ブラウン運動シミュレーター)

幾何ブラウン運動を用いて長期の資産運用をシミュレーションするPythonアプリケーションです。
月次積立投資やボーナス投資、市場暴落なども考慮したモンテカルロシミュレーションを実行し、将来の資産価値の分布を可視化します。

## 主な機能

- 幾何ブラウン運動による資産価格シミュレーション
- 定期的な積立投資のシミュレーション
- ボーナス時の追加投資シミュレーション
- ランダムな市場暴落のシミュレーション
- 結果のグラフ表示(matplotlib)
- StreamlitによるWebUI

## 必要要件

- Python 3.8以上
- 必要なPythonパッケージ(requirements.txtに記載)
- 日本語フォント(グラフの文字化けを防ぐため)

## セットアップ方法

1. リポジトリをクローン
```bash
git clone https://github.com/walksoda/GBM_simulator.git
cd GBM_simulator
```

2. 仮想環境を作成し、アクティベート
```bash
python -m venv .venv
# Windowsの場合
.venv\Scripts\activate
# macOS/Linuxの場合
source .venv/bin/activate
```

3. 必要なパッケージをインストール
```bash
pip install -r requirements.txt
```

4. 設定ファイルの準備
```bash
cp config_default.yaml config.yaml
```
必要に応じて`config.yaml`の設定値を編集してください。

## 使用方法

### コマンドライン実行
```bash
python main.py
```
シミュレーション結果がresult.pngとして保存されます。

以下の統計情報が出力されます:
- 平均終値:シミュレーション終了時点での平均資産額
- 中央値:シミュレーション終了時点での中央値資産額
- 標準偏差:資産額のばらつきを示す指標
- 最小値/最大値:シミュレーションでの最小/最大資産額
- 元本割れ確率:初期投資額を下回るケースの確率
- 5/95パーセンタイル:下位5%と上位5%の境界値

### Streamlitインターフェース
```bash
streamlit run app.py
```
ブラウザが自動的に開き、インタラクティブなインターフェースが表示されます。

WebUIでは以下の操作が可能です:
- 各種パラメータのスライダーによる調整
- リアルタイムでのシミュレーション結果の更新
- グラフと統計情報の動的な表示
- 設定のプリセット保存と読み込み

## 設定パラメータ

`config.yaml`で以下のパラメータを設定できます:

### 基本パラメータ
- `initial_price`: 初期投資額(円)
- `expected_return`: 期待リターン(年率)
- `volatility`: ボラティリティ(年率)

### シミュレーション設定
- `time_horizon`: シミュレーション期間(年)
- `num_steps`: 時間ステップ数
- `num_paths`: シミュレーションパス数

### 積立設定
- `monthly_investment`: 毎月の積立金額(円)
- `bonus_investment`: ボーナス積立金額(円/回)
- `investment_years`: 積立期間(年)

### 暴落設定
- `crash_lambda`: 暴落の発生頻度(年率)
- `crash_size`: 暴落の大きさ(%)

## 注意事項

1. グラフの日本語表示について
- Windowsの場合:IPAフォントのインストールを推奨
- macOS/Linuxの場合:適切な日本語フォントのインストールが必要

2. シミュレーション結果について
- 過去の実績は将来の運用成果を保証するものではありません
- パラメータは慎重に設定してください
- 暴落確率や規模は市場環境に応じて適宜調整してください

## ライセンス

MITライセンス