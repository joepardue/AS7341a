# AS7341 Spectroradiometer (as7341sr.py) Joe Pardue 11/20/23
# Some of this code is derived from examples provided by Adafruit.com

# ## Import libraries ##
import time
import board
import storage
import busio
import sdcardio
import digitalio
import adafruit_pcf8523
from adafruit_as7341 import AS7341

# ## Setup ##
# ###########

# setup pushbuttons
button1 = digitalio.DigitalInOut(board.GP20)
button1.switch_to_input(pull=digitalio.Pull.DOWN)
button2 = digitalio.DigitalInOut(board.GP21)
button2.switch_to_input(pull=digitalio.Pull.DOWN)

# setup I2C bus for Adafruit sensors  for using
# the built-in STEMMA QT connector on a microcontroller
i2c = board.STEMMA_I2C()

# setup ulti spectral light sensor
sensor = AS7341(i2c)

# setup for RTC
rtc = adafruit_pcf8523.PCF8523(i2c)

# #setup date/time on Adafruit PicowBell#

#  list of days to print to the text file on boot
days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

# SPI SD_CS pin
SD_CS = board.GP17

#  SPI setup for SD card
spi = busio.SPI(board.GP18, board.GP19, board.GP16)
sdcard = sdcardio.SDCard(spi, SD_CS)
vfs = storage.VfsFat(sdcard)
try:
    storage.mount(vfs, "/sd")
    print("sd card mounted")
except ValueError:
    print("no SD card")

#  to update the RTC, change set_clock to True
#  otherwise RTC will remain set
#  it should only be needed after the initial set
#  if you've removed the coincell battery
set_clock = False

if set_clock:
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    t = time.struct_time((2023,  3,   6,   00,  00,  00,    0,   -1,    -1))

    print("Setting time to:", t)
    rtc.datetime = t
    print()

#  variable to hold RTC datetime
t = rtc.datetime

time.sleep(1)

#  initial write to the SD card on startup
try:
    with open("/sd/temp.txt", "a") as f:
        #  writes the date
        f.write('The date is {} {}/{}/{}\n'.format(days[t.tm_wday], t.tm_mon, t.tm_mday, t.tm_year))
        #  writes the start time
        f.write('Start time: {}:{}:{}\n'.format(t.tm_hour, t.tm_min, t.tm_sec))
        #  headers for data, comma-delimited
        f.write('Temp,Time\n')
        #  debug statement for REPL
        print("initial write to SD card complete, starting to log")
except ValueError:
    print("initial write to SD card failed - check card")

def bar_graph(read_value):
    scaled = int(read_value / 1000)
    # return "[%5d] " % read_value + (scaled * "*")
    return "%d" % read_value + (scaled * "*")

# f.flush()
# Write first row of .csv file
with open("/sd/csvtest.txt", "a") as f:
    #  writes the date
    f.write('The date is {} {}/{}/{}\n'.format(days[t.tm_wday], t.tm_mon, t.tm_mday, t.tm_year))
    f.write("hour, min, sec, nm415, nm445, nm480, nm515, nm555, nm590, nm630, nm680, Clear, NIR"+"\n")
    print("hour, min, sec, nm415, nm445, nm480, nm515, nm555, nm590, nm630, nm680, Clear, NIR\n")


while True:
    if button1.value == 1:
        print("Button 1 pressed\n")
    # if button2.value == 1:
        #print("Button 2 pressed\n")
        try:
            #  variable for RTC datetime
            t = rtc.datetime
            # sensor values
            nm415 = sensor.channel_415nm
            nm445 = sensor.channel_445nm
            nm480 = sensor.channel_480nm
            nm515 = sensor.channel_515nm
            nm555 = sensor.channel_555nm
            nm590 = sensor.channel_590nm
            nm630 = sensor.channel_630nm
            nm680 = sensor.channel_680nm
            Clear = sensor.channel_clear
            NIR = sensor.channel_nir

            #  append SD card text file
            with open("/sd/csvtest.txt", "a") as f:
                f.write('{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(t.tm_hour,
                t.tm_min, t.tm_sec, nm415, nm445, nm480, nm515, nm555, nm590, nm630, nm680, Clear, NIR))
                print('{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(t.tm_hour, t.tm_min, t.tm_sec,
                nm415, nm445, nm480, nm515, nm555, nm590, nm630, nm680, Clear, NIR))
                print("data written to sd card")
            #  repeat every 5 seconds
            # time.sleep(5)
        except ValueError:
            print("data error - cannot write to SD card")
            # time.sleep(10)
