from QueueConfig import *
config = Config(CONFIGDIR)
from ActionFramework import *

printer = PluginPrinterInstance()
printer.setname("Texting")
printer.setcolor(bcolors.GREEN)

def addWithPhone(**kwargs):
	args, authstate, sec, ws, queue = kwargs["args"], kwargs["authstate"], kwargs["sec"], kwargs["ws"], kwargs["queue"]
	name, priority, esttime, material, phone = args["name"], args["priority"], args["time"], args["material"], args["phone"]

	# If the priority or the material aren't set up, or the name isn't defined
	if not name or material == "N/A" or priority == -1:
		# Tell the client then don't add the object
		serveToConnection({
			"action": "notification",
			"title": "Incomplete data",
			"text": "Please fill out the submission form fully."
			}, ws)
		if args.loud:
			cprint("Insufficient data to add job to queue.", color=bcolors.YELLOW)
		return

	# Contain the length of time within the configurable bounds.
	bounds = config["length_bounds"]
	if bounds[0] >= 0:
		esttime = max(bounds[0], esttime)
	if bounds[1] >= 0:
		esttime = min(bounds[1], esttime)

	# lock the priority down to the max if the user isn't authed.
	if not config["priority_selection"] and not authstate:
		priority = min(config["default_priority"], priority)

	# Recalculate priority if applicable.
	if config["recalc_priority"]:
		priority = _calcpriority(priority, esttime)

	# Strip whitespace from the name and recapitalize it
	name = name.strip().rstrip()
	if config["recapitalize"]:
		name = name.title()

	# Make sure the user isn't in the queue. The config can allow multiple materials per person, or not.
	inqueue = False
	for i in queue.queue:
		for j in i: 
			if name.lower() == j["name"].lower() and (
					material == j["material"] or (not config["allow_multiple_materials"])):
				inqueue = True
				break

	# Make the uuid of the job
	job_uuid = str(uuid.uuid1())

	if not inqueue or config["allow_multiples"]: # If the job is allowed to be created
		# Add it to the queue
		queue.queue[priority].append(QueueObject({
			"totaldiff": 0,
			"priority": priority,
			"name": name,
			"material": material,
			"esttime": esttime,
			"coachmodified": authstate,
			"uuid": job_uuid,
			"sec": sec,
			"time": time.time(),
			"phone": phone
		}))

		if argvs.loud: # If -v, report success
			color = bcolors.MAGENTA if authstate else ""
			cprint("Added {} to the queue.\n({})".format(name, job_uuid), color=color)
	elif argvs.loud: # If -v, report failures
		cprint("Cannot add {} to the queue.".format(name), color=bcolors.YELLOW)


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
	SocketCommand("add#", addWithPhone, {"name": str, "priority": int,
	 "time": any_number, "material": str, "phone": str})
]


