#include "connect.h"
#include "save_data.h"
#include "server.h"
#include "global.h"
#include <iostream>
#include <thread>
#include <atomic>

#define LENGTH 10  // For burst mode

// Global control variables for continuous recording
std::atomic<bool> continuous_recording(false);
std::atomic<bool> program_running(true);

void continuous_recording_loop(tobii_device_t* device) {
    std::cout << "Continuous recording thread started" << std::endl;
    
    while (program_running) {
        if (continuous_recording) {
            // Process callbacks while continuous recording is active
            result = tobii_wait_for_callbacks(1, &device);
            if (result == TOBII_ERROR_NO_ERROR || result == TOBII_ERROR_TIMED_OUT) {
                result = tobii_device_process_callbacks(device);
                if (result != TOBII_ERROR_NO_ERROR) {
                    std::cout << "Error processing callbacks: " << result << std::endl;
                }
            }
            Sleep(10); // Small delay to prevent excessive CPU usage
        } else {
            Sleep(50); // Longer delay when not recording
        }
    }
    
    std::cout << "Continuous recording thread ended" << std::endl;
}

void start_continuous_recording() {
    if (!continuous_recording) {
        // Generate timestamped filename for this continuous session
        current_data_filename = generate_timestamped_filename("../data/gaze_data_", ".txt");
        
        // Clear file and set up headers for new continuous session
        std::ofstream clearFile(current_data_filename, std::ios::trunc);
        clearFile << "human_time\ttobii_timestamp_us\tx_position\ty_position\n";
        clearFile.close();
        
        continuous_recording = true;
        std::cout << "=== CONTINUOUS RECORDING STARTED ===" << std::endl;
        std::cout << "Data will be saved to: " << current_data_filename << std::endl;
        std::cout << "Send 's' command to stop recording." << std::endl;
    } else {
        std::cout << "Continuous recording is already active!" << std::endl;
    }
}

void stop_continuous_recording() {
    if (continuous_recording) {
        continuous_recording = false;
        std::cout << "=== CONTINUOUS RECORDING STOPPED ===" << std::endl;
        std::cout << "Final data saved to ../data/gaze_data.txt" << std::endl;
    } else {
        std::cout << "No continuous recording active to stop." << std::endl;
    }
}

int main()
{
    std::cout << "=== Enhanced Tobii Eye Tracker Program ===" << std::endl;
    std::cout << "Initializing..." << std::endl;
    
    // Initialize Tobii API and device
    api = api_create();
    char* url = get_device(api);
    device = device_create(api, url);
    
    // Subscribe to gaze point stream
    start_listen(device);
    std::cout << "Gaze point subscription active" << std::endl;
    
    // Initialize UDP server
    init_server();
    std::cout << "UDP server listening on 127.0.0.1:1234" << std::endl;
    
    // Start continuous recording thread
    std::thread recording_thread(continuous_recording_loop, device);
    
    std::cout << "\n=== COMMAND REFERENCE ===" << std::endl;
    std::cout << "'8' = Burst recording (10 callbacks)" << std::endl;
    std::cout << "'c' = Start continuous recording" << std::endl;
    std::cout << "'s' = Stop continuous recording" << std::endl;
    std::cout << "'q' = Quit program" << std::endl;
    std::cout << "'status' = Show recording status" << std::endl;
    std::cout << "=========================" << std::endl;
    
    // Main command loop
    while (program_running) {
        std::cout << "\nWaiting for command..." << std::endl;
        
        // Receive UDP command
        int strLen = recvfrom(sock, buffer, BUF_SIZE, 0, &clintAddr, &nSize);
        if (strLen > 0) {
            buffer[strLen] = '\0';  // Null terminate
            std::string command(buffer);
            
            std::cout << "Received command: '" << command << "'" << std::endl;
            
            if (command == "8") {
                // Original burst mode
                std::cout << "=== BURST MODE RECORDING ===" << std::endl;
                if (continuous_recording) {
                    std::cout << "Warning: Stopping continuous recording for burst mode" << std::endl;
                    stop_continuous_recording();
                    Sleep(100); // Brief pause
                }
                get_save_data(device, LENGTH);
                std::cout << "Burst recording completed." << std::endl;
                
            } else if (command == "c") {
                // Start continuous recording
                start_continuous_recording();
                
            } else if (command == "s") {
                // Stop continuous recording
                stop_continuous_recording();
                
            } else if (command == "q") {
                // Quit program
                std::cout << "Quit command received - shutting down..." << std::endl;
                stop_continuous_recording();
                program_running = false;
                
            } else if (command == "status") {
                // Show current status
                std::cout << "=== STATUS ===" << std::endl;
                std::cout << "Program running: " << (program_running ? "YES" : "NO") << std::endl;
                std::cout << "Continuous recording: " << (continuous_recording ? "ACTIVE" : "INACTIVE") << std::endl;
                std::cout << "Success count: " << index_suc << std::endl;
                std::cout << "Total attempts: " << index_all << std::endl;
                
            } else {
                std::cout << "Unknown command: '" << command << "'" << std::endl;
                std::cout << "Valid commands: '8', 'c', 's', 'q', 'status'" << std::endl;
            }
        }
    }
    
    // Cleanup
    std::cout << "Cleaning up..." << std::endl;
    recording_thread.join();
    close_connect(device, api);
    close_udp(sock);
    
    std::cout << "Program ended successfully." << std::endl;
    return 0;
}