#!/usr/bin/python

import sys, argparse, pprint, os, errno, requests, json, glob

import sevenbridges as sbg

from sevenbridges.errors import SbgError

pp = pprint.PrettyPrinter(indent=4)

api_config = sbg.Config(profile='my-profile')
api = sbg.Api(config=api_config)

user = api.users.me()

#task_name = 'Leave Home Task#1'
#project_id = 'sfmclaugh/joey-ramone'

task_name = 'leave-home-task'

project_list = api.projects.query(offset=0, limit=10)
pp.pprint(project_list)

for project in api.projects.query().all():
    print (project.id,project.name)

project_id = 'sfmclaugh/steve-test2'


#App = 'sfmclaugh/joey-ramone/steve_test'
app = 'sfmclaugh/steve-test2/write-test-file'

test_file_tag = '58531409e4b0f31cb3cd1103'
file = api.files.get(id=test_file_tag)

inputs = {}
#inputs['#dummy-input'] = file

print("\n")

try:
    project_id = project_id
    project = api.projects.get(id=project_id)
    print("hello-->")
    pp.pprint(project)
    print("<--howRu?")
except SbgError as e:
    print (e.message)

bg = api.billing_groups.query(limit=1)[0] #grab the first billing group.

pp.pprint(bg)

bgroup_list = api.billing_groups.query(offset=0, limit=10) #grab all billing groups.

#print all billing groups:
for bg in bgroup_list:
    pp.pprint(bg)


new_project_id = 'darklands'
project = api.projects.get('darklands')

files_to_upload = glob.glob('/Users/c02sl6rg8wn/software/7br/tiny_bam/*bam*')

task_name = 'psycho-candy'
full_project_id = 'sfmclaugh/darklands'
app = 'sfmclaugh/excavator-sdk-demo/excavator'

inputs = {}
inputs['test']
inputs['control']

#api.files.upload(files_to_upload[0], full_project_id, file_name='this/is/a/file.txt')

#sys.exit()

#bucket_location = 's3://1000genomes/vol1/ftp/phase3/data/HG00513/exome_alignment/HG00513.mapped.ILLUMINA.bwa.CHS.exome.20120522.bam'

#imp = api.imports.submit_import(name='1000genomes', location=bucket_location, project=project)

#while True:
#      import_status = imp.reload().state
#      if import_status in (ImportExportState.COMPLETED, ImportExportState.FAILED):
#           break
 #     time.sleep(10)
# Continue with the import
#if imp.state == ImportExportState.COMPLETED:
#      imported_file = imp.result

#for file in files_to_upload:
#	api.files.upload(file, full_project_id)

#create a new project:
#api.projects.create(name=new_project_id, billing_group=bg.id)

#pp.pprint(bg.id)

#sys.exit()

####this block creates a task:
#try:
#	task = api.tasks.create(name=task_name, project='sfmclaugh/steve-test2', app=app, run=False, inputs=inputs)
#except SbgError as e:
#    print(e.message)

#create a new project:
#api.projects.create(name="momster-2017", billing_group=bg.id)
