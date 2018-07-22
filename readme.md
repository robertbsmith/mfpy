# myfp
myfp uses the [myfitnesspal](https://github.com/coddingtonbear/python-myfitnesspal) library to generate graphical weight loss predictions from calorie counting data and compares them to actual weight measurements stored on myfitnesspal.

# Features
Using users weight, height, age and activity level predict weight loss by calories in / calories out. This data is used to predict the date the user will reach target weight. This data can be graphically compared to actual weight loss data as below.

<insert image here>

# Limitations
probably loads, only tested on my mfp account and only supports weights in kg from my mfp.
  
# Installation
requires myfitnesspal, matplotlib and numpy to function. Created using Python v3.6 

Create the following file "userconfig.py"
```py
from datetime import datetime

#myfitnesspal login details:
# Note: run the following  in command line first:
# 'myfitnesspal store-password your@email.com'
# if using win make sure to pip install wincurses
username = 'your@email.com'
# The date you start 
startdate = datetime(1901,01,31).date()

# User information for TDEE calculation
heightcm = <your height cm>
age = <your age in years>
activitylevel = <your [activity level]()
startweightkg = <your starting weight in kg> (ideally matches start date)
targetweightkg = <your target weight in kg>
```
