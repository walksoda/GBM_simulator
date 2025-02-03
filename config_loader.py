import yaml
from typing import Dict, Any
import os

def load_config(file_path: str = "config.yaml") -> Dict[str, Any]:
    """
    YAML設定ファイルを読み込む
    
    パラメータ:
    file_path: 設定ファイルのパス
    
    戻り値:
    設定値の辞書
    
    例外:
    FileNotFoundError: ファイルが存在しない場合
    yaml.YAMLError: YAML形式が不正な場合
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"設定ファイル {file_path} が見つかりません")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    required_keys = ['initial_price', 'expected_return', 'volatility']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"必須パラメータ {key} が設定ファイルに存在しません")
    
    return config