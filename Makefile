# Enhanced Makefile for Tobii Eye Tracker
# Updated for new directory structure and enhanced features

# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++11 -Wall -O2
INCLUDES = -I./src -I./tobii
LIBS = -L./lib -ltobii_stream_engine -lws2_32

# Directories
SRCDIR = src
BINDIR = bin
OBJDIR = bin
DATADIR = data

# Source files (all in src directory)
SOURCES = $(SRCDIR)/main.cpp $(SRCDIR)/connect.cpp $(SRCDIR)/save_data.cpp $(SRCDIR)/server.cpp $(SRCDIR)/global.cpp

# Object files (compiled to bin directory)
OBJECTS = $(OBJDIR)/main.o $(OBJDIR)/connect.o $(OBJDIR)/save_data.o $(OBJDIR)/server.o $(OBJDIR)/global.o

# Target executable
TARGET = $(BINDIR)/eyeTrack.exe

# Default target
all: setup $(TARGET)

# Create necessary directories
setup:
	@echo "============SETUP DIRECTORIES============"
	@mkdir -p $(BINDIR)
	@mkdir -p $(DATADIR)
	@echo "Directories created/verified"

# Build the main executable
$(TARGET): $(OBJECTS)
	@echo "============LINKING============"
	$(CXX) $(OBJECTS) -o $(TARGET) $(LIBS)
	@echo "Build successful: $(TARGET)"

# Compile individual source files
$(OBJDIR)/main.o: $(SRCDIR)/main.cpp
	@echo "============COMPILING main.cpp============"
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $(SRCDIR)/main.cpp -o $(OBJDIR)/main.o

$(OBJDIR)/connect.o: $(SRCDIR)/connect.cpp $(SRCDIR)/connect.h
	@echo "============COMPILING connect.cpp============"
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $(SRCDIR)/connect.cpp -o $(OBJDIR)/connect.o

$(OBJDIR)/save_data.o: $(SRCDIR)/save_data.cpp $(SRCDIR)/save_data.h
	@echo "============COMPILING save_data.cpp============"
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $(SRCDIR)/save_data.cpp -o $(OBJDIR)/save_data.o

$(OBJDIR)/server.o: $(SRCDIR)/server.cpp $(SRCDIR)/server.h
	@echo "============COMPILING server.cpp============"
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $(SRCDIR)/server.cpp -o $(OBJDIR)/server.o

$(OBJDIR)/global.o: $(SRCDIR)/global.cpp $(SRCDIR)/global.h
	@echo "============COMPILING global.cpp============"
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $(SRCDIR)/global.cpp -o $(OBJDIR)/global.o

# Clean build files
clean:
	@echo "============CLEANING============"
	@rm -f $(OBJDIR)/*.o
	@rm -f $(TARGET)
	@echo "Clean completed"

# Clean data files
clean-data:
	@echo "============CLEANING DATA============"
	@rm -f $(DATADIR)/*.txt
	@rm -f $(DATADIR)/*.png
	@echo "Data files cleaned"

# Full clean (build files + data)
clean-all: clean clean-data

# Run the program
run: $(TARGET)
	@echo "============RUNNING PROGRAM============"
	cd $(BINDIR) && ./eyeTrack.exe

# Show help
help:
	@echo "Available targets:"
	@echo "  all       - Build the complete project (default)"
	@echo "  setup     - Create necessary directories"
	@echo "  clean     - Remove compiled object files and executable"
	@echo "  clean-data- Remove data files"
	@echo "  clean-all - Remove all generated files"
	@echo "  run       - Build and run the program"
	@echo "  help      - Show this help message"

# Declare phony targets
.PHONY: all setup clean clean-data clean-all run help