from stable_baselines3 import PPO
from traffic_env import TrafficEnv


def test_model(vehical_count):
    
    model = PPO.load('ppo_traffic_4_way')
    env = TrafficEnv(4)  
    obs = env.reset()
    

    action, _states = model.predict(obs)
    vehicle_counts = vehical_count
    env.set_vehicles(*vehicle_counts)
    obs, rewards, done, info = env.step(action)
    # print(f"Action Taken: {action}")
    print(f"Green Signal Order: {info['green_signal_order']}")
    obs=obs/3
    obs2 = [round(val) for val in obs]
    print(f"Update Lane Times: {obs2}")




test_model([1,30,70,40])
