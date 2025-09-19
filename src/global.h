#ifndef _GLOBAL_H
#define _GLOBAL_H

#include "../tobii/tobii.h"
#include "../tobii/tobii_streams.h"
#include <winsock2.h>
#include <string>


#define BUF_SIZE 100
#define SUCCESS_TIME 1000

#pragma comment (lib, "ws2_32.lib")  //加载 ws2_32.dll


// Global variables declarations
extern char url[256];
extern tobii_api_t* api;
extern tobii_device_t* device;
extern tobii_error_t result;

extern WSADATA wsaData;
extern char buffer[BUF_SIZE];  //缓冲区大小
extern SOCKET sock;
extern sockaddr_in servAddr;
extern SOCKADDR clintAddr;
extern int nSize;

extern int index_suc;
extern int index_all;
extern int success[SUCCESS_TIME];
extern bool flag_success;

extern std::string current_data_filename;


#endif