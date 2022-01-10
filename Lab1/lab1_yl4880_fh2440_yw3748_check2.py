#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from machine import Pin
import utime

builtin_light = Pin(0, Pin.OUT)
antenna_light = Pin(2, Pin.OUT)
builtin_light.value(1)
antenna_light.value(1)

def turn_on_100ms():
    for i in range(4):
        antenna_light.value(0)
        utime.sleep(0.1)
        antenna_light.value(1)
        utime.sleep(0.1)
        
def turn_on_500ms():
    builtin_light.value(0)
    antenna_light.value(0)
    utime.sleep(0.1)
    builtin_light.value(1)
    antenna_light.value(1)
    utime.sleep(0.1)
    

while True:
    turn_on_500ms()
    turn_on_100ms()

