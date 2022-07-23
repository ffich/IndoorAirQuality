## IndoorAirQuality
Public repo for Indoor Air quality made for Elettronica In.

## What's this
The Indoor Air Quality project is a simple ESP32 based device intended for acquirign and collecting Air quality data inside buildings like schools and offices, in order to have an indication that highlight the needs for air refresh. This is particularly useful for COVID infection prevention. The working principle is quite simple: the board can be configured with an user-defined CO2 threshold that indciated the maximum allowed CO2 concentration. Once this threshold is reached, the board will show a message on the display and turn on a red LED that indicated the need for an air refresh (e.g. open windows). Once the CO2 concentration falls back to an acceptable level, the red LED is turned off and a green one i light up (is possible to close the windows).

## HW details
The core of the system is the WiFi kit 32 a nice development board made by Heltec and available on futurashop at the following link:
[https://futuranet.it/prodotto/modulo-esp32-con-display-oled-096/](https://futuranet.it/prodotto/modulo-esp32-con-display-oled-096/)

The board has the following characteristics:

- Display OLED blu da 0,96” 
- Microcontrollor Dual-Core Tensilica LX6 a 32 bit
- Clock up to240 MHz
- 520 kB internal SRAM
- 32 MB internal flash
- Integarted Wi-Fi 802.11 b/g/n 
- Integarted dual-mode Bluetooth  
- Power supply from 3,3 V to 7 V
- 28 GPIO 
- Integrated LiPo battery charger
- Operating temperature from -40°C to +90°C

The WiFi kit 32 is connected to the SGP30, an indoor air quality sensor from sensirion, capable of reading Co2 and TVOC concentration. Thi sensor is also available in a confortable 4-pin breakout board from futurashop at the following link: [https://futuranet.it/prodotto/breakout-con-sensore-qualita-dellaria-sgp30/](https://futuranet.it/prodotto/breakout-con-sensore-qualita-dellaria-sgp30/)

## Wiring
The wiring between the WiFi Kit 32 and the SGP30 breakout is quite simple as the sensor got an i2c interface and thus it needs just SDA and SCL to be connected, plus power and groud. Additionally you need to foresee two additional connectio for green ad red LED.

The table below resumes the connection between the two boards:

|      Function      |      Pins      |
|--------------------|:--------------:|
| SDA                | 19             |
| SCL                | 18             |
| Ground             | GND            |
| 3,3V               | 3V3            |
| Green LED          | 17             |
| Red LED            | 16             |

## Tests
I can't access the lab in this period, so I'm really bare-metal testing it. I was nevertheless able to build a small proto and it seems working fine, here are a couple of pictures:

![1](Images/setup)

![2](Images/working)
