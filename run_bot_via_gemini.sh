#!/bin/bash

# 1. (Optional) Rebuild only if you pass the --build flag
if [ "$1" == "--build" ]; then
    echo "Cleaning and building workspace..."
    rm -rf build/ install/ log/
    colcon build --symlink-install
fi

# 2. Source the ROS2 workspace environment
source /opt/ros/jazzy/setup.bash
if [ -f install/setup.bash ]; then
    source install/setup.bash
else
    echo "Setup file not found! Please build your workspace first."
    exit 1
fi

# 3. Launch Gazebo Harmonic in the BACKGROUND using the '&' symbol
echo "Launching Gazebo simulation..."
ros2 launch bot_description gazebo.launch.py &
GAZEBO_PID=$! # Capture the process ID of Gazebo so we can close it later

# 4. Wait for Gazebo to fully load up (adjust seconds if your PC is fast/slow)
echo "Waiting 5 seconds for Gazebo to initialize..."
sleep 5

# 5. Set API key and launch the Gemini Node in the FOREGROUND
echo "Starting Gemini Control Node..."
# Export your Gemini API key as an environment variable (replace with your actual key)
export GEMINI_API_KEY="your-actual-api-key"
python3 control_node.py
# 6. Clean up: If you close the Gemini script (Ctrl+C), kill Gazebo automatically
echo "Shutting down simulation..."
kill $GAZEBO_PID