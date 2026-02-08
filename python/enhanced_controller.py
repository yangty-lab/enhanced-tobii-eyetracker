import time
import os
import utils

# ... (print_menu 與 handle_analysis 維持不變) ...
def print_menu(recording_active: bool):
    ts = utils.get_current_timestamp()
    status = "RECORDING" if recording_active else "IDLE"
    print(f"\n[{ts}] === MAIN MENU (Status: {status}) ===")
    print("1. Start  | 2. Stop  | 3. Burst  | 4. Status")
    print("5. Preview Stats | 6. Plot Graph | 7. List Files | 8. Select File")
    print("9. Command | 0. Quit")

def handle_analysis(file_path: str, show_plot: bool = False):
    print(f"Loading: {os.path.basename(file_path)}...")
    df = utils.load_data_frame(file_path)
    if df is not None:
        stats = utils.compute_gaze_statistics(df)
        print("\n=== STATISTICS ===")
        print(f"Samples: {stats.get('count', 0)}")
        print(f"Duration: {stats.get('duration_start')} -> {stats.get('duration_end')}")
        if show_plot:
            utils.render_analysis_plot(df, file_path)

def main():
    print("=== Enhanced Eye Tracking Controller (Fixed Paths) ===")
    
    net_config = utils.NetworkConfig()
    
    # 重點修改：這裡不需要再指定 base_dir，讓它使用 utils 內部的智慧預設值
    # 如果你的資料夾結構不同，才需要在這裡指定絕對路徑
    file_config = utils.FileConfig() 
    
    recording_active = False
    
    while True:
        try:
            print_menu(recording_active)
            choice = input("Choice: ").strip()
            
            if choice == '1':
                if utils.send_udp_command(net_config, 'c'): recording_active = True
            elif choice == '2':
                if utils.send_udp_command(net_config, 's'): recording_active = False
            elif choice == '3':
                utils.send_udp_command(net_config, '8')
            elif choice == '4':
                utils.send_udp_command(net_config, 'status')
                
            # === Analysis Features ===
            elif choice == '5': # Preview
                files = utils.find_data_files(file_config)
                if files: handle_analysis(files[0]['path'], show_plot=False)
                
            elif choice == '6': # Plot
                files = utils.find_data_files(file_config)
                if files: handle_analysis(files[0]['path'], show_plot=True)
                
            elif choice == '7': # List
                files = utils.find_data_files(file_config)
                if files:
                    for f in files: print(f"• {f['filename']} ({f['size_kb']} KB)")
                    
            elif choice == '8': # Select
                files = utils.find_data_files(file_config)
                if files:
                    sel = utils.prompt_user_selection(files)
                    if sel:
                        ask = input("Plot? (y/n): ").lower() == 'y'
                        handle_analysis(sel, show_plot=ask)
                        
            elif choice == '9':
                utils.send_udp_command(net_config, input("Cmd: "))
            elif choice == '0':
                if recording_active: utils.send_udp_command(net_config, 's')
                utils.send_udp_command(net_config, 'q')
                break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()