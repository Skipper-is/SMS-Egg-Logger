from machine import Pin, I2C, UART
import utime


class Phone:

    def __init__(self):

        self.uart = UART(1, baudrate=9600, bits=8, parity=None, stop=1, tx=27, rx=26)
        self.powerBoost()
        self.powerOn()
        self.reset()
        self.cyclePower()
        self.sendCommand("AT")  # The first AT signal sets up auto bauding, so the SIM800 can figure out what speed we're working at
        utime.sleep_ms(2500)  # Give it a little bit to figure out what is going on, and wake up
        self.sendCommand("AT")  # Another At just to verify, should get an OK back from this one
        utime.sleep_ms(100)  # Little break between the commands.. Though actually sendCommand also has a break
        self.sendCommand("AT+CMGF=1")  # Set the SIM into SMS Text mode.
        utime.sleep_ms(100)
        self.sendCommand('AT+CNMI=1,2,0,0,0')  # Set Text message modes: 1 = reject messages when not linked to device
        # the 2 - all incoming messages are routed to the ESP32/serial
        # Next 0 - Cell Broadcast Messages, don't forward them
        # Next 0 - Dont send SMS-Status Reports - Could change this in future, to verify that responses are sent to the senders... Or not
        # Next 0 - When changing the mode, the result codes will be flushed
        # The sim800 should be all awake and ready now, new messages will be stored on the Serial buffer, and can be fetched with readAll()

    def sendCommand(self, command):
        self.uart.write(command + '\r\n')  # Send the command, followed by CR/NL
        utime.sleep_ms(500)  # Give it a few moments to process
        return self.uart.read()  # And send back what was said - This will read back everything that is sitting on the buffer too

    def silentCommand(self, command):
        self.uart.write(command + '\r\n')
        utime.sleep_ms(100)  # This is the silent command function - sends a command, but doesn't listen for a response
        # The response will still come, but it'll sit on the buffer until you readAll(), or sendCommand()

    def readAll(self):
        return self.uart.read()

    def sendText(self, number, message):  # Pretty self evident this one....
        self.sendCommand("AT+CMGF=1")  # Just make sure it is in sms mode
        self.sendCommand('AT+CSCS="GSM"')
        self.sendCommand('AT+CMGS="' + number + '"')  # CMGS - Send a message! Plus the number - NUMBERS NEED TO INCLUDE COUNTRY CODE! eg: +44123456789
        self.sendCommand(message)  # And the message!
        self.uart.write(b'\x1A')  # This had to be sent as a 'write' command, as it is an escape character
        utime.sleep_ms(100)
        self.uart.read()

    def powerBoost(self):
        # The power boost is an I2C buck converter - the SIM800L can draw up to 2A during transmission, and runs on a weird voltage
        i2c = I2C(scl=Pin(22), sda=Pin(21))
        i2c.writeto_mem(0x75, 0x00, b'\x37')
        i2c.stop()

    def powerOn(self):
        # Power on the device!
        powerOn = Pin(23, Pin.OUT)
        powerOn.value(1)

    def reset(self):
        # For some reason, the SIM800L module wants a very rapid reset.. It isn't a full reset, as that is
        # held low for 1000ms, this is just flash it low and then high agian.. If it works eh?
        rst = Pin(14, Pin.OUT)
        rst.value(1)
        utime.sleep_ms(1)
        rst.value(0)
        utime.sleep_ms(1)
        rst.value(1)
        utime.sleep_ms(10)

    def cyclePower(self):
        # Weird one this, the sim800 module just seems to want the power cycled after the reset...
        # And this is a different pin... Pwkey and powerOn...I've no idea, I don't make the devices
        pwkey = Pin(15, Pin.OUT)
        pwkey.value(1)
        utime.sleep_ms(500)
        pwkey.value(0)
        utime.sleep_ms(1000)
        pwkey.value(1)
        utime.sleep_ms(500)
