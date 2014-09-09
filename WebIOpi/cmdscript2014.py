import webiopi
import time
import threading
import pygame
import glob
import random
pygame.mixer.init()
from webiopi import deviceInstance

#Macro script 2014
#last fo realz

# Enable debug output
#something

webiopi.setDebug()

# Device setup
GPIO = webiopi.GPIO
relay = deviceInstance("relay")
#io = deviceInstance("io")
pwm = deviceInstance("pwm")
OFF = GPIO.HIGH
ON = GPIO.LOW

#Sound Setup
soundMain = "/home/pi/Hsounds/"
typeOne = "Type1/"
typeTwo = "Type2/"
typeThree = "Type3/"
typeFour = "Type4/"
class SoundStat:
  onBool = False
  def __init__(self):
    pass

Stat = SoundStat()

# Called by WebIOPi at script loading
def setup():
  webiopi.debug("Halloween Macros - Setup")
  # Setup GPIO
  relay.setFunction(0, GPIO.OUT)
  r = 0
  while r < 16:
    relay.setFunction(r, GPIO.OUT)
   # io.setFunction(r, GPIO.OUT)
    r = r + 1
  relayOff()

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
def IOTEST(cmdString):
  testIO()
  return "TEST COMPLETE"
  
@webiopi.macro
def ChangeTest(TestString):
  return TestString + "new"

#Turn all relays on or off
@webiopi.macro
def totalRelay(OnOff):
  if OnOff == "on":
    relayOn()
  else:
    relayOff()

#Recieve command and hand off
@webiopi.macro
def cmd(cmdString):
  #Seperate out commands
  cmdList = cmdString.split(":")
  
  #Send cmd's to handlers
  for cmd in cmdList:
    tempList = cmd.split("=")
    if (tempList[0].upper()) == "IO":
      IOevent(tempList[1])
    elif (tempList[0].upper()) == "RELAY":
      Relayevent(tempList[1])
    elif (tempList[0].upper()) == "RGB":
      RGBevent(tempList[1])
    elif (tempList[0].upper()) == "PWM":
      PWMevent(tempList[1])
    elif (tempList[0].upper()) == "SOUND":
      SoundEvent(tempList[1])
    else:
      webiopi.debug(tempList[0] + " is not a valid command")
      return "ERROR - " + tempList[0] + " is not a valid command"
  
  return str(cmdList)


# *********************************************************************************
# Support Functions
# *********************************************************************************

#*****
# Handler functions
#*****
def IOevent(argString):
  argList = argSplit(argString)
  status = OFF
  if (argList[1].upper() == "ON"): status = ON
  threading.Thread(target=IOthread,args=(argList[0],status,argList[2],argList[3],)).start()

def Relayevent(argString):
  argList = argSplit(argString)
  status = OFF
  if (argList[1].upper() == "ON"): status = ON
  threading.Thread(target=Relaythread,args=(argList[0],status,argList[2],argList[3],)).start()

def RGBevent(argString):
  argList = argSplit(argString)
  rList = argList[0].split("-")
  gList = argList[1].split("-")
  bList = argList[2].split("-")
  threading.Thread(target=RGBthread,args=(rList[0],rList[1],gList[0],gList[1],bList[0],bList[1],argList[3],argList[4],)).start()

def PWMevent(argString):
  argList = argSplit(argString)
  threading.Thread(target=PWMthread,args=(argList[0],argList[1],argList[2],argList[3],)).start()

def STEPevent(argString):
  argList = argSplit(argString)
  threading.Thread(target=STEPthread,args=(argList[0],argList[1],argList[2],argList[3],argList[4],argList[5],)).start()

def SoundEvent(argString):
  if Stat.onBool == False:
    argList = argSplit(argString)
    typeStr = ""
    if argList[0] == "1":
      typeStr = typeOne
    elif argList[0] == "2":
      typeStr = typeTwo
    elif argList[0] == "3":
      typeStr = typeThree
    elif argList[0] == "4":
      typeStr = typeFour
    else:
      webiopi.debug(tempList[0] + " is not a valid sound type")
      return "ERROR"
    if typeStr != "":
      soundPath = GetSoundPath(soundMain + typeStr + "*.wav")
      webiopi.debug("Sound Path - " + soundPath)
      sound = pygame.mixer.Sound(soundPath)
      Stat.onBool = True
      threading.Thread(target=SoundThread,args=(sound,argList[1],argList[2],)).start()

