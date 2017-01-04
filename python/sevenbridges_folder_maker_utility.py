#!/usr/bin/python

import sys, argparse, pprint, os, errno, requests, json, re, copy, tempfile

import sevenbridges as sbg

def query_file_id(project_name, file_id, headers):
	return_me = ""
	url = API_ENDPOINT + '/files/' + file_id
	r = requests.get(url, headers=headers)
	r = json.loads(r.text) #hash me
	path_array = []
	path_array.append(r['name'])
	while 'parent' in r:
		current_id = r['parent']
		url = API_ENDPOINT + '/files/' + current_id
		r = requests.get(url, headers=headers)
		r = json.loads(r.text) #hash me.
		if 'parent' in r:
			path_array.append(r['name'])

	path_array = path_array[::-1]
	path_array = "/".join(path_array)
	print(path_array)
	sys.exit()

	return return_me

def query_path(project_name, file_path, headers):
	url = API_ENDPOINT + '/' + 'projects/' + project_name
	r = requests.get(url, headers=headers)
	r = json.loads(r.text) #hash me.
	current_parent_folder = str(r['root_folder'])
	file_path = os.path.normpath(file_path)
	dir_name = os.path.dirname(file_path)
	folder_array = dir_name.split("/")
	for index in enumerate(folder_array):
		if len(index[1]) == 0:  
			continue
		url = API_ENDPOINT + '/files/' + current_parent_folder + '/list'
		r = requests.get(url, headers=headers)
		r = json.loads(r.text) #hash me.
		for i in enumerate(r['items']):
			if i[1]['name'] == index[1] and i[1]['type'] == 'folder':
				current_parent_folder = i[1]['id']
		#print(current_parent_folder)
	#this is now where the file should be:
	url = API_ENDPOINT + '/files/' + current_parent_folder + '/list'
	r = requests.get(url, headers=headers)
	r = json.loads(r.text) #hash me.
	return_me = None
	for i in enumerate(r['items']):
		if i[1]['name'] == os.path.basename(file_path) and i[1]['type'] == 'file':
			#found it!
			return_me = i[1]['id'] 
	return return_me

def find_buried_file(file, project_name, headers):
	#step1: get root ID:
	dir_name = os.path.dirname(file)
	folder_array = dir_name.split("/")
	url = API_ENDPOINT + '/' + 'projects/' + project_name
	r = requests.get(url, headers=headers)
	r = json.loads(r.text) #hash me.
	current_parent_folder = str(r['root_folder'])
	for index in enumerate(folder_array):
		if len(index[1]) == 0:  
			continue
		url = API_ENDPOINT + '/files/' + current_parent_folder + '/list'
		r = requests.get(url, headers=headers)
		r = json.loads(r.text) #hash me.
		print(r)
		sys.exit()

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def get_relative_paths_from_glob_path(glob_path):
	glob_path = os.path.normpath(glob_path) #just in case there are things like extra slashes in the path.
	relative_output_path = "/".join(glob_path.split("/")[8:]) #strip away the directories that are only meaningful to the seven bridges platform.
	dir_name = os.path.dirname(relative_output_path)
	return dir_name, relative_output_path

def update_metadata_and_tags_for_sbg_file_object(f):
	if f.metadata:
		metadata = f.metadata
		if metadata['glob_path']:
			glob_path = metadata['glob_path']
			glob_path = os.path.normpath(glob_path) #just in case there are things like extra slashes in the path.
			dir_name, relative_output_path = get_relative_paths_from_glob_path(glob_path)
			metadata['relative_dir_path']  = dir_name #will be an empty string if there was no directory structure to the file.
			metadata['relative_file_path'] = relative_output_path #dir_name PLUS file_name
			#we also want to make Dir Path and File Path tags for this file if we get here.
			dir_tag  = 'Dir:'  + dir_name
			file_tag = 'File:' + relative_output_path
			f.tags = [dir_tag, file_tag]
			#print("dude?")
			f.save() #this will save all the metadata we added and the new tags.

def update_metadata_and_tags_for_all_outputs_of_a_task(task_id):
	my_details = API.tasks.get(id = task_id)
	#file_objects = {}
	for output_name in my_details.outputs.keys():
		v = my_details.outputs[output_name]
		my_list = []
		#only deal with outputs that are Files and arrays of Files
		if isinstance(v, list):
			my_list = v
		else:
			if isinstance(v, sbg.models.file.File):
				my_list = [v]
		for f in my_list:
			if not isinstance(f, sbg.models.file.File):
				continue
			print(f)
			update_metadata_and_tags_for_sbg_file_object(f)
	sys.exit()


