#!/usr/bin/env python

# //////////////////////////////////////////////////////////////////////////
# /*
# Titel:				Python Natural Light 2 RGB Converter 
# Author:				Melvin Strobl
# Credits:				Carlos Platoni (2015) : Sunset and Sunrise calculation
# 						http://thorpesoftware.com/calculating-sunrise-and-sunset/
# 						ShawnF (2014) : Color Temp to RGB Conversion :
# 						http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
# Date Created:			05.06.18
# Last Update: 			10.06.18

#BEGIN INIT INFO
# Provides:		Natural Light to RGB Converter
# Description:	Converts White to a more natural light in RGB
#END INIT INFO

# */
# //////////////////////////////////////////////////////////////////////////


#--------------------------------------------------------------------------
#	Import REGION
#--------------------------------------------------------------------------
import math
import sys
from math import log
from datetime import date, timedelta, datetime, time, tzinfo

#--------------------------------------------------------------------------
#	Constants REGION
#--------------------------------------------------------------------------
# Set your Location depending coordinates
COORDS = {'longitude' : 8.403653, 'latitude' : 49.006889 }
# Set your earliest WakeUp Time
EARLIESTWAKEUPTIME = {'hr':6, 'min':30}
# Set your earliest Sleep Time
EARLIESTSLEEPTIME = {'hr':22, 'min':0}

# Set your preferred transition times
MORNINGTRANSTIME = {'hr':1, 'min':0}
EVENINGTRANSTIME = {'hr':3, 'min':0}

NIGHTTIMECOLOR = 2450
DAYTIMECOLOR = 6500

MORNINGSUNEFFECT = 0.1
EVENINGSUNEFFECT = 0.2

#--------------------------------------------------------------------------
#	Utilities for trigonometric calculations
#--------------------------------------------------------------------------
def sinrad(deg):
	return math.sin(deg * math.pi/180)

def cosrad(deg):
	return math.cos(deg * math.pi/180)

#--------------------------------------------------------------------------
#	Calculate Sunrise and Sunset from Julian Date
#--------------------------------------------------------------------------
def calculatetimefromjuliandate(julianDate):
	julianDate=julianDate+.5
	secs=int((julianDate-int(julianDate))*24*60*60+.5)
	mins=int(secs/60)
	hour=int(mins/60)  
	return time(hour, mins % 60, secs % 60)

#--------------------------------------------------------------------------
#	Calculate Sunrise and Sunset
#--------------------------------------------------------------------------
def calcsunriseandsunset(date, coord):
	a=math.floor((14-date.month)/12)
	y = date.year+4800-a
	m = date.month+12*a -3
	julian_date=date.day+math.floor((153*m+2)/5)+365*y+math.floor(y/4)-math.floor(y/100)+math.floor(y/400)-32045
	
	longitude=coord['longitude'] #West
	latitude=coord['latitude'] #North

	nstar= (julian_date - 2451545.0 - 0.0009)-(longitude/360)
	n=round(nstar)
	jstar = 2451545.0+0.0009+(longitude/360) + n
	M=(357.5291+0.98560028*(jstar-2451545)) % 360
	c=(1.9148*sinrad(M))+(0.0200*sinrad(2*M))+(0.0003*sinrad(3*M))
	l=(M+102.9372+c+180) % 360
	jtransit = jstar + (0.0053 * sinrad(M)) - (0.0069 * sinrad(2 * l))
	delta=math.asin(sinrad(l) * sinrad(23.45))*180/math.pi
	H = math.acos((sinrad(-0.83)-sinrad(latitude)*sinrad(delta))/(cosrad(latitude)*cosrad(delta)))*180/math.pi
	jstarstar=2451545.0+0.0009+((H+longitude)/360)+n
	jset=jstarstar+(0.0053*sinrad(M))-(0.0069*sinrad(2*l))
	jrise=jtransit-(jset-jtransit)
	
	return {'sunrise':calculatetimefromjuliandate(jrise), 
			'sunset':calculatetimefromjuliandate(jset)}

#--------------------------------------------------------------------------
#	Converts given color Temp in K into RGB
#--------------------------------------------------------------------------
def colorTemp2RGB(temp):
	temp = temp/100

	# Red
	if temp <= 66:
		red = 255
	else:
		red = temp - 60
		red = 329.698727446 * (red** -0.1332047592)

	# Green
	if temp <= 66:
		green = temp
		green = 99.4708025861 * log(green) - 161.1195681661
	else:
		green = temp - 60
		green = 288.1221695283 * (green** -0.0755148492)

	#Blue
	if temp >= 66:
		blue = 255
	else:
		if temp <= 19:
			blue = 0
		else:
			blue = temp - 10
			blue = 138.5177312231 * log(blue) - 305.0447927307


	return {'r':red, 'g':green,'b':blue}
	
#--------------------------------------------------------------------------
#	Converts given UTC Time into linear Time from 0 to 1
#--------------------------------------------------------------------------
def utc2lin(hr, min):
	linMin = min/60.0/24.0
	linHr = hr/24.0
	
	return (linHr+linMin)

