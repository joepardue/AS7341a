# AS7341 Spectroradiometer (as7341sr.py) Joe Pardue 11/20/23
# Some of this code is derived from examples provided by Adafruit.com

import time
import board
import storage
import busio
import sdcardio
import digitalio
import adafruit_pcf8523
from adafruit_as7341 import AS7341

# Constants
SD_FILENAME = "/sd/csvtest.txt"
INITIAL_WRITE_MSG = "initial write to SD card complete, starting to log"
INITIAL_WRITE_ERR_MSG = "initial write to SD card failed - check card"
DATA_ERR_MSG = "data error - cannot write to SD card"
RTC_SET_TIME = (2023, 3, 6, 0, 0, 0, 0, -1, -1)
WRITE_INTERVAL = 5  # Time interval in seconds between writes to the SD card

# Setup pushbuttons
def setup_buttons():
    button1 = digitalio.DigitalInOut(board.GP20)
    button1.switch_to_input(pull=digitalio.Pull.DOWN)
    button2 = digitalio.DigitalInOut(board.GP21)
    button2.switch_to_input(pull=digitalio.Pull.DOWN)
    return button1, button2

# Setup I2C bus and sensors
def setup_sensors():
    i2c = board.STEMMA_I2C()
    sensor = AS7341(i2c)
    rtc = adafruit_pcf8523.PCF8523(i2c)
    return sensor, rtc

# Setup SD card
def setup_sd_card():
    sd_cs = board.GP17
    spi = busio.SPI(board.GP18, board.GP19, board.GP16)
    sdcard = sdcardio.SDCard(spi, sd_cs)
    vfs = storage.VfsFat(sdcard)
    try:
        storage.mount(vfs, "/sd")
        print("SD card mounted")
    except ValueError:
        print("No SD card found")

# Set RTC time
def set_rtc_time(rtc, set_clock=False):
    if set_clock:
        rtc.datetime = time.struct_time(RTC_SET_TIME)
        print(f"Setting time to: {RTC_SET_TIME}")

# Write to SD card
def write_to_sd(data_string):
    try:
        with open(SD_FILENAME, "a") as f:
            f.write(data_string)
    except ValueError:
        print(DATA_ERR_MSG)

# Main loop
def main():
    button1, button2 = setup_buttons()
    sensor, rtc = setup_sensors()
    setup_sd_card()
    set_rtc_time(rtc, set_clock=False)
    
    # Initial write to the SD card on startup
    current_time = rtc.datetime
    days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    initial_data = f'The date is {days[current_time.tm_wday]} {current_time.tm_mon}/{current_time.tm_mday}/{current_time.tm_year}\n'
    initial_data += f'Start time: {current_time.tm_hour}:{current_time.tm_min}:{current_time.tm_sec}\nTemp,Time\n'
    write_to_sd(initial_data)
    
    while True:
        if button1.value:
            print("Button 1 pressed")
            sensor_data = read_sensor_data(sensor)
            time_data = f'{current_time.tm_hour},{current_time.tm_min},{current_time.tm_sec}'
            write_to_sd(f'{time_data},{sensor_data}\n')
            print(f'{time_data},{sensor_data}')
            print("Data written to SD card")
            time.sleep(WRITE_INTERVAL)

def read_sensor_data(sensor):
    return ','.join(str(getattr(sensor, attr)) for attr in [
        'channel_415nm', 'channel_445nm', 'channel_480nm',
        'channel_515nm', 'channel_555nm', 'channel_590nm',
        'channel_630nm', 'channel_680nm', 'channel_clear',
        'channel_nir'
    ])

if __name__ == "__main__":
    main()
