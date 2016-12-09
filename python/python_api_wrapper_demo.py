#!/usr/bin/python

import sys, argparse, pprint, os, errno, requests, json

import sevenbridges as sbg

api_config = sbg.Config(profile='my-profile')
api = sbg.Api(config=api_config)

user = api.users.me()

task_name = 'Leave Home Task#1'
project_id = 'sfmclaugh/joey-ramone'

app = 'sfmclaugh/joey-ramone/steve_test'

#try:
task = api.tasks.create(name=task_name, project=project_id, app=app, run=True)
#except SbError:
 #   print('I was unable to run the task.')