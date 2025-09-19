import socket
import time
import datetime
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

class EnhancedEyeTrackingController:
    def __init__(self, host='127.0.0.1', port=1234):
        self.host = host
        self.port = port
        self.recording_active = False
        self.data_directory = "../data/"
    
    def get_timestamp(self):
        """Get current time in human readable format with milliseconds"""
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    def find_latest_data_file(self):
        """Find the most recent gaze data file"""
        # Look for files matching the pattern gaze_data_*.txt
        pattern = os.path.join(self.data_directory, "gaze_data_*.txt")
        data_files = glob.glob(pattern)
        
        if not data_files:
            # Fallback to old filename format
            old_file = os.path.join(self.data_directory, "gaze_data.txt")
            if os.path.exists(old_file):
                return old_file
            return None
        
        # Return the most recently modified file
        latest_file = max(data_files, key=os.path.getmtime)
        return latest_file
    
    def list_all_data_files(self):
        """List all available data files with timestamps"""
        pattern = os.path.join(self.data_directory, "gaze_data_*.txt")
        data_files = glob.glob(pattern)
        
        if not data_files:
            old_file = os.path.join(self.data_directory, "gaze_data.txt")
            if os.path.exists(old_file):
                data_files = [old_file]
            else:
                return []
        
        # Sort by modification time (newest first)
        data_files.sort(key=os.path.getmtime, reverse=True)
        
        file_info = []
        for file_path in data_files:
            mod_time = os.path.getmtime(file_path)
            mod_time_str = datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
            file_size = os.path.getsize(file_path)
            
            # Count lines in file
            try:
                with open(file_path, 'r') as f:
                    line_count = sum(1 for _ in f) - 1  # Subtract header
            except:
                line_count = 0
            
            file_info.append({
                'path': file_path,
                'filename': os.path.basename(file_path),
                'modified': mod_time_str,
                'size_kb': round(file_size / 1024, 1),
                'samples': line_count
            })
        
        return file_info
    
    def select_data_file_interactive(self):
        """Let user select which data file to analyze"""
        files = self.list_all_data_files()
        
        if not files:
            print("No data files found!")
            return None
        
        print(f"\n=== AVAILABLE DATA FILES ===")
        for i, file_info in enumerate(files, 1):
            print(f"{i}. {file_info['filename']}")
            print(f"   Modified: {file_info['modified']}")
            print(f"   Size: {file_info['size_kb']} KB, Samples: {file_info['samples']}")
            print()
        
        while True:
            try:
                choice = input(f"Select file (1-{len(files)}) or 0 for latest: ").strip()
                if choice == '0':
                    return files[0]['path']  # Most recent
                
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    return files[idx]['path']
                else:
                    print(f"Invalid choice. Please enter 1-{len(files)} or 0.")
                    
            except ValueError:
                print("Please enter a number.")
            except KeyboardInterrupt:
                return None
    
    def send_command(self, command):
        """Send UDP command to Tobii C++ program"""
        print(f"[{self.get_timestamp()}] Sending command '{command}' to C++ program")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(command.encode(), (self.host, self.port))
            sock.close()
            print(f"[{self.get_timestamp()}] Command '{command}' sent successfully")
            return True
        except Exception as e:
            print(f"[{self.get_timestamp()}] Failed to send command: {e}")
            return False
    
    def check_data_file_exists(self, file_path=None):
        """Check if data file exists and show basic info"""
        if file_path is None:
            file_path = self.find_latest_data_file()
            
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:  # More than just header
                        print(f"Data file: {os.path.basename(file_path)}")
                        print(f"Contains {len(lines)-1} data points")
                        return True, file_path
                    else:
                        print(f"Data file exists but is empty: {os.path.basename(file_path)}")
                        return False, file_path
            except Exception as e:
                print(f"Error reading data file: {e}")
                return False, file_path
        else:
            print("No data file found")
            return False, None
    
    def show_data_preview(self, file_path=None):
        """Show preview of collected data"""
        if file_path is None:
            file_path = self.find_latest_data_file()
            
        exists, file_path = self.check_data_file_exists(file_path)
        if not exists:
            return
        
        try:
            # Read the data
            df = pd.read_csv(file_path, sep='\t')
            
            print(f"\n=== DATA PREVIEW ===")
            print(f"File: {os.path.basename(file_path)}")
            print(f"Total samples: {len(df)}")
            print(f"Time range: {df['human_time'].iloc[0]} to {df['human_time'].iloc[-1]}")
            print(f"X range: {df['x_position'].min():.3f} to {df['x_position'].max():.3f}")
            print(f"Y range: {df['y_position'].min():.3f} to {df['y_position'].max():.3f}")
            
            print(f"\nFirst 5 samples:")
            print(df.head())
            
            print(f"\nLast 5 samples:")
            print(df.tail())
            
        except Exception as e:
            print(f"Error analyzing data: {e}")
    
    def plot_gaze_data(self, file_path=None):
        """Create a simple plot of gaze data"""
        if file_path is None:
            file_path = self.find_latest_data_file()
            
        exists, file_path = self.check_data_file_exists(file_path)
        if not exists:
            return
        
        try:
            df = pd.read_csv(file_path, sep='\t')
            
            if len(df) == 0:
                print("No data to plot")
                return
            
            # Create plots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
            
            # Gaze trajectory
            ax1.plot(df['x_position'], df['y_position'], 'b-', alpha=0.6, linewidth=1)
            ax1.scatter(df['x_position'], df['y_position'], c=range(len(df)), 
                       cmap='viridis', s=10, alpha=0.7)
            ax1.set_xlim(0, 1)
            ax1.set_ylim(0, 1)
            ax1.set_xlabel('X Position')
            ax1.set_ylabel('Y Position')
            ax1.set_title('Gaze Trajectory (color = time)')
            ax1.grid(True, alpha=0.3)
            
            # X position over time
            ax2.plot(df.index, df['x_position'], 'r-', linewidth=1)
            ax2.set_xlabel('Sample Number')
            ax2.set_ylabel('X Position')
            ax2.set_title('X Position Over Time')
            ax2.grid(True, alpha=0.3)
            
            # Y position over time
            ax3.plot(df.index, df['y_position'], 'g-', linewidth=1)
            ax3.set_xlabel('Sample Number')
            ax3.set_ylabel('Y Position')
            ax3.set_title('Y Position Over Time')
            ax3.grid(True, alpha=0.3)
            
            # Heatmap of gaze positions
            from scipy.stats import gaussian_kde
            import numpy as np
            
            # Create grid for heatmap
            x_grid = np.linspace(0, 1, 50)
            y_grid = np.linspace(0, 1, 50)
            X, Y = np.meshgrid(x_grid, y_grid)
            
            # Calculate density
            positions = np.vstack([df['x_position'], df['y_position']])
            kernel = gaussian_kde(positions)
            density = kernel(np.vstack([X.ravel(), Y.ravel()])).reshape(X.shape)
            
            # CORRECTED: Use origin='upper' to match screen coordinates
            im = ax4.imshow(density, extent=[0, 1, 1, 0], origin='upper', cmap='hot')
            
            # Remove confusing axis labels and ticks
            ax4.set_xticks([])
            ax4.set_yticks([])
            ax4.set_title('Gaze Density Heatmap (Screen View)')
            
            # Add corner labels in correct positions
            ax4.text(0.02, 0.02, '(0,1)\nBottom-Left', transform=ax4.transAxes, 
                    fontsize=8, color='white', va='bottom')
            ax4.text(0.98, 0.02, '(1,1)\nBottom-Right', transform=ax4.transAxes, 
                    fontsize=8, color='white', va='bottom', ha='right')
            ax4.text(0.02, 0.98, '(0,0)\nTop-Left', transform=ax4.transAxes, 
                    fontsize=8, color='white', va='top')
            ax4.text(0.98, 0.98, '(1,0)\nTop-Right', transform=ax4.transAxes, 
                    fontsize=8, color='white', va='top', ha='right')
            
            plt.colorbar(im, ax=ax4)
            
            plt.tight_layout()
            
            # Create timestamp for plot filename from data filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            plot_filename = f"../data/{base_name}_plot.png"
            plt.savefig(plot_filename, dpi=150, bbox_inches='tight')
            print(f"Plot saved as: {plot_filename}")
            
            plt.show()
            
        except Exception as e:
            print(f"Error creating plot: {e}")

