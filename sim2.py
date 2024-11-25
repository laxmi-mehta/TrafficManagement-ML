import random
import time
import threading
import pygame
import sys
import math
from stable_baselines3 import PPO
from traffic_env import TrafficEnv

model = PPO.load('ppo_traffic_4_way')
env = TrafficEnv(4)  
obs = env.reset()
into=0
signalpri=[0,1,2,3]
# Default values of signal timers
defaultGreen = {0: 2, 1: 2, 2: 2, 3: 2}
defaultRed = 150
defaultYellow = 5
signals = []
pendingcc = []
noOfSignals = 4
currentGreen = 0   # Indicates which signal is green currently
nextGreen = (currentGreen + 1) % noOfSignals    # Indicates which signal will turn green next
currentYellow = 0   # Indicates whether yellow signal is on or off 
penmain={
    'right': 0, 'down': 0, 'left': 0, 'up': 0
}
speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike': 2.5}  # average speeds of vehicles

# Coordinates of vehicles' start
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}    
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0}, 
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]

# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Gap between vehicles
stoppingGap = 15    # stopping gap
movingGap = 15   # moving gap

pygame.init()
simulation = pygame.sprite.Group()

# Counter for pending cars in each lane
pendingCars = {'right': [0, 0, 0], 'down': [0, 0, 0], 'left': [0, 0, 0], 'up': [0, 0, 0]}

