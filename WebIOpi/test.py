import webiopi
import time
import threading
import pygame
import glob
import random

#Test

webiopi.setDebug()


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

@webiopi.macro
def ChangeTest(TestString):
  return TestString + " awesome"

