import socket
import time
import datetime

class EyeTrackingRecorder:
    def __init__(self, host='127.0.0.1', port=1234):
        self.host = host
        self.port = port
    
    def get_timestamp(self):
        """Get current time in human readable format with milliseconds"""
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Remove last 3 digits to get milliseconds
    
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

def main():
    print("=== Continuous Eye Tracking Recorder ===")
    print("Make sure your eyeTrack.exe is running!")
    
    recorder = EyeTrackingRecorder()
    
    while True:
        print(f"\n[{recorder.get_timestamp()}] === MENU ===")
        print("1. Start continuous recording session")
        print("2. Send single data collection command")
        print("3. Quit")
        
        try:
            choice = input(f"\n[{recorder.get_timestamp()}] Enter choice (1-3): ").strip()
            print(f"[{recorder.get_timestamp()}] User pressed '{choice}'")
            
            if choice == '1':
                print(f"[{recorder.get_timestamp()}] Starting continuous recording...")
                recorder.send_command('c')
                print(f"[{recorder.get_timestamp()}] Continuous recording command sent")
                
            elif choice == '2':
                print(f"[{recorder.get_timestamp()}] User selected single data collection")
                print(f"[{recorder.get_timestamp()}] Preparing to send '8' command...")
                
                # Give user time to position gaze
                print("Position your gaze now...")
                time.sleep(2)
                print(f"[{recorder.get_timestamp()}] About to start data collection - hold your gaze steady!")
                
                # Send command
                recorder.send_command('8')
                
                # Wait for collection to complete
                print(f"[{recorder.get_timestamp()}] Data collection in progress...")
                time.sleep(3)  # Adjust based on your LENGTH setting
                print(f"[{recorder.get_timestamp()}] Data collection should be finished")
                
            elif choice == '3':
                print(f"[{recorder.get_timestamp()}] User chose to quit - goodbye!")
                break
            else:
                print(f"[{recorder.get_timestamp()}] Invalid choice: {choice}")
                
        except KeyboardInterrupt:
            print(f"\n[{recorder.get_timestamp()}] Interrupted by user - goodbye!")
            break

if __name__ == "__main__":
    main()