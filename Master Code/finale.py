# Adafruit MMA8451 Accelerometer code
import time
import math

import board
import busio

import adafruit_mma8451

import numpy as np
import mysql.connector


#one second delay
time.sleep(1)

from pyax12.connection import Connection
from pyax12.packet import Packet
from time import sleep


# Initialize I2C bus.
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize MMA8451 module.
sensor = adafruit_mma8451.MMA8451(i2c)


# Variables for velocity calculation
# previous value
x_pre = 0
y_pre = 0
z_pre = 0

# current value
x_curr = 0
y_curr = 0
z_curr = 0

x2 = 0
y2 = 0
z2 = 0

#distance traveled by acclerometer
dist = 0

#velocity recorded by acclerometer
velocity = 0

#pulse of accelerometer recordings
t = 0.5

#list of velocity recordings during one movement
vel_arr = []

#number of leg steps taken
leg_incr = 1


serial_connection = Connection(port="/dev/ttyUSB0" , baudrate = 1000000)

#artificial neural network
class NeuralNetwork():

    def __init__(self):
        # create seed for random number generation
        np.random.seed(1)

        # convert weights to a 3 by 1 matrix with values from -1 to 1 and mean of 0
        self.synaptic_weights = 2 * np.random.random((3,1)) - 1

    def sigmoid(self, x):
        #sigmoid function
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        # compute derivative of Sigmoid function
        return x * (1 - x)

    def train(self, training_inputs, training_outputs, training_iterations):
        # training the model to make accurate predictions while adjusting weights continually
        for iteration in range(training_iterations):
            # create training data through the neuron
            output = self.learn(training_inputs)

            # compute error rate for back-propagation
            error = training_outputs - output

            # perform weight adjustments
            adjustments = np.dot(training_inputs.T, error * self.sigmoid_derivative(output))

            self.synaptic_weights += adjustments

    def learn(self, inputs):
        # pass the inputs through the neuron to get output
        # convert values to floats

        inputs = inputs.astype(float)
        output = self.sigmoid(np.dot(inputs, self.synaptic_weights))
        return output
    
#--------------------------------------------------------------------------------
# Remote Web App
# uploads data to SQL database to be outputted through php web app
def insert_variables_into_table(movement_duration, avg_velocity, date):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='performance',
                                             user='logger',
                                             password='donwonath')
        cursor = connection.cursor()
        mySql_insert_query = """INSERT INTO performancedata (Movement_Duration, Avg_Velocity, Date) 
                                VALUES (%s, %s, %s) """

        record = (movement_duration, avg_velocity, date)
        cursor.execute(mySql_insert_query, record)
        connection.commit()
        print("Record inserted successfully into performance table")

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
#--------------------------------------------------------------------------------

#function used to convert data into a readable TTL packet for servo communication
def packetGen(dataLength, ID1, ID2, angle1, mov_speed1, angle2, mov_speed2):
    #hexSplit variablaes compensate for the data lost when converting raw decimal values into hex.
    #Depending on the range of values, the hexSplit value must match accordingly for accurate mapping within the byte word
    hexSplit1 = 0
    hexSplit2 = 0
    hexSplit3 = 0
    hexSplit4 = 0
    
    #test for angle1
    #manipulate 
    if angle1 < 256:
        hexSplit1 = 0
    elif angle1 >= 512 and angle1 < 768: # 512-767
        angle1 = angle1 - 512
        hexSplit1 = 2
    elif angle1 >= 768 and angle1 < 1024: # 768-1023
        angle1 = angle1 - 768
        hexSplit1 = 3
    else: #256-511
        angle1 = angle1 - 256
        hexSplit1 = 1
    
    if mov_speed1 < 256:
        hexSplit2 = 0
    elif mov_speed1 >= 512 and mov_speed1 < 768:
        mov_speed1 = mov_speed1 - 512
        hexSplit2 = 2
    elif mov_speed1 >= 768 and mov_speed1 < 1024: # 768-1023
        mov_speed1 = mov_speed1 - 768
        hexSplit2 = 3
        #can also compensate for angles above 768 but implement later
    else:
        mov_speed1 = mov_speed1 - 256
        hexSplit2 = 1
    
    if angle2 < 256:
        hexSplit3 = 0
    elif angle2 >= 512 and angle2 < 768:
        angle2 = angle2 - 512
        hexSplit3 = 2
    elif angle2 >= 768 and angle2 < 1024: # 768-1023
        angle2 = angle2 - 768
        hexSplit13 = 3
        #can also compensate for angles above 768 but implement later
    else:
        angle2 = angle2 - 256
        hexSplit3 = 1
    
    if mov_speed2 < 256:
        hexSplit4 = 0
    elif mov_speed2 >= 512 and mov_speed2 < 768:
        mov_speed2 = mov_speed2 - 512
        hexSplit4 = 2
    elif mov_speed2 >= 768 and mov_speed2 < 1024: # 768-1023
        mov_speed2 = mov_speed2 - 768
        hexSplit14 = 3
        #can also compensate for angles above 768 but implement later
    else:
        mov_speed2 = mov_speed2 - 256
        hexSplit4 = 1
    
    #check to see if any of the data values can be generated with only two bytes
    #iterate and build the packet with a for loop
    return [131, 30, dataLength, ID1, angle1, hexSplit1, mov_speed1, hexSplit2, ID2,angle2, hexSplit3, mov_speed2, hexSplit4]  