#*****
# Thread functions
#*****
#****************************************************************
#Run thread for IO
def IOthread(pin,status,sec,delay):
  inPin = int(pin)-1 
  #Handle delay in needed
  if (str(delay) != "0"):
    webiopi.sleep(float(delay))
  #Write desired status
  io.digitalWrite(inPin, status)
  #If interval needed then wait and toggle
  if (str(sec) != "0"):
    webiopi.sleep(float(sec))
    if (status == ON):
      io.digitalWrite(inPin, OFF)
    else:
      io.digitalWrite(inPin, ON)

#****************************************************************
#Run thread for Relay      
def Relaythread(pin,status,sec,delay):
  inPin = int(pin)-1 
  #Handle delay in needed
  if (str(delay) != "0"):
    webiopi.sleep(float(delay))
  #Write desired status
  relay.digitalWrite(inPin, status)
  #If interval needed then wait and toggle
  if (str(sec) != "0"):
    webiopi.sleep(float(sec))
    if (status == ON):
      relay.digitalWrite(inPin, OFF)
    else:
      relay.digitalWrite(inPin, ON)

#****************************************************************
#Run thread for RGB
def RGBthread(rNum,rDC,gNum,gDC,bNum,bDC,sec,delay,strobe):
  #Handel delay if needed
  if (str(delay) != "0"):
    webiopi.sleep(float(delay))
  #Write out PWM to RGB
  pwm.pwmWriteFloat(int(rNum),float(rDC))
  pwm.pwmWriteFloat(int(gNum),float(gDC))
  pwm.pwmWriteFloat(int(bNum),float(bDC))
  #If interval/strobe needed then wait and toggle
  if (str(sec) != "0"):
    webiopi.sleep(float(sec))
    pwm.pwmWriteFloat(int(rNum),0.0)
    pwm.pwmWriteFloat(int(gNum),0.0)
    pwm.pwmWriteFloat(int(bNum),0.0)

#****************************************************************
#Run thread for PWM
def PWMthread(pin,DC,sec,delay):
  #Handel delay if needed
  if (str(delay) != "0"):
    webiopi.sleep(float(delay))
  #Write out PWM to to DC
  pwm.pwmWriteFloat(int(pin),float(DC))
  #If interval needed then wait and toggle
  if (str(sec) != "0"):
    webiopi.sleep(float(sec))
    pwm.pwmWriteFloat(int(pin),0.0)

#****************************************************************
#Run thread for Sound
def SoundThread(sound,relay,delay):
  #Handel delay if needed
  webiopi.debug("SOUND ON")
  if (str(delay) != "0"):
    webiopi.sleep(float(delay))
  timeOn = sound.get_length() + .5
  threading.Thread(target=Relaythread,args=(relay,ON,timeOn,"0.25",)).start()
  sound.play()
  webiopi.sleep(float(timeOn))
  Stat.onBool = False
  webiopi.debug("SOUND OFF")
 
#*****
# Sub Support functions
#*****
def argSplit(argsIn):
  return argsIn.split(";")

def testIO():
#Relays
  n = 0
  while n < 16:
    relay.digitalWrite(n, ON)
    webiopi.sleep(.5)
    relay.digitalWrite(n, OFF)
    n = n + 1
#IO;s
#  n = 0
#  while n < 16:
#    io.digitalWrite(n, ON)
#    webiopi.sleep(.5)
#    io.digitalWrite(n, OFF)
#    n = n + 1

def relayOn():
  n = 0
  while n < 16:
    relay.digitalWrite(n, ON)
    n = n +1

def relayOff():
  n = 0
  while n < 16:
    relay.digitalWrite(n, OFF)
    n = n +1

#Return random file for directory
def GetSoundPath(dirStr):
  aFiles = glob.glob(dirStr)
  path = aFiles[random.randint(0,len(aFiles)-1)]
  return path

# *********************************************************************************
# Notes
# *********************************************************************************

#threading.Thread(target=threadrun,args=(pin,sec,)).start()

# sound = pygame.mixer.Sound("/home/pi/WebIOPi-0.6.0/examples/scripts/macros/TestWav.wav")
    # sound.play()
