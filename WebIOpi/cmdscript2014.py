import webiopi
import time
import threading
import pygame
import glob
import random


#Macro script 2014



# Called by WebIOPi at script loading
def setup():
  # Do nothing
  pass
# Looped by WebIOPi
def loop():
  # Do nothing
  pass

# Called by WebIOPi at server shutdown
def destroy():
  # Do nothing
  pass

# *********************************************************************************
# Macros
# *********************************************************************************
#cmd to test the GPIO expansions
  
@webiopi.macro
def ChangeTest():
  return "new"
