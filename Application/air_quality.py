# --------------------------------------------------------------------------------
# - DEPENDENCIES
# --------------------------------------------------------------------------------
import time
from machine import Pin, SoftI2C, I2C
import ssd1306
import adafruit_sgp30

# --------------------------------------------------------------------------------
# - CONST
# --------------------------------------------------------------------------------
CO2_LINE = 20
TVOC_LINE = 40
DEBUG = True

# --------------------------------------------------------------------------------
# - USER TH DEFAULT VALUES
# --------------------------------------------------------------------------------
co2eq_th = 450
hysteresis = 10

# --------------------------------------------------------------------------------
# - TIMING CONST
# --------------------------------------------------------------------------------
SAMPLING_TIME_S = 60
SENS_INIT_DELAY_S = 15

# --------------------------------------------------------------------------------
# - GLOBALS
# --------------------------------------------------------------------------------
has_baseline = False
baseline_time = 0

# --------------------------------------------------------------------------------
# - SERVICE FUNCTIONS
# --------------------------------------------------------------------------------
def user_message(text):
    if DEBUG == True:
        print(text)    
    oled.fill(0)
    oled.text(text, 0, 0)
    oled.show()
    
def oled_data(co2eq, tvoc):
    oled.fill(0)
    oled.text('CO2 Sensor - Ein', 0, 0)
    oled.text('Co2 Eq: ', 0, CO2_LINE)
    oled.text(str(co2eq) + ' ppm', 60, CO2_LINE)    
    oled.text('TVOC: ', 0, TVOC_LINE)
    oled.text(str(tvoc) + ' ppb', 60, TVOC_LINE)
    oled.show() 

def get_sensor_baseline():
    global has_baseline
    
    try:
        # Retrieve previously stored baselines, if any (helps the compensation algorithm).
        f_co2 = open('co2eq_baseline.txt', 'r')
        f_tvoc = open('tvoc_baseline.txt', 'r')
        co2_baseline = int(f_co2.read())
        tvoc_baseline = int(f_tvoc.read())    
        # Use them to calibrate the sensor
        sgp30.set_iaq_baseline(co2_baseline, tvoc_baseline)
        f_co2.close()
        f_tvoc.close()
        has_baseline = True
        user_message('Baseline Set')        
    except:
        user_message('No baseline')    
        
    time.sleep(2)
    
def update_sensor_baseline():
    global has_baseline
    global baseline_time
    
    # Baselines should be saved after 12 hour the first time then every hour, according to the doc
    if (has_baseline and (time.time() - baseline_time >= (3600/SAMPLING_TIME_S))) \
            or ((not has_baseline) and (time.time() - baseline_time >= (43200/SAMPLING_TIME_S))):        
        user_message('Baseline Set')      
        baseline_time = time.time()

        try:
            f_co2 = open('co2eq_baseline.txt', 'w')
            f_tvoc = open('tvoc_baseline.txt', 'w')
            bl_co2, bl_tvoc = sgp30.get_iaq_baseline()
            f_co2.write(str(bl_co2))
            f_tvoc.write(str(bl_tvoc))
            f_co2.close()
            f_tvoc.close()
            has_baseline = True
        except:
            user_message('No baseline')    
    
def get_user_threshold():
    global co2eq_th
    global hysteresis
    
    try:
        # Get the Threshold fro CO2
        f_co2_th = open('co2eq_th.txt', 'r')
        f_hysteresis = open('hist_th.txt', 'r')
        co2eq_th = int(f_co2_th.read())
        hysteresis = int(f_hysteresis.read())
        f_co2_th.close()
        f_hysteresis.close()
        user_message('User Th set')
    except:        
        user_message('No user Th')
    
    time.sleep(2)
    
# --------------------------------------------------------------------------------
# - SYSTEM INIT
# --------------------------------------------------------------------------------

# LEDs
led_green = Pin(17, Pin.OUT)
led_red = Pin(16, Pin.OUT)
led_green.on()
led_red.off()

# Initialize I2C buses
s_i2c = I2C(scl=Pin(18), sda=Pin(19), freq=100000)
d_i2c = SoftI2C(scl=Pin(15), sda=Pin(4), freq=100000)

# OLED enable pin
oled_sts = Pin(16, Pin.OUT)
oled_sts.on()

# OLED initialization
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, d_i2c)

# Air quality sensor init
sgp30 = adafruit_sgp30.Adafruit_SGP30(s_i2c)

# Initialize SGP-30 internal drift compensation algorithm.
sgp30.iaq_init()

# Wait 15 seconds for the SGP30 to properly initialize
user_message('Sensor Init...')
time.sleep(SENS_INIT_DELAY_S)

# User threshold for LEDs indication
get_user_threshold()

# Sensor Calibration
get_sensor_baseline()

# Store the time at which last baseline has been saved
baseline_time = time.time()

# --------------------------------------------------------------------------------
# - MAIN LOOP
# --------------------------------------------------------------------------------
while True:
    # Get CO2 and TVOC data
    co2eq, tvoc = sgp30.iaq_measure()
    
    if DEBUG == True:
        # Print values on REPL
        print('co2eq = ' + str(co2eq) + ' ppm \t tvoc = ' + str(tvoc) + ' ppb')
    
    # Print values on Display
    oled_data(co2eq, tvoc)
    
    # Manage LEDs
    if (co2eq > co2eq_th):
        led_green.off()
        led_red.on()
    elif (co2eq < (co2eq_th - hysteresis)):
        led_green.on()
        led_red.off()        
    
    # Update sensor baseline
    update_sensor_baseline()

    # Wait for the new sampling time
    time.sleep(SAMPLING_TIME_S)