# TL DR! README

## Setup
1. Ubuntu-24.04
2. ROS2 Jazzy -- advised to install via binaries
3. Gazebo Harmonic
4. ros_gz bridge for the pair in use
5. Gemini API usage toolkit

## Procedure to make it
1. Use fusion 360 to prepare 3D model ( a CAD file) of bot ---> follow naming conventions as per https://github.com/runtimerobotics/fusion360-urdf-ros2 . This video might be helpful https://www.youtube.com/watch?v=GTFPwJnb_fk --> this one works in 2026 --> You might have to find something else if you are in 2027 or next years usually fusion updates break's this. 
2. About URDF
   This is needed to us to observe stuff in physics engine of gazebo.
	1. Now you will have to modify .xacro files contains URDF that is object description format used by Gazebo.
	2. .gazebo files are used to add gazebo references to ass physics to bodies that are stored as STL. This is where we also add gazebo plugins that we will use further to bring data into ROS2 space to control motion of joints by using ROS2.
	3. .ros2control is how ROS2 control library can be used and integrated though not used in this project but would be helpful. Leave it as it is.
	4. materials is useful for choosing what kind of material the  body is made of in gazebo will be soft like sponge or a hard metal sheet. Leave it as it is.
3. Modify ros_gz_bridge_gazebo.yaml file to have joints information. The standard style of writing topic names and topic data type is a clearly seen pattern.
4. By now you will have built a system that data like wheel_speed=5, leg_angle=30 such high level but specific commands and move the bot accordingly. But the way to input these will be using
   ``ros2 topic pub --once /left_leg_joint/cmd_vel std_msgs/msg/Float64 "{data: 0.5}"``
   Using such kind of codes you would have to manually run such commands for each joint. To avoid manually setting speed values we add an API here to convert human language into such codes for bot to run.
   `ros2 topic pub --once /high_level_nav_cmd std_msgs/msg/String "{data: 'slight left'}" `
   this will make bot move to left.
5. For this to work just add you API key of Gemini only into run_bot_via_gemini.sh.


## How to run?
just clone repo run rub_bot_via_gemini.sh after doing the above mentioned changes



## Directory Structure
```
├── bot_description
├── config
├── control_node.py
├── launch
├── meshes
├── package.xml
├── resource
├── ros2_env
├── run_bot_via_gemini.sh
├── setup.cfg
├── setup.py
├── test
└── urdf
    ├── bot.gazebo
    ├── bot.ros2control
    ├── bot.xacro
    └── materials.xacro
```