#--------------------------------------------------------------------------
#	Calculates sine-wave transition with given parameters
#--------------------------------------------------------------------------
def transition(linTime, linMidTime, linTransTime, maxTemp, minTemp, orientation):
	aveTemp = minTemp + (maxTemp - minTemp)/2
	scaleTemp = (maxTemp - minTemp)/2
	
	linScaledTime=(linTime-linMidTime)/linTransTime*math.pi

	# 	   y-shift y-orientation y-scale           x scale
	return aveTemp+orientation*scaleTemp*math.sin(linScaledTime)

#--------------------------------------------------------------------------
#	Calculates Sunrise and Sunset time from class sun into linear time
#--------------------------------------------------------------------------	
def adaptTime2Sun(linEventTime, linTransTime, beforeMidday):
	today=date.today()
	res = calcsunriseandsunset(today, COORDS)

	if beforeMidday:
		sunrise={'hr':res['sunrise'].hour, 'min':res['sunrise'].minute}
		
		linSunrise = utc2lin(sunrise['hr'], sunrise['min'])
		
		linEventTime = linEventTime - MORNINGSUNEFFECT*(linEventTime-linSunrise)
		linTransTime = linTransTime - MORNINGSUNEFFECT*(linEventTime-linSunrise)
		
	else:
		sunset={'hr':res['sunset'].hour, 'min':res['sunset'].minute}

		linSunset = utc2lin(sunset['hr'], sunset['min'])
		
		linEventTime = linEventTime - EVENINGSUNEFFECT*(linEventTime-linSunset)
		linTransTime = linTransTime - EVENINGSUNEFFECT*(linEventTime-linSunset)
		
	return {
		'linEvent':linEventTime, 
		'linTrans':linTransTime
	}
	
#--------------------------------------------------------------------------
#	Calculates White RGB into a smoother color using Sunset and 
#	Sunrise Information
#--------------------------------------------------------------------------
def time2Color(linTime):
	if(linTime < utc2lin(12,00)): #Before Midday
		linTransTime = utc2lin(MORNINGTRANSTIME['hr'], MORNINGTRANSTIME['min'])
		linWakeUpTime = utc2lin(EARLIESTWAKEUPTIME['hr'], EARLIESTWAKEUPTIME['min'])
		
		linWakeUpTime = adaptTime2Sun(linWakeUpTime, linTransTime, True)['linEvent']
		linTransTime = adaptTime2Sun(linWakeUpTime, linTransTime, True)['linTrans']
		
		if abs(linWakeUpTime - linTime) < linTransTime/2: #within transition zone
			color = transition(linTime, linWakeUpTime, linTransTime, DAYTIMECOLOR, NIGHTTIMECOLOR, +1)
		elif linTime < linWakeUpTime: #nighttime
			color = NIGHTTIMECOLOR
		else: #daytime
			color = DAYTIMECOLOR
	else: #After Midday
		linTransTime = utc2lin(EVENINGTRANSTIME['hr'], EVENINGTRANSTIME['min'])
		linSleepTime = utc2lin(EARLIESTSLEEPTIME['hr'], EARLIESTSLEEPTIME['min'])
		
		linSleepTime= adaptTime2Sun(linSleepTime, linTransTime, False)['linEvent']
		linTransTime = adaptTime2Sun(linSleepTime, linTransTime, False)['linTrans']
		
		if abs(linSleepTime - linTime) < linTransTime/2: #within transition zone
			color = transition(linTime, linSleepTime, linTransTime, DAYTIMECOLOR, NIGHTTIMECOLOR, -1)
		elif linTime < linSleepTime: #daytime
			color = DAYTIMECOLOR
		else: #nighttime
			color = NIGHTTIMECOLOR
	
	return color

#--------------------------------------------------------------------------
#	Main
#--------------------------------------------------------------------------
def main():
	today=date.today()
	res = calcsunriseandsunset(today, COORDS)
	print "Sunrise at:\t"+str(res['sunrise'])
	print "Sunset at:\t"+str(res['sunset'])
	
	now = datetime.now()
	print("Current Time:\t"+str(now.hour)+":"+str(now.minute))
	
	color = time2Color(utc2lin(now.hour, now.minute))
	print("Calculated Color Temperature:\t"+str(color))
	
	rgb = colorTemp2RGB(color)
	
	print("Red:\t"+str(rgb['r'])+"\nGreen:\t"+str(rgb['g'])+"\nBlue:\t"+str(rgb['b']))

if __name__ == '__main__':
	try:
		main()
	#On keyboard interrupt
	except KeyboardInterrupt:
		print("\nQuit cause of keyboard interrupt")
		# quit_i2c_broker()

	#On IO Error interrupt
	except IOError:
		print("\nQuit cause of IO error")
		# quit_i2c_broker()
	#General Errors
	except:
		e = sys.exc_info()[0]
		print( "<p>Error: %s</p>" % e )