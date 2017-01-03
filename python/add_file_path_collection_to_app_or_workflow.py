#!/usr/bin/python

import sys, argparse, pprint, os, errno, requests, json, glob, json, re
import sevenbridges as sbg
from sevenbridges.errors import SbgError

pp = pprint.PrettyPrinter(indent=4)

#api_config = sbg.Config(profile='my-demo-profile')
#api = sbg.Api(config=api_config)

def create_new_cwl(user, project_name, app_name, args, arguments_json, output_tar_outputs_json):
	app_id = user + '/' + project_name + '/' + app_name
	project_name = user + '/' + project_name

	my_project = [p for p in API.projects.query(limit=100).all() \
					if p.id == project_name][0]

	my_apps = API.apps.query(project = my_project.id, limit=100)

	single_app = [a for a in my_apps.all() if a.id == app_id][0]

	workflow = {'cwl':single_app.raw}

	workflow_cwl_json = workflow['cwl']
	outputs_array   = workflow_cwl_json['outputs']
	arguments_array = workflow_cwl_json['arguments']

	##this is the metadata you want to add to the CWL to get it to retain 1) glob_path and 2) self for any output files.
	full_path_metadata = """{"sbg:metadata": {
    	    "glob_path": {
        	    "script": "$self.path",
            	"class": "Expression",
           		"cwl-js-engineine": "#cwl-js-engine"
          	}}}"""

	full_path_metadata = json.loads(full_path_metadata)['sbg:metadata']

	for i in outputs_array:
		if 'File' in i['type']:
			if 'outputBinding' in i:
			#there is going to be an entry for outputBinding if there is an output file specified in the workflow.
			#but, there might not be an entry for metadata.  if there is an entry for metdata, we want to add to it.  if not, create it.
				if args['add_glob_path']:
					if 'sbg:metadata' not in i['outputBinding']:
						i['outputBinding']['sbg:metadata'] = {}
					new_metadata = i['outputBinding']['sbg:metadata'].copy()
					new_metadata.update(full_path_metadata) #add the code that makes the path of the file get recorded.
					#print(i['outputBinding']['sbg:metadata'])
					#print(new_metadata)
					i['outputBinding']['sbg:metadata'] = new_metadata


	if args['add_output_tar']:
		outputs_array.append(output_tar_outputs_json)
		#arguments_array.append(arguments_json)
		arguments_array = arguments_array + arguments_json #appending this isn't right- it's an array you want to add to the existing arguments array.
		workflow_cwl_json['arguments'] = arguments_array
		#print(arguments_array)
		#sys.exit()


	new_cwl = workflow_cwl_json
	if args['add_glob_path'] and not args['add_output_tar']:
		new_cwl['label'] = new_cwl['label'] + ' w/full path capture'
		new_app_id = project_name + '/' + app_name + '-with-full-path'
	elif args['add_output_tar'] and not args['add_glob_path']:
		new_cwl['label'] = new_cwl['label'] + ' w/output.tar'
		new_app_id = project_name + '/' + app_name + '-with-output-tar5'
		new_cwl["sbg:cmdPreview"] = new_cwl["sbg:cmdPreview"] + '  ;tar -cvf output.tar ./"' 

	#was thinking maybe adding in something if the user wants to do both but it sort of doesn't make sense
	#seeing as how once the files are all tarred there isn't any point in capturing the glob path.

	if args['test']:
		print(("new_app_id: %s")%(new_app_id))
		print(("new_cwl: %s")%(new_cwl))
		sys.exit()
	new_app = API.apps.install_app(id = new_app_id, raw = new_cwl)
	return new_cwl, new_app_id

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-u', '--user', help="i.e. <bob>")
	parser.add_argument('-p', '--project_name', help='i.e. project_name w/o user.')
	parser.add_argument('-a', '--app_name', help='just the appname i.e. my_app')
	parser.add_argument('-t', '--token')
	parser.add_argument('-e', '--api_endpoint', default='https://api.sbgenomics.com/v2')

	parser.add_argument('-g', '--add_glob_path', action="store_true", help="add the glob-path capture to the output files.")
	parser.add_argument('-z', '--add_output_tar', action="store_true", help="add creation of output.tar in the working directory to the end of any app or workflow.")
	#parser.add_argument('-d', '--delete_orig_files', action="store_true", help="Delete the original output files if creating an output.tar")
	parser.add_argument('-x', '--test', action="store_true", help="Just print the CWL json- don't actually create the app.")
	args = parser.parse_args()
	args = vars(args)

	ARGS = args
	if len(sys.argv) == 1: 
		parser.print_help()
		sys.exit() 

	#replicate what the platform does: swap out all underscores in apps and project names for hyphens:
	if ARGS['project_name']:
		ARGS['project_name'] = re.sub(r'_', '-', ARGS['project_name'])
	if ARGS['app_name']:
		ARGS['app_name'] = re.sub(r'_', '-', ARGS['app_name'])

#print(ARGS)
if (not args['add_glob_path'] and not args['add_output_tar']) or (args['add_glob_path'] and args['add_output_tar']):
	print("You must either --add_glob_path OR --add_output_tar.  Now exiting!")
	sys.exit()


#this is the hack for getting any job to create a tar file of the working directory as the final step:
arguments_json = """{"arguments": [
    {
      "separate": false,
      "valueFrom": "tar -cvf output.tar ./",
      "prefix": ";",
      "position": 99999999
    }
  ]}"""

arguments_json = json.loads(arguments_json)['arguments'] #add this in to tar up the output files if that is the intent.

#this actually adds the tar file to the outputs.
output_tar_outputs_json = """{
      "type": [
        "null",
        "File"
      ],
      "outputBinding": {
        "glob": "output.tar"
      },
      "id": "#output_tar"
    }"""

output_tar_outputs_json = json.loads(output_tar_outputs_json)


API = sbg.Api(url=ARGS['api_endpoint'], token=ARGS['token'])
new_cwl, new_app_id = create_new_cwl(ARGS['user'], ARGS['project_name'], ARGS['app_name'], ARGS, arguments_json, output_tar_outputs_json)
print(("altered workflow has been added to project %s!")%(ARGS['project_name']))
print(("new app label: %s")%(new_cwl['label']))
print(("new app id:    %s")%(new_app_id))
sys.exit()



