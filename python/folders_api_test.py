#!/usr/bin/python

import sys, argparse, pprint, os, errno, requests, json

import sevenbridges as sbg
api_config = sbg.Config(profile='my-profile')
api = sbg.Api(config=api_config)

user = api.users.me()
#print "What is the user? --> ", user



exit

API_BASEPATH = 'https://api.sbgenomics.com/v2'

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def make_full_path(dir_name, project_name, headers):
	folder_array = dir_name.split("/")
	url = API_BASEPATH + '/' + 'projects/' + project_name
	r = requests.get(url, headers=headers)
	r = json.loads(r.text) #hash me.
	current_parent_folder = str(r['root_folder'])
	print(current_parent_folder)
	for index in enumerate(folder_array):
		if len(index[1]) == 0:  
			continue
		url = API_BASEPATH + '/' + 'files'
		print(url)
		b = {'name': index[1], 'parent': current_parent_folder, 'type': "FOLDER"}
		print(b)
		r = requests.post(url, data=json.dumps(b), headers=headers)
		r = json.loads(r.text)
		pprint.pprint(r)
		if 'message' in r.keys() and r['message'] == "Requested folder already exists.":
			#cool, but we need the existing file id:
			url = API_BASEPATH + '/files/' + current_parent_folder + '/list'
			r = requests.get(url, headers=headers)
			r = json.loads(r.text) #hash me.
			for i in enumerate(r['items']):
				if i[1]['name'] == index[1] and i[1]['type'] == 'folder':
					current_parent_folder = i[1]['id']
			print current_parent_folder
		else:
			current_parent_folder = r['id']
		print current_parent_folder


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--test_file')
    parser.add_argument('-t', '--token')
    parser.add_argument('-p', '--project_name')
    parser.add_argument('-i', '--file_id')
    #parser.add_argument('-v', dest='verbose', action='store_true')
    args = parser.parse_args()

    # ... do something with args.output ...
    # ... do something with args.verbose ..
    if len(sys.argv) == 1: 
    	parser.print_help()
    	sys.exit() 

    abs_path_test_file = os.path.abspath(args.test_file)
    print abs_path_test_file
    #print args.test_file
    dir_name = os.path.dirname(os.path.realpath(args.test_file))
    test_file_basename = os.path.basename(args.test_file)
    #print test_file_basename
    mkdir_p(dir_name)
    f = open(abs_path_test_file, 'w')
    f.write('This is a test file.' + "\n")
    #pprint.pprint(folder_array)
    #print args.project_name
    headers = {'content-type': 'application/json', 'Accept': 'application/json',
    	'X-SBG-Advance-Access': 'advance',
    	'X-SBG-Auth-Token': args.token}


make_full_path(dir_name=dir_name, project_name=args.project_name, headers=headers)

