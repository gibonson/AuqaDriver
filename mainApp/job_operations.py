from mainApp.webContent import WebContentCollector
from mainApp.webContent import WebContentExecutor
from mainApp.webContent import LinkCreator
from mainApp import app, db
from datetime import datetime
from mainApp.models import FunctionScheduler, DevicesFunctions, Devices



def jobCollector(httpAddress):
   print("jobCollector: " + httpAddress)
   webContentCollector = WebContentCollector(httpAddress)
   webContentCollector.collect()
   print()

def jobExecutor(httpAddress): 
   print("jobExecutor: " + httpAddress)
   webContentExecutor = WebContentExecutor(httpAddress)
   webContentExecutor.execute()
   print()

def schedStart(sched, runSchedulerID = None):
   print("schduler start")
   with app.app_context():
      if runSchedulerID == None:
         functionsScheduler = FunctionScheduler.query.all()
      else:
         functionsScheduler = FunctionScheduler.query.filter_by(schedulerID=runSchedulerID)
      devicesFunctions = DevicesFunctions.query.all()
      devices = Devices.query.all()
      for functionScheduler in functionsScheduler:
         print()
         linkCreator = LinkCreator(devicesFunctions[functionScheduler.functionId-1].id)
         httpLink =  linkCreator.functions_list_link_creator()
         print("httpLink = " + httpLink)
         schedulerID = functionScheduler.schedulerID
         print("schedulerID = " + schedulerID)         
         print(functionScheduler.id)
         print(devicesFunctions[functionScheduler.functionId-1].id)
         print(devices[devicesFunctions[functionScheduler.functionId-1].deviceId-1].deviceIP)
         print(devices[devicesFunctions[functionScheduler.functionId-1].deviceId-1].deviceName)
         print(devicesFunctions[functionScheduler.functionId-1].deviceId)
         jobType = devicesFunctions[functionScheduler.functionId-1].jobType
         print("jobType = " + jobType)
         print(devicesFunctions[functionScheduler.functionId-1].actionLink)
         print(devicesFunctions[functionScheduler.functionId-1].functionDescription)
         print(devicesFunctions[functionScheduler.functionId-1].functionParameters)
         trigger = functionScheduler.trigger
         print("trigger = " + trigger)
         year = functionScheduler.year
         print(year)
         month = functionScheduler.month
         print(month)
         day = functionScheduler.day
         print(day)
         day_of_week = functionScheduler.day_of_week
         print(day_of_week)
         hour = functionScheduler.hour
         print(hour)
         minute = functionScheduler.minute
         print("minute = " + str(minute))
         second = functionScheduler.second
         print("second = " + str(second))

         if functionScheduler.trigger == "interval":
            print("interval")
            sched.add_job(id=schedulerID, func=globals()[jobType], args=[httpLink], trigger=trigger, hours = hour, minutes = minute, seconds = second, max_instances = 10)

         elif functionScheduler.trigger == "date":
            print("date")
            sched.add_job(id=schedulerID, func=globals()[jobType], args=[httpLink], trigger=trigger,run_date=datetime(year, month, day, hour, minute, second), max_instances = 10)

         elif functionScheduler.trigger == "cron":
            print("cron")
            if day > 0:
               sched.add_job(id=schedulerID, func=globals()[jobType], args=[httpLink], trigger=trigger, day = day, hour = hour, minute = minute, second = second, max_instances = 10)
            elif day_of_week != "None":
               sched.add_job(id=schedulerID, func=globals()[jobType], args=[httpLink], trigger=trigger, day_of_week = day_of_week, hour = hour, minute = minute, second = second, max_instances = 10)
            else:
               sched.add_job(id=schedulerID, func=globals()[jobType], args=[httpLink], trigger=trigger, hour = hour, minute = minute, second = second, max_instances = 10)
         else:
            print("wrong job type")
