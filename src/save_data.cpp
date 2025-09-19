#include "save_data.h"
#include <chrono>
#include <iomanip>
#include <sstream>
#include <atomic>
#include <string>

// Add this function to save_data.cpp at the top, after includes

std::string generate_timestamped_filename(const std::string& base_path, const std::string& extension) {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    
    std::stringstream filename;
    filename << base_path << std::put_time(std::localtime(&time_t), "%Y%m%d_%H%M%S") << extension;
    return filename.str();
}

// Modify the gaze_point_callback function to use a global filename variable
// Add this global variable at the top of save_data.cpp (or in global.cpp)
extern std::string current_data_filename;

// External variables for continuous recording control
extern std::atomic<bool> continuous_recording;

// Enhanced gaze point callback with continuous recording support
void gaze_point_callback(tobii_gaze_point_t const* gaze_point, void* /* user_data */)
{
    if(gaze_point->validity == TOBII_VALIDITY_VALID)
    {
        // Get current system time
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
        
        // Format: YYYY-MM-DD HH:MM:SS.mmm
        std::stringstream timeStr;
        timeStr << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S");
        timeStr << "." << std::setfill('0') << std::setw(3) << ms.count();
        
        // Always print to console for monitoring
        std::cout << "Gaze point: " << gaze_point->position_xy[0] << "\t" << gaze_point->position_xy[1] << 
                    "\t" << gaze_point->timestamp_us;
        
        // Add recording mode indicator
        if (continuous_recording) {
            std::cout << "\t[CONTINUOUS]";
        } else {
            std::cout << "\t[BURST]";
        }
        std::cout << std::endl;
        
        // Save to timestamped file
        std::ofstream saveFile(current_data_filename, std::ios::app);
        if (saveFile.is_open()) {
            saveFile << timeStr.str() << "\t"                    // Human-readable time
                     << gaze_point->timestamp_us << "\t"         // Original microsecond timestamp  
                     << gaze_point->position_xy[0] << "\t" 
                     << gaze_point->position_xy[1] << "\n";
            saveFile.close();
        } else {
            std::cout << "Warning: Could not open data file for writing: " << current_data_filename << std::endl;
        }
        
        flag_success = true;
    }
    else
    {
        // Only print invalid samples in burst mode to avoid spam in continuous mode
        if (!continuous_recording) {
            std::cout << "Gaze out of screen\t" << gaze_point->timestamp_us << std::endl;
        }
    }
}

// User presence callback - only compile if supported
#ifdef TOBII_USER_PRESENCE_STATUS_UNKNOWN
void user_presence_callback(tobii_user_presence_status_t status, int64_t timestamp_us, void* /* user_data */)
{
    const char* status_str = (status == TOBII_USER_PRESENCE_STATUS_PRESENT) ? "PRESENT" : "NOT_PRESENT";
    std::cout << "User presence: " << status_str << "\t" << timestamp_us << std::endl;
    
    std::ofstream saveFile("../data/user_presence.txt", std::ios::app);
    if (saveFile.is_open()) {
        saveFile << timestamp_us << "\t" << status_str << "\n";
        saveFile.close();
    }
}
#endif

// Eye position callback - only compile if supported  
#ifdef TOBII_EYE_POSITION_NORMALIZED_T
void eye_position_callback(tobii_eye_position_normalized_t const* eye_position, void* /* user_data */)
{
    if(eye_position->left_validity == TOBII_VALIDITY_VALID || eye_position->right_validity == TOBII_VALIDITY_VALID)
    {
        std::cout << "3D Eye Position - Left: (" << eye_position->left_xyz[0] << ", " 
                  << eye_position->left_xyz[1] << ", " << eye_position->left_xyz[2] << ") "
                  << "Right: (" << eye_position->right_xyz[0] << ", " 
                  << eye_position->right_xyz[1] << ", " << eye_position->right_xyz[2] << ")\t"
                  << eye_position->timestamp_us << std::endl;
        
        std::ofstream saveFile("../data/eye_position_3d.txt", std::ios::app);
        if (saveFile.is_open()) {
            saveFile << eye_position->timestamp_us << "\t"
                     << eye_position->left_xyz[0] << "\t" << eye_position->left_xyz[1] << "\t" << eye_position->left_xyz[2] << "\t"
                     << eye_position->right_xyz[0] << "\t" << eye_position->right_xyz[1] << "\t" << eye_position->right_xyz[2] << "\n";
            saveFile.close();
        }
    }
}
#endif

