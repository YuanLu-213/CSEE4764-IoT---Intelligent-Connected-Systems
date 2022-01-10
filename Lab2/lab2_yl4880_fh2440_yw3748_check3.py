#!/usr/bin/env python
# coding: utf-8

# In[3]:


from machine import Pin, PWM, Timer
from machine import ADC
import utime

interrupt_disabled = False
sensor_enabled = False

def debounce(pin):
    global switch, interrupt_disabled
    if not interrupt_disabled:
        switch.irq(trigger=0)
        interrupt_disabled = True
        tim = Timer(-1)
        print("timer registered")
        tim.init(period=100, mode=Timer.ONE_SHOT, callback=toggle)
        
def toggle(void):
    global interrupt_disabled, sensor_enabled
    sensor_enabled = not sensor_enabled
    switch.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=debounce)
    interrupt_disabled = False

        
switch = Pin(13, Pin.IN, Pin.PULL_UP)
p12 = Pin(12, Pin.OUT)
p14 = Pin(14, Pin.OUT)
p12.off()
p14.off()
adc = ADC(0) 
pwm12 = PWM(Pin(12), 1000, 0)
pwm14 = PWM(Pin(14), 1000, 512)

switch.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=debounce)

while True:
    if sensor_enabled == False:
        pwm12.duty(0)
        pwm14.freq(0)
    else: 
        value = adc.read()
        print(value)
        pwm12.duty(value)
        pwm14.freq(value)
    utime.sleep_ms(50)
        
   