def make_full_path(dir_name, project_name, headers):
	folder_array = dir_name.split("/")
	url = API_ENDPOINT + '/' + 'projects/' + project_name
	r = requests.get(url, headers=headers)
	r = json.loads(r.text) #hash me.
	current_parent_folder = str(r['root_folder'])
	print(current_parent_folder)
	for index in enumerate(folder_array):
		if len(index[1]) == 0:  
			continue
		url = API_ENDPOINT + '/' + 'files'
		print(url)
		b = {'name': index[1], 'parent': current_parent_folder, 'type': "FOLDER"}
		print(b)
		r = requests.post(url, data=json.dumps(b), headers=headers)
		r = json.loads(r.text)
		pprint.pprint(r)
		if 'message' in r.keys() and r['message'] == "Requested folder already exists.":
			#cool, but we need the existing file id:
			url = API_ENDPOINT + '/files/' + current_parent_folder + '/list'
			r = requests.get(url, headers=headers)
			r = json.loads(r.text) #hash me.
			for i in enumerate(r['items']):
				if i[1]['name'] == index[1] and i[1]['type'] == 'folder':
					current_parent_folder = i[1]['id']
			print(current_parent_folder)
		else:
			current_parent_folder = r['id']
	return current_parent_folder

def move_file_to_folder(parent_folder, destination_file, headers, source_file_id):
	url = API_ENDPOINT + '/' + 'files/' + source_file_id + '/' + 'actions/move'
	b = {'parent': parent_folder, 'name': destination_file}
	r = requests.post(url, data=json.dumps(b), headers=headers)
	r = json.loads(r.text)
	pprint.pprint(r)
#def move_file_to_folder(parent_folder, destination_file, headers):
#	url = API_ENDPOINT + '/' + 'files/' + project_name

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-e', '--api_endpoint', default='https://api.sbgenomics.com/v2')
	parser.add_argument('-f', '--file', help="name of file currently stored on Seven Bridges platform.")
	parser.add_argument('-l', '--local_file', help="name of a file that is not currently stored at Seven Bridges platform.  This file will be uploaded to the platform.")
	parser.add_argument('-t', '--token')
	parser.add_argument('-p', '--project_name')
	parser.add_argument('-r', '--remove_num', action='store_true')
	parser.add_argument('-z', '--tag_all', help="attempt to tag all files in project w/glob_path metadata.", action="store_true")
	parser.add_argument('-i', '--task_id', help="explicitly define a task ID.")
	parser.add_argument('-m', '--move_all', help="move all files in project to folders using the metadata.", action='store_true')
	parser.add_argument('-a', '--auto_task_id', help="automatically determine task ID from current working directory.", action="store_true")
	parser.add_argument('-x', '--tag_one', help="tag one file where f.name is specified by --file.  Must have glob_path in metadata.", action="store_true")
	parser.add_argument('-y', '--move_one', help="move one file where f.name is specified by --file.  Must have glob_path in metadata.", action="store_true")
	parser.add_argument('-d', '--destination_dir', help="if --move_one is used, this is where the file will move to.  This will override whatever is in glob_path.")
	parser.add_argument('--query_file_id', help="Query file ID using the path of the file i.e. my/file/is/here/file.txt")
	parser.add_argument('--query_path', help="pass the file ID and traverse backwards to establish the full path.")
	#parser.add_argument('-k', '--move_file_to_root', help="move file back to root directory (needs PROJECT_NAME and FILE).")

	##to do: add the ability to move the files to a single directory specified on the command line.  right now it only uses the metadata field glob_path which is whatever the Glob in the Output matches.  If glob_path is missing, this script simply doesn't do anything (silently exits without throwing an error).

	args = parser.parse_args()

	args = vars(args)

	if args['api_endpoint']:
		API_ENDPOINT = args['api_endpoint']

	ARGS = args

	if len(sys.argv) == 1: 
		parser.print_help()
		sys.exit() 

#MAIN BLOCK OF CODE:

headers = {'content-type': 'application/json', 'Accept': 'application/json', 'X-SBG-Advance-Access': 'advance', 'X-SBG-Auth-Token': ARGS['token']} #use for folders API which doesn't have a python interface yet.
api = sbg.Api(url=ARGS['api_endpoint'], token=ARGS['token'])
API = api
PP = pprint.PrettyPrinter(depth=99)

