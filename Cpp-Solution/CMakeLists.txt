cmake_minimum_required(VERSION 3.10)
project(river_crossing)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(include)

# Source files
set(SOURCES
    src/main.cpp
    src/State.cpp
    src/Solver.cpp
)

# Create executable
add_executable(river_crossing ${SOURCES})