def origPos():
    ID1 = 0 #right leg hip
    ID2 = 2 #right leg knee
    ID3 = 3 #left leg hip
    ID4 = 10 #left leg knee
    
    angle1 = 300 #right leg hip position
    angle2 = 300 #right leg knee position
    angle3 = 724 #left leg hip position
    angle4 = 724 #left leg knee position
    
    
    mov_speed = 200
    
    data = 4
    
    temp_lst1 = packetGen(data, ID1, ID2, angle1, mov_speed, angle2, mov_speed)
    temp_pkt1 = Packet(254,temp_lst1)
    serial_connection.send(temp_pkt1)
    #sleep(1)
    temp_lst2 = packetGen(data, ID3, ID4, angle3, mov_speed, angle4, mov_speed)
    temp_pkt2 = Packet(254,temp_lst2)
    serial_connection.send(temp_pkt2)


def rOrigPos(spdh,spdk):
    ID1 = 0 #right leg hip
    ID2 = 2 #right leg knee
    
    angle1 = 300 #right leg hip position
    angle2 = 300 #right leg knee position
    
    data = 4
    
    temp_lst1 = packetGen(data, ID1, ID2, angle1, spdh, angle2, spdk)
    temp_pkt1 = Packet(254,temp_lst1)
    serial_connection.send(temp_pkt1)


def lOrigPos(spdh,spdk):
    ID3 = 3 #left leg hip
    ID4 = 10 #left leg knee

    angle3 = 724 #left leg hip position
    angle4 = 724 #left leg knee position
    

    
    data = 4
    
    temp_lst2 = packetGen(data, ID3, ID4, angle3, spdh, angle4, spdk)
    temp_pkt2 = Packet(254,temp_lst2)
    serial_connection.send(temp_pkt2)

def rStepSeq(angle1, mov_speed, angle2, mov_speed2):
    ID1 = 0 #right leg hip
    ID2 = 2 #right leg knee
    

    data = 4
    
    temp_lst1 = packetGen(data, ID1, ID2, angle1, mov_speed, angle2, mov_speed2)
    temp_pkt1 = Packet(254,temp_lst1)
    serial_connection.send(temp_pkt1)
    
    
def lStepSeq(angle3, mov_speed, angle4, mov_speed2):
    ID3 = 3 #right leg hip
    ID4 = 10 #right leg knee
    
  
    data = 4
    
    temp_lst2 = packetGen(data, ID3, ID4, angle3, mov_speed, angle4, mov_speed2)
    temp_pkt2 = Packet(254,temp_lst2)
    serial_connection.send(temp_pkt2)
    
    
    
userIn = 0