class TrafficSignal:
    def __init__(self, red, yellow, green):  # add __init__ method
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        vehicles[direction][lane].append(self)
        pendingCars[direction][lane] += 1  # Increment the pending car counter
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.image = pygame.image.load(path)

        if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):    
            # if more than 1 vehicle in the lane and vehicle before it has not crossed the stop line
            if(direction == 'right'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().width - stoppingGap         
            elif(direction == 'left'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().width + stoppingGap
            elif(direction == 'down'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().height - stoppingGap
            elif(direction == 'up'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().height + stoppingGap
        else:
            self.stop = defaultStop[direction]
            
        # Set new starting and stopping coordinate
        if(direction == 'right'):
            temp = self.image.get_rect().width + stoppingGap    
            x[direction][lane] -= temp
        elif(direction == 'left'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif(direction == 'down'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif(direction == 'up'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        if(self.direction == 'right'):
            if(self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]):   
                # if the vehicle has crossed the stop line
                self.crossed = 1
                pendingCars[self.direction][self.lane] -= 1  # Decrement the pending car counter
            if((self.x + self.image.get_rect().width <= self.stop or self.crossed == 1 or (currentGreen == 0 and currentYellow == 0)) and 
               (self.index == 0 or self.x + self.image.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - movingGap))):                
                self.x += self.speed  # move the vehicle
        elif(self.direction == 'down'):
            if(self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]):
                self.crossed = 1
                pendingCars[self.direction][self.lane] -= 1  # Decrement the pending car counter
            if((self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or (currentGreen == 1 and currentYellow == 0)) and 
               (self.index == 0 or self.y + self.image.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - movingGap))):                
                self.y += self.speed
        elif(self.direction == 'left'):
            if(self.crossed == 0 and self.x < stopLines[self.direction]):
                self.crossed = 1
                pendingCars[self.direction][self.lane] -= 1  # Decrement the pending car counter
            if((self.x >= self.stop or self.crossed == 1 or (currentGreen == 2 and currentYellow == 0)) and 
               (self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap))):                
                self.x -= self.speed   
        elif(self.direction == 'up'):
            if(self.crossed == 0 and self.y < stopLines[self.direction]):
                self.crossed = 1
                pendingCars[self.direction][self.lane] -= 1  # Decrement the pending car counter
            if((self.y >= self.stop or self.crossed == 1 or (currentGreen == 3 and currentYellow == 0)) and 
               (self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + movingGap))):                
                self.y -= self.speed

# Initialization of signals with default values
def initialize():
   # penmain
    
   
    global signals, defaultGreen, into,obs,signalpri# Add defaultGreen to the global scope
    
    # Ensure defaultGreen is populated with values
    if not defaultGreen:
        defaultGreen = {0: 1, 1: 1, 1: 1, 3: 1}  # Assign default values if empty or None
        
    
    if into > 0:
        print("call model")
        action, _states = model.predict(obs)
        env.set_vehicles(penmain['right'], penmain['down'], penmain['left'], penmain['up'])
        obs, rewards, done, info = env.step(action)
        signalpri = info['green_signal_order']
        obs=obs/3
        obs2 = [round(val) for val in obs]
        defaultGreen = dict(zip(info['green_signal_order'],obs2))
        print(signalpri)
        print(defaultGreen)
        
        print()
    
    signals = []  # Initialize the signals listd
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
    signals.append(ts4)
    into += 1

    repeat(n=0)

def repeat(n):
    
    global currentGreen, currentYellow, nextGreen
    currentGreen=signalpri[n]
    
    print("  **", signalpri)
    while(signals[currentGreen].green > 0):   # while the timer of current green signal is not zero
        updateValues()
        time.sleep(1)
    currentYellow = 1   # set yellow signal on
    # reset stop coordinates of lanes and vehicles 
    for i in range(0,3):
        
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while(signals[currentGreen].yellow > 0):  # while the timer of current yellow signal is not zero
        updateValues()
        time.sleep(1)
    currentYellow = 0   # set yellow signal off
    
     # reset all signal times of current signal to default times
    signals[currentGreen].green = defaultGreen[currentGreen]
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed
    
    
    
   
   # currentGreen = nextGreen # set next signal as green signal
    nextGreen = (currentGreen + 1) % noOfSignals  # set next green signal
       
    # set the red time of next green signal
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
  
  
    n+=1
    if(n==4):
        initialize()
  
    repeat(n)

# Update values of the signals after every second
def updateValues():
    for i in range(0, noOfSignals):
        if(i == currentGreen):
            if(currentYellow == 0):
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1


def draw_pending_cars(screen, font):
    y_offset = 10 
    for direction in directionNumbers.values():
        v=0
        for lane in range(3):
            v+=pendingCars[direction][lane]
        text = font.render(f"Pending: {v}", True, (255, 255, 255))
        penmain.update({direction:v})
        screen.blit(text, (10 + lane * 150, y_offset + list(directionNumbers.values()).index(direction) * 30))
            
            
# Main code
class Main:
    thread1 = threading.Thread(name="initialization", target=initialize, args=())    # initialization
    thread1.daemon = True
    thread1.start()

    # Colours 
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize 
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/intersection2.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # Vehicle spawning using arrow keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    for i in range(5):
                        Vehicle(lane=random.randint(0, 2), vehicleClass=vehicleTypes[random.randint(0, 3)], direction_number=0, direction='right')
                elif event.key == pygame.K_DOWN:
                    for i in range(5):
                        Vehicle(lane=random.randint(0, 2), vehicleClass=vehicleTypes[random.randint(0, 3)], direction_number=1, direction='down')
                elif event.key == pygame.K_LEFT:
                    for i in range(5):
                        Vehicle(lane=random.randint(0, 2), vehicleClass=vehicleTypes[random.randint(0, 3)], direction_number=2, direction='left')
                elif event.key == pygame.K_UP:
                    for i in range(5):
                        Vehicle(lane=random.randint(0, 2), vehicleClass=vehicleTypes[random.randint(0, 3)], direction_number=3, direction='up')

        screen.blit(background, (0, 0))   # display background in simulation

        # Display signals and their timers
        for i in range(0, noOfSignals):
            if i == currentGreen:
                if currentYellow == 1:
                    signals[i].signalText = signals[i].yellow
                    if signals[i].signalText<0:
                        signals[i].signalText = signals[i].yellow*(-1)
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    signals[i].signalText = signals[i].green
                    if signals[i].signalText<0:
                        signals[i].signalText = signals[i].green*(-1)
                    screen.blit(greenSignal, signalCoods[i])
            else:
                if signals[i].red <= 10:
                    signals[i].signalText = signals[i].red
                    if signals[i].signalText<0:
                        signals[i].signalText = signals[i].red=30
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
        signalTexts = ["", "", "", ""]

        # Display signal timer
        for i in range(0, noOfSignals):  
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])

        # Display the vehicles
        for vehicle in simulation:  
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
       
        draw_pending_cars(screen, font)
        

        pygame.display.update()
