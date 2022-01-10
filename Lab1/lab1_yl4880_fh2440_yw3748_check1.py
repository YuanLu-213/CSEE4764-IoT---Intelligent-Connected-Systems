#!/usr/bin/env python
# coding: utf-8

# In[1]:


from machine import Pin
import utime
builtin_led = Pin(0, Pin.OUT)
antenna_led = Pin(2, Pin.OUT)
builtin_led.value(1)
antenna_led.value(1)

def S_letter():
    for i in range(3):
        builtin_led.value(not builtin_led.value())
        utime.sleep(0.3)
        builtin_led.value(not builtin_led.value())
        utime.sleep(0.3)

   

def O_letter():
    for j in range(3):
        builtin_led.value(not builtin_led.value())
        utime.sleep(0.6)
        builtin_led.value(not builtin_led.value())
        utime.sleep(0.3)

while True:
    S_letter()
    O_letter()
    S_letter()
    builtin_led.value(1)
    utime.sleep(1.5)