def main():
    print("=== Enhanced Eye Tracking Controller ===")
    print("Make sure your enhanced eyeTrack.exe is running!")
    
    controller = EnhancedEyeTrackingController()
    
    while True:
        print(f"\n[{controller.get_timestamp()}] === MAIN MENU ===")
        print("RECORDING MODES:")
        print("1. Start continuous recording")
        print("2. Stop continuous recording") 
        print("3. Single burst recording (10 callbacks)")
        print("4. Check recording status")
        print("")
        print("DATA ANALYSIS:")
        print("5. Preview latest data")
        print("6. Plot latest data")
        print("7. List all data files")
        print("8. Select and analyze specific file")
        print("")
        print("SYSTEM:")
        print("9. Send custom command")
        print("0. Quit")
        
        try:
            choice = input(f"\n[{controller.get_timestamp()}] Enter choice (0-9): ").strip()
            print(f"[{controller.get_timestamp()}] User selected: '{choice}'")
            
            if choice == '1':
                print(f"[{controller.get_timestamp()}] Starting continuous recording...")
                if controller.send_command('c'):
                    controller.recording_active = True
                    print("Continuous recording started! Data will be saved with timestamp.")
                    print("Use option 2 to stop when ready.")
                
            elif choice == '2':
                print(f"[{controller.get_timestamp()}] Stopping continuous recording...")
                if controller.send_command('s'):
                    controller.recording_active = False
                    print("Continuous recording stopped!")
                
            elif choice == '3':
                print(f"[{controller.get_timestamp()}] Single burst recording...")
                print("Position your gaze and hold steady...")
                time.sleep(2)
                print("Recording now!")
                controller.send_command('8')
                time.sleep(3)
                print("Burst recording completed.")
                
            elif choice == '4':
                print(f"[{controller.get_timestamp()}] Checking status...")
                controller.send_command('status')
                print(f"Python tracking: Recording active = {controller.recording_active}")
                
            elif choice == '5':
                print(f"[{controller.get_timestamp()}] Analyzing latest data...")
                controller.show_data_preview()
                
            elif choice == '6':
                print(f"[{controller.get_timestamp()}] Creating plot of latest data...")
                controller.plot_gaze_data()
                
            elif choice == '7':
                print(f"[{controller.get_timestamp()}] Listing all data files...")
                files = controller.list_all_data_files()
                if files:
                    print(f"\n=== ALL DATA FILES ===")
                    for file_info in files:
                        print(f"• {file_info['filename']}")
                        print(f"  Modified: {file_info['modified']}, Size: {file_info['size_kb']} KB, Samples: {file_info['samples']}")
                else:
                    print("No data files found.")
                
            elif choice == '8':
                print(f"[{controller.get_timestamp()}] Select specific file to analyze...")
                selected_file = controller.select_data_file_interactive()
                if selected_file:
                    print(f"\nAnalyzing: {os.path.basename(selected_file)}")
                    controller.show_data_preview(selected_file)
                    
                    plot_choice = input("Create plot for this file? (y/n): ").strip().lower()
                    if plot_choice == 'y':
                        controller.plot_gaze_data(selected_file)
                
            elif choice == '9':
                custom_cmd = input("Enter custom command: ").strip()
                if custom_cmd:
                    print(f"[{controller.get_timestamp()}] Sending custom command: '{custom_cmd}'")
                    controller.send_command(custom_cmd)
                
            elif choice == '0':
                print(f"[{controller.get_timestamp()}] Shutting down...")
                if controller.recording_active:
                    print("Stopping any active recording...")
                    controller.send_command('s')
                print("Sending quit command to C++ program...")
                controller.send_command('q')
                print("Goodbye!")
                break
                
            else:
                print(f"[{controller.get_timestamp()}] Invalid choice: {choice}")
                
        except KeyboardInterrupt:
            print(f"\n[{controller.get_timestamp()}] Interrupted by user")
            if controller.recording_active:
                print("Stopping recording...")
                controller.send_command('s')
            print("Sending quit command...")
            controller.send_command('q')
            break
        except Exception as e:
            print(f"[{controller.get_timestamp()}] Error: {e}")

if __name__ == "__main__":
    main()