Traffic Light Control System Using Reinforcement Learning
Python Implementation

Overview

This project simulates a four-lane intersection (north, east, south, and west) and utilizes Reinforcement Learning (RL) to optimize traffic light timing. The objective is to reduce vehicle wait times and enhance traffic flow efficiency by dynamically adjusting green light durations based on real-time traffic patterns.

Key Features

Reinforcement Learning-Driven Control: The system employs an RL agent to determine which lane receives the green light based on live traffic data.
Dynamic Traffic Simulation: Realistic traffic patterns are generated, simulating varying vehicle densities during peak and off-peak hours.
Customizable Intersection Settings: Parameters like green light duration, vehicle crossing time, and maximum waiting time are fully adjustable.
Four-Lane Traffic Management: Traffic flow is managed for four independent lanes, each with unique vehicle counts and states.
Reward-Based Optimization: A tailored reward system encourages the RL agent to clear traffic efficiently, penalizing delays to ensure optimal performance.
Environment Details

Action Space: The agent selects from four discrete actions, representing which lane should receive the green light.
Observation Space: The state consists of the current vehicle count in each lane.
Vehicle Cross Time: Default crossing time is set to 3 seconds per vehicle, adjustable as needed.
Adaptive Green Light Duration: While the default is 10 seconds, green light durations dynamically adjust to match traffic conditions.
Peak and Off-Peak Simulation: Traffic densities vary to mimic morning and evening rush hours, creating a realistic simulation.
Episode Limit: Each simulation runs for up to 100 steps per episode. Delays or inefficiencies are penalized if the limit is reached without clearing traffic effectively.
How It Works

Vehicle Generation: Vehicles are generated randomly for each lane based on traffic conditions, varying by time of day (peak or off-peak).
Traffic Light Control: The RL agent observes vehicle counts and selects the lane to receive the green light, prioritizing efficient traffic flow.
Reward System: Positive rewards are granted for reducing congestion and clearing vehicles promptly. Negative rewards are applied for delays or traffic mismanagement.

![traffic-management-1](https://github.com/user-attachments/assets/d72f80f9-47d5-4733-9a5a-f62a6f19cfe8)


Simulation Progression: The simulation continues step-by-step until the maximum episode limit is reached or all lanes are cleared.
Highlights

Configurable Parameters: Adjust traffic settings such as vehicle density, crossing speed, and light duration to match different scenarios.
Real-World Relevance: Simulates realistic traffic patterns, providing a foundation for smarter traffic management solutions.
Scalable Design: Easily extendable to handle intersections with more lanes or complex layouts.
