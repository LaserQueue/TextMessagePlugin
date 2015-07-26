from QueueConfig import *
from ActionFramework import *

printer = PluginPrinterInstance()
printer.setname("Texting")
printer.setcolor(bcolors.GREEN)

requiredTags = {
	"phone": "none"
}

hideFromClient = [
	"phone"
]