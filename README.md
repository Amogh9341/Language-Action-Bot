# Gemini Controlled Bot

> [!info]
> Convert natural language instructions into robot actions inside ROS2 + Gazebo using Gemini.

---

## Table of Contents

* [[#What Have I Built?]]
* [[#Setup]]
* [[#Procedure To Make It]]
* [[#Running The Project]]
* [[#Debugging]]
* [[#Directory Structure]]

---

# What Have I Built?

> [!abstract]
> This project creates a language-to-action layer on top of ROS2.

Normally ROS2 requires low-level commands:

```bash
ros2 topic pub --once /left_leg_joint/cmd_vel \
std_msgs/msg/Float64 "{data: 0.5}"
```

This project allows:

```bash
ros2 topic pub --once /high_level_nav_cmd \
std_msgs/msg/String "{data: 'slight left'}"
```

The translation pipeline is:

```text
Human Language
      ↓
 Gemini API
      ↓
control_node.py
      ↓
ROS2 Topics
      ↓
Gazebo Robot
```

---

# Setup

> [!tip]
> Recommended versions are known to work together.

```text
Ubuntu        : 24.04
ROS2          : Jazzy
Gazebo        : Harmonic
Bridge        : ros_gz_bridge
LLM           : Gemini API
```

---

# Procedure To Make It

## 1. Create CAD Model

Use Fusion 360 to prepare the robot CAD model.

Follow naming conventions from:

https://github.com/runtimerobotics/fusion360-urdf-ros2

Helpful video:

https://www.youtube.com/watch?v=GTFPwJnb_fk

> [!warning]
> This video works in 2026. Fusion updates frequently break exporter plugins and workflows. If you are using a newer Fusion release, you may need to find an updated export workflow.

<details>
<summary>Common Issues</summary>

### Missing Parts In Gazebo

Check:

* STL files exist inside `meshes/`
* Component names were exported correctly
* Link names match URDF references

### Robot Appears With Wrong Joint Locations

Usually caused by:

* Incorrect Fusion hierarchy
* Wrong joint origins
* Incorrect rotation axes

### Exporter Fails

Usually caused by:

* Fusion version mismatch
* Exporter installation issues
* Naming convention violations

</details>

---

## 2. Understanding The URDF Files

> [!info]
> URDF is needed for Gazebo to understand the robot structure and simulate physics.

### bot.xacro

Contains:

* Links
* Joints
* Geometry
* Robot hierarchy

### bot.gazebo

Used to add:

* Gazebo references
* Physics properties
* Plugins
* Sensor integrations

This is where Gazebo plugins are attached so information can later be brought into ROS2 space.

### bot.ros2control

Defines ROS2 Control integration.

Not used directly in this project.

Leave it as-is.

### materials.xacro

Material definitions used by Gazebo.

Can affect visual appearance and physical properties.

Leave it as-is.

<details>
<summary>Common Issues</summary>

### Robot Falls Apart

Check:

* Parent-child link relationships
* Joint definitions
* Joint origins

### Robot Invisible

Check:

* STL paths
* Mesh filenames
* Package paths

### Robot Explodes On Spawn

Usually caused by:

* Bad inertia values
* Overlapping geometry
* Unrealistic masses

### Robot Falls Through Floor

Check collision geometry.

Visual geometry alone is not enough.

### Robot Spawns Sideways

Usually a coordinate frame mismatch between Fusion and Gazebo.

</details>

---

## 3. Configure ROS ↔ Gazebo Bridge

Modify:

```text
config/ros_gz_bridge_gazebo.yaml
```

Add joint information.

The standard naming and topic type pattern is already present throughout the file.

Follow the existing style.

You should typically bridge:

* Joint command topics
* Joint state topics
* Sensor topics

<details>
<summary>Common Issues</summary>

### Topic Exists In Gazebo But Not In ROS2

Check:

```bash
ros2 topic list
```

Possible causes:

* Missing bridge entry
* Wrong topic type
* Bridge not running

### Sensor Data Missing

Check:

* Gazebo plugin loaded
* Topic correctly bridged
* Topic names match exactly

### Type Mismatch Errors

Verify message types carefully.

ROS2 and Gazebo often use different internal message definitions.

</details>

---

## 4. Joint-Level Control

At this stage your robot should already be controllable.

Example:

```bash
ros2 topic pub --once \
/left_leg_joint/cmd_vel \
std_msgs/msg/Float64 \
"{data: 0.5}"
```

By now you have effectively built a system where commands such as:

```text
wheel_speed = 5
leg_angle = 30
```

can move the robot.

The problem is that you must manually publish commands for every joint.

---

## 5. Add Natural Language Control

To avoid manually publishing individual joint commands, this project adds a language interface.

Instead of:

```bash
ros2 topic pub --once /left_leg_joint/cmd_vel ...
ros2 topic pub --once /right_leg_joint/cmd_vel ...
```

you can use:

```bash
ros2 topic pub --once \
/high_level_nav_cmd \
std_msgs/msg/String \
"{data: 'slight left'}"
```

Gemini converts the command into the required joint actions.

The robot then executes those actions through ROS2 topics.

---

# Running The Project

## Add Gemini API Key

Edit:

```bash
run_bot_via_gemini.sh
```

Insert your Gemini API key.

---

## Launch

```bash
git clone <repo>

cd <repo>

./run_bot_via_gemini.sh
```

---

# Directory Structure

```text
.
├── bot_description
├── config
├── launch
├── meshes
├── urdf
├── control_node.py
├── run_bot_via_gemini.sh
└── ...
```

---

# Debugging

> [!warning]
> Most failures occur before Gemini is involved.

Always debug from bottom to top.

```text
Robot Doesn't Move
        │
        ▼
Can Joint Topics Move Robot?
        │
       No
        │
 Fix URDF / Gazebo
        │
       Yes
        ▼
Can ROS2 Publish Commands?
        │
       No
        │
 Fix Bridge
        │
       Yes
        ▼
Can control_node.py Publish?
        │
       No
        │
 Fix Control Node
        │
       Yes
        ▼
Can Gemini Generate Commands?
        │
       No
        │
 Fix API / Prompt
        │
       Yes
        ▼
System Working
```

---

## Robot Appears But Does Not Move

Check:

```bash
ros2 topic list
```

Verify command topics exist.

Then manually publish a joint command.

If manual commands fail, Gemini is not the problem.

---

## Topics Missing

Check:

```text
config/ros_gz_bridge_gazebo.yaml
```

Verify:

* Topic names
* Message types
* Bridge launch status

---

## Robot Moves Incorrectly

Common causes:

* Wrong joint sign conventions
* Incorrect wheel orientation
* Wrong joint axes

---

## Gemini Works But Nothing Happens

Check:

* Internet connectivity
* Gemini API key
* API quota
* `control_node.py` logs
* Joint command topics

---

## Robot Behaves Unexpectedly

Gemini can only use the information it knows.

If commands are interpreted incorrectly:

* Improve the Gemini prompt
* Define robot capabilities clearly
* Specify supported actions
* Define joint limits

---

# How The System Is Built

```text
CAD Model
    ↓
URDF/Xacro
    ↓
Gazebo Simulation
    ↓
ROS2 Topics
    ↓
High-Level Command Topic
    ↓
Gemini
    ↓
Joint Commands
```

> [!success]
> At this point you have a robot that can be controlled using natural language rather than manually publishing commands to every individual joint.
