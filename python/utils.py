import os
import glob
import socket
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple, Any

# ==========================================
# 1. 資料結構與配置 (Data Structures & Config)
#    Immutable data containers to pass state
# ==========================================

@dataclass(frozen=True)
class NetworkConfig:
    """網路連線配置 (Network Configuration)"""
    host: str = '127.0.0.1'
    port: int = 1234

@dataclass(frozen=True)
class FileConfig:
    """檔案路徑配置 (File Path Configuration)"""
    base_dir: str = "../data/"
    file_pattern: str = "gaze_data_*.txt"
    fallback_file: str = "gaze_data.txt"

# ==========================================
# 2. 純函數：邏輯與轉換 (Pure Functions)
#    No side effects, deterministic output
# ==========================================

def get_current_timestamp() -> str:
    """生成人類可讀的時間戳字串"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def format_file_metadata(file_path: str) -> Dict[str, Any]:
    """
    將檔案屬性轉換為結構化字典
    雖然涉及 os.stat (IO)，但在邏輯層視為資料讀取轉換
    """
    try:
        stat = os.stat(file_path)
        mod_time = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        return {
            'path': file_path,
            'filename': os.path.basename(file_path),
            'modified': mod_time,
            'timestamp_val': stat.st_mtime, # 用於排序
            'size_kb': round(stat.st_size / 1024, 1)
        }
    except Exception as e:
        return {'path': file_path, 'error': str(e), 'timestamp_val': 0}

def compute_gaze_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    計算凝視數據的統計特徵 (Pure Calculation)
    """
    if df.empty:
        return {}
    
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
# 3. I/O 副作用：網路與檔案 (IO / Side Effects)
#    Interactions with the outside world
# ==========================================

def send_udp_command(config: NetworkConfig, command: str) -> bool:
    """
    發送 UDP 指令至 C++ 端
    """
    ts = get_current_timestamp()
    print(f"[{ts}] Sending command '{command}'...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(command.encode(), (config.host, config.port))
        print(f"[{ts}] Command sent successfully.")
        return True
    except Exception as e:
        print(f"[{ts}] Failed to send command: {e}")
        return False

def find_data_files(config: FileConfig) -> List[Dict[str, Any]]:
    """
    搜尋並返回排序後的檔案列表
    """
    # 建立完整路徑
    pattern_path = os.path.join(config.base_dir, config.file_pattern)
    files = glob.glob(pattern_path)
    
    # Fallback 檢查
    if not files:
        old_file = os.path.join(config.base_dir, config.fallback_file)
        if os.path.exists(old_file):
            files = [old_file]
        else:
            return []
            
    # 轉換為 metadata 並排序 (最新在最前)
    file_list = [format_file_metadata(f) for f in files]
    file_list.sort(key=lambda x: x['timestamp_val'], reverse=True)
    
    return file_list

def load_data_frame(file_path: str) -> Optional[pd.DataFrame]:
    """
    安全讀取 CSV/TSV 檔案
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
        
    try:
        # 假設檔案格式為 Tab 分隔
        df = pd.read_csv(file_path, sep='\t')
        if len(df) <= 1: # 檢查是否只有 header 或空
             print(f"File {os.path.basename(file_path)} seems empty or invalid.")
        return df
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

# ==========================================
# 4. 視覺化副作用 (Visualization / Side Effects)
#    Matplotlib logic separated from data loading
# ==========================================

def render_analysis_plot(df: pd.DataFrame, source_filename: str, save_dir: str = "../data/"):
    """
    繪製並儲存分析圖表
    """
    if df.empty:
        print("No data to plot.")
        return

    try:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # 1. Gaze Trajectory
        ax1.plot(df['x_position'], df['y_position'], 'b-', alpha=0.6, linewidth=1)
        ax1.scatter(df['x_position'], df['y_position'], c=range(len(df)), cmap='viridis', s=10, alpha=0.7)
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.set_title('Gaze Trajectory (Color=Time)')
        ax1.grid(True, alpha=0.3)
        ax1.invert_yaxis() # 眼動座標通常 Y 向下為正，若需反轉可調整此處，原程式無反轉但 Heatmap 有

        # 2. X over time
        ax2.plot(df.index, df['x_position'], 'r-', linewidth=1)
        ax2.set_title('X Position Over Time')
        ax2.grid(True, alpha=0.3)

        # 3. Y over time
        ax3.plot(df.index, df['y_position'], 'g-', linewidth=1)
        ax3.set_title('Y Position Over Time')
        ax3.grid(True, alpha=0.3)

        # 4. Density Heatmap
        x_grid = np.linspace(0, 1, 50)
        y_grid = np.linspace(0, 1, 50)
        X, Y = np.meshgrid(x_grid, y_grid)
        
        positions = np.vstack([df['x_position'], df['y_position']])
        kernel = gaussian_kde(positions)
        density = kernel(np.vstack([X.ravel(), Y.ravel()])).reshape(X.shape)
        
        # origin='upper' 對應螢幕座標系 (左上為 0,0)
        im = ax4.imshow(density, extent=[0, 1, 1, 0], origin='upper', cmap='hot')
        ax4.set_title('Gaze Density Heatmap')
        ax4.set_xticks([])
        ax4.set_yticks([])
        plt.colorbar(im, ax=ax4)

        # Save
        base_name = os.path.splitext(os.path.basename(source_filename))[0]
        plot_path = os.path.join(save_dir, f"{base_name}_plot.png")
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved to: {plot_path}")
        
        plt.show()
        plt.close(fig) # 釋放記憶體

    except Exception as e:
        print(f"Error generating plot: {e}")

# ==========================================
# 5. 互動式輔助函數 (Interactive Helpers)
# ==========================================

def prompt_user_selection(options: List[Dict[str, Any]]) -> Optional[str]:
    """
    處理使用者選單邏輯
    Return: Selected file path or None
    """
    if not options:
        print("No files available.")
        return None
        
    print(f"\n=== AVAILABLE DATA FILES ===")
    for i, info in enumerate(options, 1):
        print(f"{i}. {info['filename']} (Modified: {info['modified']}, Size: {info['size_kb']}KB)")
    
    while True:
        try:
            choice = input(f"Select file (1-{len(options)}) or 0 for latest: ").strip()
            if choice == '0':
                return options[0]['path']
            
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]['path']
            print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")
        except KeyboardInterrupt:
            return None