if ARGS['auto_task_id']:
	cwd = os.getcwd()
	cwd = os.path.abspath(cwd)
	cwd = os.path.normpath(cwd)
	eprint(("what is the cwd? --> %s")%(cwd))
	ARGS['task_id'] = cwd.split("/")[5]

#print(ARGS['task_id'])

if ARGS['task_id']:
	eprint(("what is the task_id? --> %s")%(ARGS['task_id']))
	ARGS['task_details'] = API.tasks.get(id = ARGS['task_id'])
	ARGS['project_name'] = ARGS['task_details'].project
	#update_metadata_and_tags_for_all_outputs_of_a_task(ARGS['task_id'])
#sys.exit()

if ARGS['query_path']:
	file_id = query_path(ARGS['project_name'], ARGS['query_path'], headers)
	print(file_id)
	sys.exit()

if ARGS['query_file_id']:
	path = query_file_id(ARGS['project_name'], ARGS['query_file_id'], headers)
	print(path)
	sys.exit()

if ARGS['local_file']:
	#step1: upload file w/temp name because it will fail if there is already a file with the same name.
	temp_name = next(tempfile._get_candidate_names()) #use the tempfile module without actually creating a file.
	temp_name = temp_name + '.' + os.path.basename(ARGS['local_file'])
	API.files.upload(project=ARGS['project_name'], path=ARGS['local_file'], file_name=temp_name)
	#step2: set file to the temp_name so that when an attempt is made to grab the file it grabs the one that was just uploaded here.
	ARGS['file'] = temp_name

#if ARGS['move_file_to_root']:
#	file = os.path.normpath(ARGS['file'])
#	find_buried_file(file, ARGS['project_name'], headers)
#	sys.exit()

if ARGS['tag_one']:
	my_files = api.files.query(project =ARGS['project_name'].project)
	file_basename = os.path.basename(ARGS['file'])
	for i in my_files:
		if i.name == file_basename:
			f = i
	update_metadata_and_tags_for_sbg_file_object(f)

if ARGS['move_one']:
	my_files = api.files.query(project=ARGS['project_name'])
	file_basename = os.path.basename(ARGS['file'])
	for i in my_files:
		if i.name == file_basename:
			f = i
	#if f.metadata and f.metadata['glob_path']:
	destination_file = os.path.basename(f.name)

	if ARGS['local_file']:
		destination_file = re.sub(r'^[^\.]+\.', '', destination_file) #strip off the temporary prefix.

	if ARGS['remove_num']:
		destination_file = re.sub(r'^_(\d+)_', '', destination_file)

	if f.metadata and f.metadata['glob_path']:
		dir_name, relative_output_path = get_relative_paths_from_glob_path(f.metadata['glob_path'])

	if ARGS['destination_dir']:
		dir_name = os.path.normpath(ARGS['destination_dir'])
		relative_output_path = dir_name + '/' + destination_file
		relative_output_path = os.path.normpath(relative_output_path)

	parent_folder = make_full_path(dir_name, ARGS['project_name'], headers)
	print(parent_folder)
	move_file_to_folder(parent_folder, destination_file, headers, f.id)		

#--move_one and --tag_one can be used together.  If either is kicked off, exit:
if ARGS['tag_one'] or ARGS['move_one']:
	sys.exit()

###Likewise, this utility can be run with --tag_all and --move_all either alone or in tandem.

if ARGS['tag_all']:
	my_files = api.files.query(project =ARGS['project_name'])
	for f in my_files:
		print(f.id)
		print(f.metadata)
		update_metadata_and_tags_for_sbg_file_object(f)
	#print(my_files)
	#sys.exit()

if ARGS['move_all']:
	my_files = api.files.query(project=ARGS['project_name'])
	for f in my_files:
		#print(f.id)
		#print(f.metadata)
		if f.metadata and f.metadata['glob_path']:
			#destination_file = os.path.basename(f.metadata['glob_path'])
			#destination_file = os.path.basename(f.metadata['glob_path'])
			destination_file = os.path.basename(f.name)
			if ARGS['remove_num']:
				destination_file = re.sub(r'^_(\d+)_', '', destination_file)
			#print(destination_file)
			dir_name, relative_output_path = get_relative_paths_from_glob_path(f.metadata['glob_path'])
			parent_folder = make_full_path(dir_name, ARGS['project_name'], headers)
			move_file_to_folder(parent_folder, destination_file, headers, f.id)
		else:
			continue
		#ARGS['project_name']
		#requires project_name:
	#sys.exit()
