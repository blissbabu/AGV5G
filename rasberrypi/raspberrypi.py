import serial
import socket
import time
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Joy
import socket
import json
import select
import time
import serial
from struct import pack
from struct import unpack
from timeit import default_timer as timer
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
# Bind the socket to the port
server_address = ('',9090)
#print('Starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

joyPub = rospy.Publisher( 'joy_arm', Joy, queue_size=10)

rospy.init_node('joy_arm_interface', anonymous=True)

def u2d2(message):
    joyMsg = Joy()
    joyMsg.axes = [ 0,0,0,0,0,0]

    if message=="ARM_REST":
        arm_activate(joyMsg)
        time.sleep(1)
        arm_rest_position(joyMsg)
    elif message=="ARM_START":
        arm_activate(joyMsg)
        time.sleep(1)
        arm_start_position(joyMsg)
    elif message=="ARM_PICK":
        arm_activate(joyMsg)
        time.sleep(1)
        arm_gripper_open(joyMsg)
        time.sleep( 1)
        arm_pick_position(joyMsg)
    elif message=="ARM_DROP":
        arm_activate(joyMsg)
        time.sleep(1)
        arm_pick_position(joyMsg)
        time.sleep(1)
        arm_gripper_open(joyMsg)
    elif message=="ARM_OPEN":
        arm_activate(joyMsg)
        time.sleep(1)
        arm_gripper_open(joyMsg)
    elif message=="ARM_CLOSE":
        arm_activate(joyMsg)
        time.sleep(1)
        arm_gripper_close(joyMsg)
        

def arm_activate(joyMsg):
    joyMsg.buttons = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    joyPub.publish( joyMsg )
    print (joyMsg)
    print("ARM Activated")
def arm_start_position(joyMsg):
    joyMsg.buttons = [0, 0, 0, 0, 0, 0, 0, 0,1, 0, 0, 0]
    joyPub.publish( joyMsg )
    print (joyMsg)
    print("START Position")
def arm_pick_position(joyMsg):
    joyMsg.buttons = [0, 0, 0, 0, 0, 0, 0, 0,0, 1, 0, 0]
    joyPub.publish( joyMsg )
    print (joyMsg)
    print("PICK Position")
def arm_rest_position(joyMsg):
    joyMsg.buttons = [0, 0, 0, 0, 0, 0, 1, 0,0, 0, 0, 0]
    joyPub.publish( joyMsg )
    print (joyMsg)
    print("REST Position")
def arm_gripper_open(joyMsg):
    joyMsg.buttons = [0, 1, 0, 0, 0, 0, 0, 0,0, 0, 0, 0]
    joyPub.publish( joyMsg )
    print (joyMsg)
    print("Gripper Open")
def arm_gripper_close(joyMsg):
    joyMsg.buttons = [1, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0]
    joyPub.publish( joyMsg )
    print (joyMsg)
    print("Gripper Close")


def split_recieved_message(message, delimiter):
    parts = message.split(delimiter)
    if len(parts) >= 2:
        part1, part2= parts[:2]
        return part1, part2
    else:
        return None, None, None, None,None

def send_to_arduino(message):

    ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)
    ser.reset_input_buffer()
    
    # delimeter='_'
    # DeviceID,direction,speed,parameter,counter=split_recieved_message(message,delimeter)
    # print(DeviceID,direction,speed,parameter,counter)
    
    command=(str(message))
    print("command sent to arduino: ",command)
    ser.write(bytes(command+'\n', encoding='utf-8'))
    line = ser.readline().decode('utf-8').rstrip()
    print("recieved by arduino:",line)
    time.sleep(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1024)
            message = data.decode("utf-8")
            print('recieved from client:',(message))

            if data:
                print('sending data back to the client')
                connection.sendall(bytes( message, encoding="utf-8" ) )
                if message!='ALIVE':
                    delimeter='_'
                    device=split_recieved_message(message,delimeter)
                    print(device[0])
                    if device[0]=="ARM":
                        u2d2(message)
                        print("Sending to ARM")
                    else:
                        print("Sending to Arduino")
                        send_to_arduino(message)
            else:
                print('no data from', client_address)
                break

    finally:
        # Clean up the connection
        print("Closing current connection")
        connection.close()


