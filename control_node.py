#!/usr/bin/env python3
import os
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# 1. Define the strict output schema matching your exact joints
class RobotControlSchema(BaseModel):
    left_wheel_vel: float = Field(description="Velocity for left wheel joint, range -2.0 to 2.0")
    right_wheel_vel: float = Field(description="Velocity for right wheel joint, range -2.0 to 2.0")
    left_leg_vel: float = Field(description="Velocity for left stability leg, range -1.0 to 1.0")
    right_leg_vel: float = Field(description="Velocity for right stability leg, range -1.0 to 1.0")

class GeminiRobotController(Node):
    def __init__(self):
        super().__init__('gemini_robot_controller')

        # Initialize Gemini client
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            self.get_logger().error("API Key missing! Please run: export GEMINI_API_KEY='your_key'")
            return
        self.client = genai.Client(api_key=api_key)

        # 2. Setup publishers targeting your exact ROS 2 topic list
        self.pub_left_wheel = self.create_publisher(Float64, '/left_wheel_joint/cmd_vel', 10)
        self.pub_right_wheel = self.create_publisher(Float64, '/right_wheel_joint/cmd_vel', 10)
        self.pub_left_leg = self.create_publisher(Float64, '/left_leg_joint/cmd_vel', 10)
        self.pub_right_leg = self.create_publisher(Float64, '/right_leg_joint/cmd_vel', 10)

        # 3. Setup subscriber for high-level language inputs
        self.sub_high_level_cmd = self.create_subscription(
            String, 
            '/high_level_nav_cmd', 
            self.command_callback, 
            10
        )
        
        self.get_logger().info("Gemini control node running. Listening on topic: /high_level_nav_cmd")

    def command_callback(self, msg):
        user_prompt = msg.data
        self.get_logger().info(f"Processing command: '{user_prompt}'")

        # Define specialized logic for your wheel-legged topology
        system_instruction = """
        You control a hybrid robot with two rear differential wheels and two side stabilizing legs. 
        Convert spatial navigation commands into precise motor velocities.
        
        Kinematic Translation Rules:
        - Go Straight: Both wheels equal positive velocity.
        - Left Turns (slight/more/hard): Right wheel spins faster than left wheel. 
        - Right Turns (slight/more/hard): Left wheel spins faster than right wheel.
        - For 'hard' or 'more' turns, utilize the side legs to apply counter-velocities (- and +) 
          to help lean the chassis into the pivot point to prevent tipping.
        """

        try:
            # Request inference using Gemini 2.5 Flash for rapid low-latency control response
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=RobotControlSchema, # Forces Gemini to return data matching our class
                    temperature=0.1 # Low temperature ensures reliable kinematic scaling
                ),
            )

            # Parse structural JSON output directly
            data = json.loads(response.text)
            
            # Construct standard ROS 2 Float64 messages
            msg_lw = Float64(data=float(data['left_wheel_vel']))
            msg_rw = Float64(data=float(data['right_wheel_vel']))
            msg_ll = Float64(data=float(data['left_leg_vel']))
            msg_rl = Float64(data=float(data['right_leg_vel']))

            # Publish synchronized commands to Gazebo Harmonic interfaces
            self.pub_left_wheel.publish(msg_lw)
            self.pub_right_wheel.publish(msg_rw)
            self.pub_left_leg.publish(msg_ll)
            self.pub_right_leg.publish(msg_rl)

            self.get_logger().info(
                f"Dispatched -> Wheels: [L: {msg_lw.data}, R: {msg_rw.data}] | Legs: [L: {msg_ll.data}, R: {msg_rl.data}]"
            )

        except Exception as e:
            self.get_logger().error(f"Failed to generate or parse control vectors: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = GeminiRobotController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()