import time
from machine import Pin, SoftI2C, I2C
import ssd1306
import adafruit_sgp30

CO2_Line = 20
Tvoc_Line = 40

# OLED enable pin
oled_sts = Pin(16, Pin.OUT)
oled_sts.on()

# Initialize I2C bus
s_i2c = I2C(scl=Pin(18), sda=Pin(19), freq=100000)
d_i2c = SoftI2C(scl=Pin(15), sda=Pin(4))

# OLED
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, d_i2c)

# Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(s_i2c)

#print("SGP30 serial #", [hex(i) for i in sgp30.serial])

# Initialize SGP-30 internal drift compensation algorithm.
sgp30.iaq_init()

# Wait 15 seconds for the SGP30 to properly initialize
print("Waiting 15 seconds for SGP30 initialization.")

oled.fill(0)
oled.text('Sensor Init...', 0, 0)
oled.show()

time.sleep(15)
# Retrieve previously stored baselines, if any (helps the compensation algorithm).
has_baseline = False
try:
    f_co2 = open('co2eq_baseline.txt', 'r')
    f_tvoc = open('tvoc_baseline.txt', 'r')

    co2_baseline = int(f_co2.read())
    tvoc_baseline = int(f_tvoc.read())
    # Use them to calibrate the sensor
    sgp30.set_iaq_baseline(co2_baseline, tvoc_baseline)

    f_co2.close()
    f_tvoc.close()

    has_baseline = True
except:
    print('Impossible to read SGP30 baselines!')

#Store the time at which last baseline has been saved
baseline_time = time.time()

while True:
    co2eq, tvoc = sgp30.iaq_measure()
    
    # Print on REPL
    print('co2eq = ' + str(co2eq) + ' ppm \t tvoc = ' + str(tvoc) + ' ppb')
    
    # Print on Display
    oled.fill(0)
    oled.text('CO2 Sensor - Ein', 0, 0)
    oled.text('Co2 Eq: ', 0, CO2_Line)
    oled.text(str(co2eq) + ' ppm', 60, CO2_Line)    
    oled.text('TVOC: ', 0, Tvoc_Line)
    oled.text(str(tvoc) + ' ppb', 60, Tvoc_Line)
    oled.show() 

    # Baselines should be saved after 12 hour the first timen then every hour,
    # according to the doc.
    if (has_baseline and (time.time() - baseline_time >= 3600)) \
            or ((not has_baseline) and (time.time() - baseline_time >= 43200)):

        print('Saving baseline!')
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
            print('Impossible to write SGP30 baselines!')

    # A measurement should be done every 60 seconds, according to the doc.
    time.sleep(60)