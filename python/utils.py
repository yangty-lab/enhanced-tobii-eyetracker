import os
import glob
import socket
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

# ==========================================
# 0. 路徑錨點 (Path Anchoring) - 關鍵修正
# ==========================================
# 取得 utils.py 目前所在的絕對路徑
_CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 假設資料結構如下：
# Project/
#   ├── data/
#   └── src/
#       └── utils.py
# 所以我們要從 utils.py 往上一層 (Project) 找 data
_DEFAULT_DATA_PATH = os.path.join(os.path.dirname(_CURRENT_SCRIPT_DIR), "data")

# 確保路徑結尾沒有多餘斜線，並正規化分隔符號 (Windows/Mac 通用)
_DEFAULT_DATA_PATH = os.path.normpath(_DEFAULT_DATA_PATH) + os.sep

# ==========================================
# 1. 資料結構與配置 (Data Structures & Config)
# ==========================================

@dataclass(frozen=True)
class NetworkConfig:
    """網路連線配置"""
    host: str = '127.0.0.1'
    port: int = 1234

@dataclass(frozen=True)
class FileConfig:
    """
    檔案路徑配置
    base_dir 預設為我們剛剛算出來的 _DEFAULT_DATA_PATH
    """
    base_dir: str = _DEFAULT_DATA_PATH
    file_pattern: str = "gaze_data_*.txt"
    fallback_file: str = "gaze_data.txt"

# ==========================================
# 2. 純函數：邏輯與轉換
# ==========================================

def get_current_timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def format_file_metadata(file_path: str) -> Dict[str, Any]:
    try:
        stat = os.stat(file_path)
        mod_time = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        return {
            'path': file_path,
            'filename': os.path.basename(file_path),
            'modified': mod_time,
            'timestamp_val': stat.st_mtime,
            'size_kb': round(stat.st_size / 1024, 1)
        }
    except Exception as e:
        return {'path': file_path, 'error': str(e), 'timestamp_val': 0}

def compute_gaze_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty: return {}
    return {
        'count': len(df),
        'duration_start': df['human_time'].iloc[0],
        'duration_end': df['human_time'].iloc[-1],
        'x_stats': {
            'min': df['x_position'].min(),
            'max': df['x_position'].max(),
            'mean': df['x_position'].mean()
        },
        'y_stats': {
            'min': df['y_position'].min(),
            'max': df['y_position'].max(),
            'mean': df['y_position'].mean()
        }
    }

# ==========================================
# 3. I/O 副作用：網路與檔案
# ==========================================

def send_udp_command(config: NetworkConfig, command: str) -> bool:
    ts = get_current_timestamp()
    print(f"[{ts}] Sending command '{command}'...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(command.encode(), (config.host, config.port))
        print(f"[{ts}] Command sent.")
        return True
    except Exception as e:
        print(f"[{ts}] Failed to send: {e}")
        return False

def find_data_files(config: FileConfig) -> List[Dict[str, Any]]:
    """搜尋檔案，如果找不到會印出詳細的路徑資訊以便除錯"""
    
    # 組合路徑
    pattern_path = os.path.join(config.base_dir, config.file_pattern)
    files = glob.glob(pattern_path)
    
    # 除錯訊息：讓你知道程式到底去哪裡找檔案了
    if not files:
        # 嘗試找 Fallback
        fallback_path = os.path.join(config.base_dir, config.fallback_file)
        if os.path.exists(fallback_path):
            files = [fallback_path]
        else:
            # 這是重點：如果還是找不到，印出「絕對路徑」告訴你它在哪裡找
            print(f"\n[⚠️ DEBUG INFO] No files found.")
            print(f"   - Looking in: {config.base_dir}")
            print(f"   - Full Pattern: {pattern_path}")
            print(f"   - Please check if your 'data' folder is actually at that path.\n")
            return []
            
    file_list = [format_file_metadata(f) for f in files]
    file_list.sort(key=lambda x: x['timestamp_val'], reverse=True)
    return file_list

def load_data_frame(file_path: str) -> Optional[pd.DataFrame]:
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    try:
        df = pd.read_csv(file_path, sep='\t')
        if len(df) <= 1:
             print(f"Warning: File {os.path.basename(file_path)} seems empty.")
        return df
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# ==========================================
# 4. 視覺化副作用
# ==========================================

def render_analysis_plot(df: pd.DataFrame, source_filename: str):
    if df.empty:
        print("No data to plot.")
        return

    try:
        # 確保儲存路徑與來源檔案在同一目錄
        save_dir = os.path.dirname(source_filename)
        base_name = os.path.splitext(os.path.basename(source_filename))[0]
        plot_path = os.path.join(save_dir, f"{base_name}_plot.png")

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # 1. Trajectory
        ax1.plot(df['x_position'], df['y_position'], 'b-', alpha=0.6, linewidth=1)
        ax1.scatter(df['x_position'], df['y_position'], c=range(len(df)), cmap='viridis', s=10)
        ax1.set_xlim(0, 1); ax1.set_ylim(0, 1)
        ax1.set_title('Trajectory'); ax1.invert_yaxis()

        # 2. X Time
        ax2.plot(df.index, df['x_position'], 'r-')
        ax2.set_title('X Position Over Time')

        # 3. Y Time
        ax3.plot(df.index, df['y_position'], 'g-')
        ax3.set_title('Y Position Over Time')

        # 4. Heatmap
        x_grid = np.linspace(0, 1, 50); y_grid = np.linspace(0, 1, 50)
        X, Y = np.meshgrid(x_grid, y_grid)
        positions = np.vstack([df['x_position'], df['y_position']])
        kernel = gaussian_kde(positions)
        density = kernel(np.vstack([X.ravel(), Y.ravel()])).reshape(X.shape)
        
        ax4.imshow(density, extent=[0, 1, 1, 0], origin='upper', cmap='hot')
        ax4.set_title('Density Heatmap')
        ax4.set_xticks([]); ax4.set_yticks([])

        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        print(f"Plot saved to: {plot_path}")
        plt.show()
        plt.close(fig)
    except Exception as e:
        print(f"Plot error: {e}")

# ==========================================
# 5. 互動輔助
# ==========================================

def prompt_user_selection(options: List[Dict[str, Any]]) -> Optional[str]:
    if not options:
        print("No files available.")
        return None
    print(f"\n=== AVAILABLE DATA FILES ===")
    for i, info in enumerate(options, 1):
        print(f"{i}. {info['filename']} ({info['size_kb']}KB)")
    
    while True:
        try:
            c = input(f"Select (1-{len(options)}) or 0 for latest: ").strip()
            if c == '0': return options[0]['path']
            idx = int(c) - 1
            if 0 <= idx < len(options): return options[idx]['path']
        except: pass
        return None