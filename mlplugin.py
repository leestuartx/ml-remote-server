import importlib
from mlpluginapi import MLPluginAPI
from threading import Timer

#Script data
active_script = None
active_script_name = None
mlobject = None
script_folder = 'examples'

#begins setup and training if marked as should_train_on_start
def begin_play_events():
	if(mlobject.should_train_on_start):
		mlobject.on_begin_training()


def begin_play():
	if(mlobject == None):
		error_msg = 'mlplugin Error: No valid active script, run load first'
		print(error_msg)
		return None, error_msg
	else:
		try:
			#call startup sequence
			mlobject.on_setup()

			#post tick start events (runs 10 ms later)
			Timer(0.01, begin_play_events).start()		

			return True, None
		except BaseException as e:
			error_msg = 'mlplugin Error: Incorrect api for ' + active_script_name + ': ' + e
			return None, error_msg


def start_training():
	mlobject.on_begin_training()

#stop script (training for now)
def stop_training():
	if(mlobject != None):
		#NB: this stops training, but atm won't do anything else
		mlobject._stop_training() 


#load script into memory. Ready to call start().
def load(script_name):
	global active_script
	global active_script_name
	global mlobject

	if(active_script_name != script_name):
		del active_script
		active_script = None
		mlobject = None
		active_script_name = None

	status_msg = 'unknown'
	active_script_name = script_name

	if(active_script != None):
		importlib.reload(active_script)
	else:
		active_script = importlib.import_module(script_folder + '.' + script_name)

	#grab an instance and check api
	try:
		mlobject = active_script.get_api()
		if issubclass(mlobject.__class__, MLPluginAPI):
			status_msg = 'valid script loaded'
			return status_msg, None #its valid reverse tuple
		else:
			status_msg = 'invalid script class, please subclass MLPluginAPI'
			return None, status_msg
	except BaseException as e:
		status_msg = e
		return None, status_msg


#run inputs on our class
def json_input(input):
	if(mlobject != None):
		return mlobject.on_json_input(input)

def float_input(input):
	if(mlobject != None):
		return mlobject.on_float_array_input(input)

def custom_function(name, param):
	if(mlobject != None):
		method_to_call = getattr(mlobject, name)
		if(method_to_call):
			return method_to_call(param)
		else:
			return None