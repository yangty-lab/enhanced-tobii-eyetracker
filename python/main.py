import time
import os
import sys
import utils  # 匯入剛剛整理好的 utils.py

def print_menu(recording_active: bool):
    """顯示主選單"""
    ts = utils.get_current_timestamp()
    status = "RECORDING" if recording_active else "IDLE"
    
    print(f"\n[{ts}] === MAIN MENU (Status: {status}) ===")
    print("RECORDING MODES:")
    print("1. Start continuous recording")
    print("2. Stop continuous recording") 
    print("3. Single burst recording (10 callbacks)")
    print("4. Check recording status")
    print("")
    print("DATA ANALYSIS:")
    print("5. Preview latest data (Stats only)")
    print("6. Plot latest data (Graph)")
    print("7. List all data files")
    print("8. Select specific file to analyze/plot")
    print("")
    print("SYSTEM:")
    print("9. Send custom command")
    print("0. Quit")

def handle_analysis(file_path: str, show_plot: bool = False):
    """處理單一檔案的分析流程"""
    print(f"Loading: {os.path.basename(file_path)}...")
    df = utils.load_data_frame(file_path)
    
    if df is not None:
        # 1. 計算並顯示統計數據 (Pure Logic)
        stats = utils.compute_gaze_statistics(df)
        print("\n=== STATISTICS ===")
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_k, sub_v in value.items():
                    print(f"  - {sub_k}: {sub_v:.4f}")
            else:
                print(f"{key}: {value}")
        
        # 2. 繪圖 (Side Effect)
        if show_plot:
            print("\nGenerating plot...")
            utils.render_analysis_plot(df, file_path)

def main():
    print("=== Enhanced Eye Tracking Controller (Functional ver.) ===")
    
    # 1. 初始化配置 (Immutable Configs)
    net_config = utils.NetworkConfig(host='127.0.0.1', port=1234)
    file_config = utils.FileConfig(base_dir="../data/")
    
    # 2. 本地狀態管理
    recording_active = False
    
    while True:
        try:
            print_menu(recording_active)
            choice = input("Enter choice (0-9): ").strip()
            
            # === RECORDING COMMANDS ===
            if choice == '1':
                if utils.send_udp_command(net_config, 'c'):
                    recording_active = True
                    print(">> Continuous recording STARTED.")
                
            elif choice == '2':
                if utils.send_udp_command(net_config, 's'):
                    recording_active = False
                    print(">> Continuous recording STOPPED.")
                
            elif choice == '3':
                print(">> Preparing burst recording in 2 seconds...")
                time.sleep(2)
                utils.send_udp_command(net_config, '8')
                print(">> Burst command sent. Waiting 3 seconds...")
                time.sleep(3)
                print(">> Done.")
                
            elif choice == '4':
                utils.send_udp_command(net_config, 'status')
                print(f">> Local State Tracker: {recording_active}")
                
            # === DATA ANALYSIS ===
            elif choice == '5':
                # Preview Latest
                files = utils.find_data_files(file_config)
                if files:
                    handle_analysis(files[0]['path'], show_plot=False)
                else:
                    print(">> No data files found.")
                
            elif choice == '6':
                # Plot Latest
                files = utils.find_data_files(file_config)
                if files:
                    handle_analysis(files[0]['path'], show_plot=True)
                else:
                    print(">> No data files found.")
                
            elif choice == '7':
                # List All
                files = utils.find_data_files(file_config)
                if files:
                    print("\n=== ALL DATA FILES ===")
                    for f in files:
                        print(f"• {f['filename']} ({f['size_kb']} KB) - {f['modified']}")
                else:
                    print(">> No files found.")
                
            elif choice == '8':
                # Interactive Selection
                files = utils.find_data_files(file_config)
                if files:
                    selected_path = utils.prompt_user_selection(files)
                    if selected_path:
                        # 詢問是否要畫圖
                        plot_ask = input("Generate plot? (y/n): ").strip().lower()
                        handle_analysis(selected_path, show_plot=(plot_ask == 'y'))
                else:
                    print(">> No files to select.")
            
            # === SYSTEM ===
            elif choice == '9':
                cmd = input("Custom command: ").strip()
                if cmd:
                    utils.send_udp_command(net_config, cmd)
                
            elif choice == '0':
                print(">> Shutting down...")
                if recording_active:
                    utils.send_udp_command(net_config, 's')
                utils.send_udp_command(net_config, 'q')
                break
                
            else:
                print("!! Invalid choice.")
                
        except KeyboardInterrupt:
            print("\n>> Interrupted. Stopping recording and quitting...")
            utils.send_udp_command(net_config, 's')
            utils.send_udp_command(net_config, 'q')
            break
        except Exception as e:
            print(f"!! Unexpected Error: {e}")

if __name__ == "__main__":
    main()