// Original burst mode data collection function
void get_save_data(tobii_device_t* device, int timeLength)
{
    // Generate timestamped filename for this burst session
    current_data_filename = generate_timestamped_filename("../data/gaze_data_", ".txt");
    
    // Clear file and set up headers for new burst session
    std::ofstream clearFile(current_data_filename, std::ios::trunc);
    clearFile << "human_time\ttobii_timestamp_us\tx_position\ty_position\n";
    clearFile.close();
    
    std::cout << "Starting burst data collection (" << timeLength << " callbacks)..." << std::endl;
    std::cout << "Data will be saved to: " << current_data_filename << std::endl;
    
    for(int i = 0; i < timeLength; i++)
    {
        result = tobii_wait_for_callbacks(1, &device);
        assert(result == TOBII_ERROR_NO_ERROR || result == TOBII_ERROR_TIMED_OUT);
        
        result = tobii_device_process_callbacks(device);
        assert(result == TOBII_ERROR_NO_ERROR);
        
        Sleep(50); // Small delay to ensure proper data collection timing
    }
    std::cout << "Burst data collection finished." << std::endl;
    
    // Save success index (keep original index.txt logic if needed)
    if(flag_success)
    {
        success[index_suc] = index_all;
        std::ofstream saveFile("../data/index.txt", std::ios::app);
        if (saveFile.is_open()) {
            saveFile << index_all << "\n";
            saveFile.close();
        }
        index_suc = index_suc + 1;
    }
    index_all = index_all + 1;
    flag_success = false;
    std::cout << "Success: " << index_suc << ", Total: " << index_all << std::endl;
}

// Original function - just gaze points
void start_listen(tobii_device_t* device)
{
    result = tobii_gaze_point_subscribe(device, gaze_point_callback, 0);
    assert(result == TOBII_ERROR_NO_ERROR);
    std::cout << "Gaze point stream subscription active" << std::endl;
}

// New function - subscribe to available streams only
void start_available_streams(tobii_device_t* device)
{
    // Always start gaze points (we know this works)
    result = tobii_gaze_point_subscribe(device, gaze_point_callback, 0);
    if(result == TOBII_ERROR_NO_ERROR) 
        std::cout << "Gaze point stream started" << std::endl;
    else
        std::cout << "Gaze point stream failed" << std::endl;
    
    // Try user presence if supported
#ifdef TOBII_USER_PRESENCE_STATUS_UNKNOWN
    result = tobii_user_presence_subscribe(device, user_presence_callback, 0);
    if(result == TOBII_ERROR_NO_ERROR) 
        std::cout << "User presence stream started" << std::endl;
    else
        std::cout << "User presence stream not available" << std::endl;
#endif
    
    // Try 3D eye position if supported
#ifdef TOBII_EYE_POSITION_NORMALIZED_T
    result = tobii_eye_position_normalized_subscribe(device, eye_position_callback, 0);
    if(result == TOBII_ERROR_NO_ERROR) 
        std::cout << "3D eye position stream started" << std::endl;
    else
        std::cout << "3D eye position stream not available" << std::endl;
#endif
}

// New function: Prepare file for continuous recording
void prepare_continuous_recording()
{
    std::cout << "Preparing file for continuous recording..." << std::endl;
    
    // Clear file and set up headers
    std::ofstream clearFile("../data/gaze_data.txt", std::ios::trunc);
    if (clearFile.is_open()) {
        clearFile << "human_time\ttobii_timestamp_us\tx_position\ty_position\n";
        clearFile.close();
        std::cout << "Data file prepared: ../data/gaze_data.txt" << std::endl;
    } else {
        std::cout << "Error: Could not prepare data file!" << std::endl;
    }
}

// New function: Get current data file statistics
void show_data_statistics()
{
    std::ifstream dataFile("../data/gaze_data.txt");
    if (!dataFile.is_open()) {
        std::cout << "No data file found." << std::endl;
        return;
    }
    
    std::string line;
    int lineCount = 0;
    
    // Count lines (excluding header)
    while (std::getline(dataFile, line)) {
        lineCount++;
    }
    
    dataFile.close();
    
    if (lineCount > 1) {
        std::cout << "Data file contains " << (lineCount - 1) << " gaze samples" << std::endl;
    } else {
        std::cout << "Data file is empty (header only)" << std::endl;
    }
}