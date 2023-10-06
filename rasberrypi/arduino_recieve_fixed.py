#arduino reviecing fixed
import serial
import socket
import time
# Set up the serial connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('',9090)
#print('Starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)


arduino = serial.Serial('/dev/ttyUSB0', baudrate=9600)
def send_message_to_arduino(message): 
   # Add a newline character to the message 
    message_with_newline = message + "\n"   
       # Send the message to Arduino   
    arduino.write(message_with_newline.encode())  
    print("Message sent to Arduino:", message)
try:  
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

            # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(64)
            message = data.decode("utf-8")
            print('recieved',(message))

            if data:
                print('sending data back to the client')
                connection.sendall(bytes( message, encoding="utf-8" ) )
                if message!='ALIVE':
                    send_message_to_arduino(message)
                else:
                    print('no data from', client_address)
                    break

    finally:
        # Clean up the connection
        print("Closing current connection")
        connection.close()

except KeyboardInterrupt: 
    pass
finally:   
                                  # Close the serial connection  
    arduino.close()
