#ifndef _SAVE_DATA_H
#define _SAVE_DATA_H

#include "global.h"
#include <stdio.h>
#include <assert.h>
#include <string>
#include <iostream>
#include <fstream>
#include <atomic>
#include "../tobii/tobii.h"
#include "../tobii/tobii_streams.h"

extern char url[256];
extern tobii_api_t* api;
extern tobii_device_t* device;
extern tobii_error_t result;

extern int index_suc;
extern int index_all;
extern int success[SUCCESS_TIME];
extern bool flag_success;

// External variables for continuous recording (declared in main.cpp)
extern std::atomic<bool> continuous_recording;
extern std::atomic<bool> program_running;

// Basic gaze callback (works for both burst and continuous modes)
void gaze_point_callback(tobii_gaze_point_t const* gaze_point, void* user_data);

// Only add additional callbacks if the types exist
#ifdef TOBII_USER_PRESENCE_STATUS_UNKNOWN
void user_presence_callback(tobii_user_presence_status_t status, int64_t timestamp_us, void* user_data);
#endif

#ifdef TOBII_EYE_POSITION_NORMALIZED_T
void eye_position_callback(tobii_eye_position_normalized_t const* eye_position, void* user_data);
#endif

// Original functions
void get_save_data(tobii_device_t* device, int timeLength);  // Burst mode
void start_listen(tobii_device_t* device);                  // Subscribe to gaze points

// Enhanced function to start available streams
void start_available_streams(tobii_device_t* device);

// New functions for continuous recording support
void prepare_continuous_recording();   // Set up file for continuous recording
void show_data_statistics();          // Show current data file stats

std::string generate_timestamped_filename(const std::string& base_path, const std::string& extension);
#endif