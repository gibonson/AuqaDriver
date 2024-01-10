from functions import web_content_executor
from functions import web_content_collector
from flask import Flask
from flask_apscheduler import APScheduler


class Config(object):
    SCHEDULER_API_ENABLED = True
    JSONIFY_PRETTYPRINT_REGULAR = True

app = Flask(__name__)
app.config.from_object(Config())
sched = APScheduler()
sched.init_app(app)


jobTableCollector = [
    ['jobID1', 'jobCollector', "interval", 0, 0, 10, '192.168.0.184', 'device1'],
    ['jobID2', 'jobCollector', "interval", 0, 0, 10, '192.168.0.185', 'device2']
]

jobTableExecutor = [
    ['jobID3', 'jobExecutor', "interval", 0, 0, 60, '192.168.0.185', 'device2', '/gpioON', None],
    ['jobID4', 'jobExecutor', "interval", 0, 0, 60, '192.168.0.185', 'device2', '/gpioOFF', None],
    ['jobID5', 'jobExecutor', "interval", 0, 0, 60, '192.168.0.185', 'device2', '/nawozy', [["value1","1"],["value2","2"],["value3","3"]]]
]



def jobCollector(deviceIP, deviceName):
   print("jobCollector: " + deviceIP, deviceName)
   webContentCollector = web_content_collector.WebContentCollector(deviceIP, deviceName)
   webContentCollector.collect()
   print()



def jobExecutor(deviceIP, deviceName, location, nameValueTable):
   print("jobExecutor: " + deviceIP, deviceName)
   webContentExecutor = web_content_executor.WebContentExecutor(deviceIP, deviceName, location, nameValueTable)
   webContentExecutor.execute()
   print()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/stop")
def stop():
    # sched.pause()
    sched.remove_job('job1')
    return "<p>stop</p>"


@app.route("/start")
def start():
    sched.resume()
    return "<p>start</p>" 


@app.route("/get_jobs")
def get_jobs():
    print(sched.get_jobs())
    for job in sched.get_jobs():
        print("JOB ID:" + job.id + " JOB NAME:" + job.name + " JOB TRIGGER:" + str(job.trigger) + " NEXT JOB:" + str(job.next_run_time))
        # print(job)
    return "<p>get_jobs</p>" 



def schedStart():
    # for job in jobTableCollector:
    #     print(job)
    #     print("0=", job[0], "1=", job[1], "2=", job[2], "3=", job[3],
    #           "4=", job[4], "5=", job[5], "6=", job[6], "7=", job[7])

    #     if job[2] == "interval":
    #         sched.add_job(id=job[0], func=globals()[job[1]], args=[
    #                       job[6], job[7]], trigger=job[2], seconds=job[5])
    #     else:
    #         sched.add_job(id=job[0], func=globals()[job[1]], args=[
    #                       job[6], job[7]], trigger=job[2], hour=job[3], minute=job[4], second=job[5])
            
    for job in jobTableExecutor:
        print(job)
        print("0=", job[0], "1=", job[1], "2=", job[2], "3=", job[3],
              "4=", job[4], "5=", job[5], "6=", job[6], "7=", job[7], "8=", job[8], "9=", job[9])
        if job[2] == "interval":
            sched.add_job(id=job[0], func=globals()[job[1]], args=[job[6], job[7], job[8], job[9]], trigger=job[2], seconds=job[5])
      #   else:
      #       sched.add_job(id=job[0], func=globals()[job[1]], args=[
      #                     job[6], job[7]], trigger=job[2], hour=job[3], minute=job[4], second=job[5])
    sched.start()


if __name__ == '__main__':
    schedStart()
    app.run(debug=True, use_reloader=False)
