#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from machine import Pin, Timer
import utime

interrupt_disabled = False
def debounce(pin):
    global switch, interrupt_disabled
    if not interrupt_disabled:
        switch.irq(trigger=0)
        interrupt_disabled = True
        tim = Timer(-1)
        print("timer registered")
        tim.init(period=100, mode=Timer.ONE_SHOT, callback=toggle)
    

def toggle(void):
    global interrupt_disabled
    p12.value(not p12.value())
    switch.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=debounce)
    interrupt_disabled = False
    print("toggle")
    
    
switch = Pin(13, Pin.IN, Pin.PULL_UP)
p12 = Pin(12, Pin.OUT)
p12.off()

switch.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=debounce)



