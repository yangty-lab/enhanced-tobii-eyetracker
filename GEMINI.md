# Enhanced Tobii Eye Tracker 5 for Research - Project Overview

This project provides a comprehensive solution for utilizing the consumer-grade Tobii Eye Tracker 5 as a research instrument. It enhances the device's capabilities by adding continuous recording, automated data analysis, and robust experiment integration. The system aims to bridge the gap between Tobii's Stream Engine API and the stringent requirements of research, delivering high-quality gaze coordinate data with microsecond-precision timestamps.

## Key Technologies and Architecture

The system employs a hybrid C++/Python architecture:

*   **C++ Program (`eyeTrack.exe`)**: Handles the direct hardware interface via the Tobii Stream Engine, streams continuous gaze data (~90Hz), acts as a UDP server for experiment control, and performs real-time data validation and storage.
*   **Python Controller**: Manages experiment timing and control, performs data analysis and visualization (gaze trajectories, heatmaps), offers interactive file management, and generates statistical reports.

The data flow involves hardware sampling, stream processing by the C++ program, quality filtering for valid samples, storage with dual timestamps, and subsequent analysis by the Python controller.

## Building and Running the Project

### Prerequisites

*   **Hardware**: Tobii Eye Tracker 5, Windows 10/11.
*   **Software**: MSYS2 MinGW64 (for C++ build tools like make, g++, cmake), Anaconda or Miniconda (for Python environment).

### Installation and Setup

1.  **Clone Repository**:
    ```bash
    git clone https://github.com/basophobic/enhanced-tobii-eyetracker.git
    cd enhanced-tobii-eyetracker
    ```
2.  **Setup Python Environment**:
    ```bash
    conda env create -f environment.yml
    conda activate eyetracking
    ```
    (Alternatively, manual setup: `conda create -n eyetracking python=3.9`, then `conda install numpy pandas matplotlib scipy pygame`)
3.  **Build C++ Program (in MSYS2 MinGW64 terminal)**:
    ```bash
    make clean
    make
    ```

### Usage

1.  **Start the Eye Tracker Program (in MSYS2 MinGW64 terminal)**:
    ```bash
    cd /C/enhanced-tobii-eyetracker/bin
    ./eyeTrack.exe
    ```
2.  **Run Python Controller (in Anaconda Prompt)**:
    ```bash
    cd C:\enhanced-tobii-eyetracker\python
    conda activate eyetracking
    python enhanced_controller.py
    ```

### Command Reference (C++ program via UDP on port 1234)

*   `'c'`: Start continuous recording
*   `'s'`: Stop continuous recording
*   `'8'`: Burst recording (10 callbacks)
*   `'status'`: Show recording status
*   `'q'`: Quit program

## Development Conventions

*   **Code Style**: Follow existing code style and structure within the codebase.
*   **Testing**: Thoroughly test on Windows 10/11 systems.
*   **Documentation**: Update documentation for any new features implemented.
*   **Compatibility**: Maintain backward compatibility where possible.
*   **Building**: Use `make clean` before recompiling, and `make CXXFLAGS="-std=c++11 -Wall -g"` for debugging.

## Project File Structure

```
enhanced-tobii-eyetracker/
├── README.md
├── environment.yml          # Conda environment specification
├── Makefile                # C++ build configuration
├── bin/                    # Compiled executables
│   └── eyeTrack.exe
├── data/                   # Data output directory
│   ├── gaze_data_*.txt     # Timestamped data files
│   ├── *_plot.png          # Generated visualizations
│   └── index.txt           # Session tracking
├── lib/                    # Tobii libraries
│   └── tobii_stream_engine.dll
├── python/                 # Python scripts
│   ├── enhanced_controller.py
│   └── record_gaze.py
├── src/                    # C++ source code
│   ├── main.cpp
│   ├── connect.cpp/h
│   ├── save_data.cpp/h
│   ├── server.cpp/h
│   ├── global.cpp/h
│   └── utils.py
└── tobii/                  # Tobii SDK headers
    ├── tobii.h
    └── tobii_streams.h
```