# Main loop to print the acceleration and orientation every second, stops after 100 iterations
while userIn < 100:
    #indicates  acceleromter is ready to record values
    print('movement ready')
    userIn += 1
    x, y, z = sensor.acceleration
    #print('Acceleration: x={0:0.3f}m/s^2 y={1:0.3f}m/s^2 z={2:0.3f}m/s^2'.format(x, y, z))
    
    
    x_pre = x_curr
    y_pre = y_curr
    z_pre = z_curr

    x_curr = x
    y_curr = y
    z_curr = z
    
    x2 = (x_curr - x_pre) ** 2
    y2 = (y_curr - y_pre) ** 2
    z2 = (z_curr - z_pre) ** 2

    dist = math.sqrt(x2 + y2 + z2)
    
    #velocity at every 0.5 seconds
    velocity = dist / t
    
    #adds to array if accelerometer reads a velocity value 
    if velocity > 1:
        vel_arr.append(velocity)

    
    #print('Velocity: {0:0.3f}m/s'.format(velocity))
    #print(len(vel_arr))
    time.sleep(t)


    
    #check to see if the movement has ended and is a reasonable amount of elements withing the array
    if velocity < 1 and len(vel_arr) > 2:
        leg_incr = leg_incr + 1
        avg_vel = sum(vel_arr)/len(vel_arr)

        print('Average Velocity of Overall Movement: {0:0.3f} m/s'.format(avg_vel))
        print('Length of Movement: {0:0.1f} s'.format(len(vel_arr)/2))

        insert_variables_into_table(len(vel_arr), avg_vel, '2021-03-07')
        
        
        #clear the list of array of velocity for next movement
        vel_arr.clear()

        #Neural Network
        # initializing the neuron class
        neural_network = NeuralNetwork()

        print("Beginning Randomly Generated Weights: ")
        print(neural_network.synaptic_weights)

        # training data 
        training_inputs = np.array([[0, 0, 0],
                                    [0, 1, 0],
                                    [0, 0, 1],
                                    [0, 1, 1],
                                    [1, 0, 0],
                                    [1, 1, 0],
                                    [1, 0, 1],
                                    [1, 1, 1]])

        training_outputs_one = np.array([[0, 0, 0, 0, 0, 1, 1, 0]]).T

        # training taking place
        neural_network.train(training_inputs, training_outputs_one, 15000)

        if (leg_incr % 2) == 0:         #right front leg moves
            user_input_one = 1
            user_input_two = 1
            user_input_three = 0
        else:
            user_input_one = 1          #left front leg moves
            user_input_two = 0
            user_input_three = 1



        print("Considering New Situation: ", user_input_one, user_input_two, user_input_three)
        print("New Output data: ")
        print(neural_network.learn(np.array([user_input_one, user_input_two, user_input_three])))
        
        output = neural_network.learn(np.array([user_input_one, user_input_two, user_input_three]))
        
        print("Wow, we did it!")
        
        spdh = int((round(avg_vel,0)*13) + 100)
        spdk = int((round(avg_vel,0)*13) + 250)
        s= ((round(avg_vel,0)*-0.04) + 1)
        if avg_vel >= 25:
            s= 0.2
        
        print(spdh)
        print(spdk)
        print(s)
        #left sequence
        if user_input_one == 1 and user_input_two == 0 and user_input_three == 1:  
            #s = 0.5
            #spdh = 150
            #spdk = 300
            lStepSeq(512,spdh,760,spdk)
            sleep(s)
            rStepSeq(0,spdh,460,spdk)
            sleep(0.2)
            lOrigPos(spdh,spdk)
            #sleep(s)
            rStepSeq(512,spdh,264,spdk)
            sleep(s)
            rOrigPos(spdh,spdk)
            sleep(5)
            origPos()
            
        #right sequence
        elif user_input_one == 1 and user_input_two == 1 and user_input_three == 0:
            #s = 0.5
            #spdh = 150
            #spdk = 300
            rStepSeq(512,spdh,264,spdk)
            sleep(s)
            lStepSeq(1023,spdh,580,spdk)
            sleep(0.2)
            rOrigPos(spdh,spdk)
            #sleep(s)
            lStepSeq(512,spdh,700,spdk)
            sleep(s)
            lOrigPos(spdh,spdk)
            sleep(5)
            origPos()
 
        
serial_connection.close()





