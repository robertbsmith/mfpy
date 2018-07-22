import myfitnesspal
from datetime import timedelta, date, timezone
import datetime
import sys
import matplotlib.pyplot as plt
import matplotlib
import numpy
import userconfig


# Helper functions
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

#http://www.superskinnyme.com/calculate-tdee.html
def calcTDEE(weightkg,heightcm,age,activityfactor):
	return activityfactor * (66 + (13.7 * weightkg) + (5*heightcm) - (6.8*age))

def calcKgLoss(calories):
	return calories/7700

# run in command line first: myfitnesspal store-password your@email.com
# note if using win make sure to pip install wincurses

# MFP login details
print("Logging into myfitnesspal user " + userconfig.username)
client = myfitnesspal.Client(userconfig.username)

# User Input 
startdate = userconfig.startdate
heightcm = userconfig.heightcm
age = userconfig.age
activitylevel = userconfig.activitylevel
startweightkg = currentweightkg = userconfig.startweightkg
targetweightkg = userconfig.targetweightkg

# Calculated inputs
enddate = datetime.datetime.now().date()
TDEE = calcTDEE(startweightkg,heightcm,age,activitylevel)
startBMI = startweightkg / pow(heightcm/100,2)
targetBMI = targetweightkg / pow(heightcm/100,2)

print("Collecting data (" + startdate.strftime('%d-%b-%Y') + " to " + enddate.strftime('%d-%b-%Y') + ")",end='',flush=True)


# Read calorie time series
daylist = []
missed = 0
for dt in daterange(startdate,enddate):
	day = client.get_date(dt)
	if day.totals:
		daylist.append(day)
	print('.',end='',flush=True)

print('')

# Perform calculations on calorific data
calorieDefecit = 0
cnt = 0;
WeightLoss = 0
predictedWeightList = []
predictedWeightDateList = []


for day in daylist:
	calories = day.totals["calories"]
	calorieDefecit += (TDEE - calories)
	cnt += 1
	if calories > TDEE :
		WeightLoss = calcKgLoss(abs(TDEE - calories))
		currentweightkg += WeightLoss
		print(day.date.strftime('%d-%b-%Y') + ' Calorie Surplus = %.1f' % WeightLoss)
	else:
		WeightLoss = calcKgLoss(TDEE - calories)
		currentweightkg -= WeightLoss
		print(day.date.strftime('%d-%b-%Y') + ' Calorie defecit = %.1f' % WeightLoss)

	predictedWeightList.append(currentweightkg)
	predictedWeightDateList.append(day.date)

#Read actual weight time series
weights = client.get_measurements('Weight')

actualWeightList = []
actualWeightDateList = []

actualWeightList.append(startweightkg)
actualWeightDateList.append(predictedWeightDateList[0])

for key, value in weights.items() :
	actualWeightDateList.append(key)
	actualWeightList.append(value)

kgloss = calcKgLoss(calorieDefecit);
ibloss = kgloss * 2.2 
print('Start Weight was %.1f'% startweightkg)
print('Total predicted weight loss over %d days is %.1f kg (%.1f ib)' %(cnt,kgloss,ibloss))
print('Predicted weight is %.1f'% (startweightkg - kgloss))

#Generate BMI data
predictedBMIList = [x/pow((heightcm/100),2) for x in predictedWeightList]
actualBMIList = [x/pow((heightcm/100),2) for x in actualWeightList]

#generate 1d trendline from predicted weight
datenum = matplotlib.dates.date2num(predictedWeightDateList)

z = numpy.polyfit(datenum,predictedWeightList,1)
p = numpy.poly1d(z)

eqnx = z[0]
eqny = z[1]

# Target weight = eqnx*X + eqny	
# solve for x 
# (Target weight - eqny)/eqnx = X = date to reach target
targetWeightDate = matplotlib.dates.num2date((targetweightkg - eqny) / eqnx)
deltaTime = targetWeightDate.replace(tzinfo=None) - datetime.datetime.utcnow().replace(tzinfo=None)

print("Will reach target weight on: " + targetWeightDate.strftime('%d-%b-%Y') + " (%d days / %d weeks)"%(deltaTime.days,deltaTime.days/7))


# Graph results
if(actualWeightDateList[0] < predictedWeightDateList[0]):
	graphStartDate = actualWeightDateList[0]
else:
	graphStartDate = predictedWeightDateList[0]

fig, ax = plt.subplots()
plt.title("MyFitnessPal Actual vs Predicted weight")
l1 = ax.plot(actualWeightDateList,actualWeightList,"g-",label='Actual Weight',zorder=10)
l2 = ax.plot(predictedWeightDateList,predictedWeightList,"g--",label='predicted weight',zorder=10)
plt.xticks(rotation=45)
plt.ylabel('Weight (kg)')
plt.xlabel('Date')



# Plot limits
ax.text(graphStartDate,startweightkg + 0.5,'Start Weight',zorder=10)
ax.text(graphStartDate,targetweightkg + 0.5,'Target Weight',zorder=10)
ax.axhline(y=startweightkg,color='black',linestyle='--',zorder=10)
ax.axhline(y=targetweightkg,color='black',linestyle='--',zorder=10)



axBMI = ax.twinx()
l3 = axBMI.plot(actualWeightDateList,actualBMIList,"r-",label='Actual BMI',zorder=10)
l4 = axBMI.plot(predictedWeightDateList,predictedBMIList,"r--",label='Predicted BMI',zorder=10)

axBMI.text(graphStartDate,startBMI + 0.5,'Start BMI',zorder=10)
axBMI.text(graphStartDate,targetBMI + 0.5,'Target BMI',zorder=10)
axBMI.axhline(y=startBMI,color='black',linestyle='--',zorder=10)
axBMI.axhline(y=targetBMI,color='black',linestyle='--',zorder=10)

lns = l1+l2+l3+l4
labs = [l.get_label() for l in lns]
legend = ax.legend(lns,labs,loc='upper right', shadow=True, fontsize='large')
legend.set_zorder(10)

axBMI.axhspan(25,30,facecolor='gold',zorder=0)
axBMI.axhspan(20,25,facecolor='lightgreen',zorder=0)
axBMI.set_ylabel('BMI')
axBMI.text(graphStartDate,25.1,'Overweight',zorder=1)
axBMI.text(graphStartDate,24.6,'Normal',zorder=1)

ax.set_xlim([graphStartDate,enddate])
ax.set_ylim([targetweightkg - 2, startweightkg + 2])

formatter = matplotlib.dates.DateFormatter('%d-%m-%Y')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)

ax.set_zorder(axBMI.get_zorder()+1)
ax.patch.set_visible(False)
plt.show()
