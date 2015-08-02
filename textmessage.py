from QueueConfig import *
config = Config(CONFIGDIR)
from ActionFramework import *
from ParseArgs import args as argvs

printer = PluginPrinterInstance()
printer.setname("Texting")
printer.setcolor(bcolors.GREEN)

def addNumberToJob(**kwargs):
	args, authstate, sec, ws, queue = kwargs["args"], kwargs["authstate"], kwargs["sec"], kwargs["ws"], kwargs["queue"]
	job_uuid, phone = args["uuid"], args["phone"]

	job, masterindex, priority, index = queue.getQueueObject(job_uuid)

	if "phone" not in job or job["phone"] == "none":
		if authstate:
			job["phone"] = phone
			job["coachmodified"] = True
		else:
			return "Changing a set phone number requires auth."
	else:
		job["phone"] = phone

	if argvs.loud: # If -v, report success
		color = bcolors.MAGENTA if authstate else ""
		printer.cprint("Gave {} a phone number.\n({})".format(job["name"], job_uuid), color=color)


prevLength = 0
sentTo = []

def text(phone):
	if not phone:
		return
	pass # texting protocol goes here

def upkeep(**kwargs):
	global sentTo, prevLength
	queue = kwargs["queue"]

	for i in sentTo:
		job, masterindex, priority, index = queue.getQueueObject(i)
		if not job:
			sentTo.remove(i)

	masterqueue = queue.masterqueue()
	if masterqueue:
		job = masterqueue[0]
		uuid = job["uuid"]
		if uuid not in sentTo:
			sentTo.append(uuid)
			if prevLength != 0:
				cprint("Texting {}.\n({})".format(job["name"], uuid))
				text(job["phone"])
	prevLength = len(masterqueue)
		 


requiredTags = {
	"phone": "none"
}

hideFromClient = [
	"phone"
]

socketCommands = [
	SocketCommand("add#", addNumberToJob, {"uuid": str, "phone": str})
]

requiresAuth = [
]

