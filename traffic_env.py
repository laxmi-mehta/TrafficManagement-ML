import numpy as np
import gym
from gym import spaces


# North : 0 , East : 1, South : 2, West : 3
class TrafficEnv(gym.Env):
    def __init__(self, num_directions=4):
        super(TrafficEnv, self).__init__()
        self.num_directions = num_directions
        self.action_space = spaces.Discrete(num_directions)  
        self.observation_space = spaces.Box(low=0, high=100, shape=(num_directions,), dtype=np.float32)  

        # Lane settings based on number of directions
        self.lanes = {direction: {'vehicles': 0, 'color': 'red', 'state': True} for direction in self.get_directions()}
        
        self.update_lane_time = np.array([0] * num_directions)
        self.current_state = np.array([0] * num_directions)
        self.min_green_duration = 10  
        self.max_wait_time = 120  
        self.vehicle_cross_time = 3  

        self.steps = 0
        self.max_steps = 100  

    def get_directions(self):
        if self.num_directions == 3:
            return [0, 1, 2]  
        elif self.num_directions == 4:
            return [0, 1, 2, 3]  
        else:
            raise ValueError("num_directions must be 3 or 4")

    def reset(self):
        for lane in self.lanes:
            self.lanes[lane]['vehicles'] = 0
            self.lanes[lane]['color'] = 'red'
        self.current_state = np.array([0] * self.num_directions)
        return self.current_state

    def step(self, action):
        self.steps += 1

        lane_names = self.get_directions()
        vehicle_counts = np.array([self.lanes[lane]['vehicles'] for lane in lane_names])
        sorted_indices = np.argsort(-vehicle_counts)
        self.green_signal_order = [lane_names[i] for i in sorted_indices]

        for i in range(self.num_directions):
            total_time_required = (self.lanes[self.green_signal_order[i]]['vehicles'] * self.vehicle_cross_time) / 3
            self.update_lane_time[i] = min(total_time_required, self.max_wait_time)
            if (self.update_lane_time[i] <= 10):
                self.update_lane_time[i] = self.min_green_duration

        done = self.steps >= self.max_steps
        return np.array(self.update_lane_time), 0, done, {'green_signal_order': self.green_signal_order}

    def set_vehicles(self, *args):
        directions = self.get_directions()
        for i, direction in enumerate(directions):
            if i < len(args):
                self.lanes[direction]['vehicles'] = args[i]

    def render(self, mode='ansi'):
        if mode == 'ansi':
            return {
                'current_green_lane': self.current_green_lane,
                'time_remaining': self.time_remaining,
                'next_green_lane': self.current_green_lane
            }
        elif mode == 'human':
            print(f"Current State: {self.current_state}")
            print("Lane Status:")
            for lane, info in self.lanes.items():
                print(f"{lane.capitalize()}: {info['vehicles']} vehicles, light {info['color']}")
            print(f"Current Green Light Lane: {self.current_green_lane.capitalize()}")
            print(f"Time Remaining for Green Light: {self.time_remaining} seconds")
            print(f"Next Green Light Lane: {self.next_green_lane.capitalize()}")

    def close(self):
        pass
