import webiopi
import time
import threading
import pygame
import glob
import random
import os
pygame.mixer.init()
from webiopi import deviceInstance

# *********************************************************************************
# Setup
# *********************************************************************************

# Initial setup and constants
webiopi.setDebug()
GPIO = webiopi.GPIO
OFF = GPIO.HIGH
ON = GPIO.LOW

# Relay modual setup
relay1 = deviceInstance("relay1")
relay2 = deviceInstance("relay2")
relay3 = deviceInstance("relay3")
relayMax = 24

#Sound Setup
soundMain = str(os.path.dirname(os.path.realpath(__file__))) + "/Sound/"
typeOne = "Type1/"
typeTwo = "Type2/"
typeThree = "Type3/"
typeFour = "Type4/"
class SoundStat:
  onBool = False
  def __init__(self):
    pass

Stat = SoundStat()

#Other modual *Future work
#pwm = deviceInstance("pwm")

# *********************************************************************************
# Inherited
# *********************************************************************************

# Called by WebIOPi at script loading
def setup():
  webiopi.debug("Halloween Macros - Start")
 
  #Set expander pins as outputs
  for num in range(0,7):
    relay1.setFunction(num, GPIO.OUT)
  for num in range(0,7):
    relay2.setFunction(num, GPIO.OUT)
  for num in range(0,7):
    relay3.setFunction(num, GPIO.OUT)
    
  # Setup GPIO
  relayOff(0)
  
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

#*****
# Diagnostics
#*****

#cmd to test the GPIO expansions
@webiopi.macro
def IOTEST():
  testIO()
  return "TEST COMPLETE"

#Turn all relays on or off
@webiopi.macro
def totalRelay(OnOff):
  if OnOff == "on":
    relayOn(0)
  else:
    relayOff(0)

#*****
# Main Command
#*****

#Recieve command and hand off
@webiopi.macro
def cmd(cmdString):
  #Seperate out commands
  cmdList = cmdString.split(":")
  
  #Send cmd's to handlers
  for cmd in cmdList:
    tempList = cmd.split("=")
    if (tempList[0].upper()) == "RELAY":
      RelayEvent(tempList[1])
    #elif (tempList[0].upper()) == "RGB":
      #RGBevent(tempList[1])
    #elif (tempList[0].upper()) == "PWM":
      #PWMevent(tempList[1])
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

def RelayEvent(argString):
  argList = argSplit(argString)
  # Handle requests over the max amount of relays
  if (int(argList[0]) > relayMax):
    webiopi.debug(str(argList[0]) + " greater than the max value of " + str(relayMax))
    return
  #Work with status
  status = OFF
  if (argList[1].upper() == "ON"): status = ON
  #pin,status,sec,delay
  threading.Thread(target=Relaythread,args=(argList[0],status,argList[2],argList[3],)).start()

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
      #Sound object, relay, delay
      threading.Thread(target=SoundThread,args=(sound,argList[1],argList[2],)).start()


#*****
# Future functions
#*****      
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

#*****
# Thread functions
#*****
#****************************************************************

#Run thread for Relay      
def Relaythread(pin,status,sec,delay):
  relay = relay1
  #Select relay object and set logic pin
  if int(pin) <= 8:
    relay = relay1
    inPin = int(pin)-1
  #elif int(pin) <= 16:
    relay = relay2
    inPin = int(pin)-9 
  elif int(pin) <= 24:
    #relay = relay3
    inPin = int(pin)-17 
  else:
    webiopi.debug(tempList[0] + " is not a valid command")
    return "ERROR - " + tempList[0] + " is not a valid command"
    
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
#Run thread for Sound
def SoundThread(sound,relay,delay):
    
  #Handel delay if needed
  if (str(delay) != "0"):
    webiopi.sleep(float(delay))
    
  #Get Sound length
  timeOn = sound.get_length() + .5
  
  #Turn sound on for desired length and relay
  webiopi.debug("SOUND ON")
  threading.Thread(target=Relaythread,args=(relay,ON,timeOn,"0.25",)).start()
  sound.play()
  webiopi.sleep(float(timeOn))
  
  #Sound has ended
  Stat.onBool = False
  webiopi.debug("SOUND OFF")

#**************************************************************** Future below here
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
 
#*****
# Sub Support functions
#*****
def argSplit(argsIn):
  return argsIn.split(";")

def testIO():
  relayOff(0)
  relayOn(0.5)
  webiopi.sleep(3.00)
  relayOff(0.5)

def relayOn(delay):
  for pin in range(1,relayMax):
    Relaythread(pin,ON,"0","0")
    webiopi.sleep(float(delay))

def relayOff(delay):
  for pin in range(1,relayMax):
    Relaythread(pin,OFF,"0","0")
    webiopi.sleep(float(delay))
    

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
