#!/usr/bin/env python
import RPi.GPIO as GPIO
import MFRC522
import signal
import requests
import time
import smbus

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address, if any error, change this address to 0x3f
LCD_WIDTH = 16   # Maximum characters per line

continue_reading = True
URL = "https://controlescolar.tosei.mx/api/index.php"

# function to read uid an conver it to a string

def uidToString(uid):
    mystring = ""
    for i in uid:
        mystring = format(i, '02X') + mystring
    return mystring


# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

GPIO.setmode (GPIO.BOARD)
GPIO.setup(40,GPIO.OUT)#led Verde 1
GPIO.setup(38,GPIO.OUT)#led Rojo 1
GPIO.setup(33,GPIO.OUT)#led Verde 2
GPIO.setup(32,GPIO.OUT)#led Rojo 2
GPIO.setup(36,GPIO.OUT)#buzzer

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print("Welcome to the MFRC522 data read example")
print("Press Ctrl-C to stop.")

# This loop keeps checking for chips.
# If one is near it will get the UID and authenticate
while continue_reading:

    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    lcd_init()
    # If a card is found
    
    if status == MIFAREReader.MI_OK:
        print ("Card detected")
        # Send some test
        lcd_string("Tarjeta detectada",LCD_LINE_1)
        # Get the UID of the card
        (status, uid) = MIFAREReader.MFRC522_SelectTagSN()
        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:
            print("Card read UID: %s" % uidToString(uid))
            number_uid = uidToString(uid)
            #print(number_uid)
            PARAMS = {'tag':number_uid }
            r = requests.get(url = URL, params = PARAMS)
            print(r.text)
            if 'true' in r.text:
                lcd_string(">Autorizado",LCD_LINE_1)
                GPIO.output(40,1)#verde1
                GPIO.output(38,0)#rojo1
                GPIO.output(33,1)#verde2
                GPIO.output(32,0)#rojo2
                GPIO.output(36,1)#buzzer
                time.sleep(.8)
                GPIO.output(36,0)
                GPIO.cleanup
            if 'false' in r.text:
                lcd_string("No autorizado",LCD_LINE_1)
                GPIO.output(40,0)#verde1
                GPIO.output(38,1)#rojo1
                GPIO.output(33,0)#verde2
                GPIO.output(32,1)#rojo2
                GPIO.output(36,1)#buzzer
                time.sleep(.5)
                GPIO.output(36,0)
                time.sleep(.5)
                GPIO.output(36,1)
                time.sleep(.5)
                GPIO.output(36,0)
                time.sleep(.5)
                GPIO.output(36,1)
                time.sleep(.5)
                GPIO.output(36,0)
                GPIO.cleanup
        else:
            print("Authentication error")
            GPIO.output(40,1)
            GPIO.output(38,1)
            GPIO.output(36,1)
            GPIO.output(33,1)#verde2
            GPIO.output(32,1)#rojo2
            time.sleep(.5)
            GPIO.output(36,0)
            time.sleep(.5)
            GPIO.output(36,1)
            time.sleep(.5)
            GPIO.output(36,0)
            time.sleep(.5)
            GPIO.output(36,1)
            time.sleep(.5)
            GPIO.output(36,0)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
