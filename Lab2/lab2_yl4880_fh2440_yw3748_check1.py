#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from machine import Pin, PWM
from machine import ADC

p12 = Pin(12, Pin.OUT)
p14 = Pin(14, Pin.OUT)
pwm12 = PWM(Pin(12))
pwm14 = PWM(Pin(14))
pwm12.freq(1000)
pwm14.freq(1000)
adc = ADC(0)

while True:
    value = adc.read()
    pwm12.duty(value)
    pwm14.freq(value)


