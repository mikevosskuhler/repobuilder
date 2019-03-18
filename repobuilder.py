'''
The purpose of this script is to quickly create a bitbucket repository that
allows for the deployment of splunk apps via the cicd pipeline. The user should
not have to have any interactions with git and the script should clean up after
itself
'''

import os
import requests
import git
import sh

file_dir = os.path.abspath(os.path.join(os.path.realpath(__file__), ".."))

def get_response(itemname):
    x = 0
    while x == 0:
        input = raw_input("Do you need "+itemname+"?[y|n]")
        if input == "y" or input == "n":
            x += 1
    return input

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

project_name = str(raw_input("What should your project be called?"))
username = str(raw_input("What is your username?"))
password = str(raw_input("What is your password?"))
pr_inputs = get_response("pr inputs")
et_inputs = get_response("et inputs")
st_inputs = get_response("st inputs")
ut_inputs = get_response("ut inputs")
props = pr_inputs or et_inputs or st_inputs or ut_inputs
pr_shc = get_response("pr shc")
et_shc = get_response("et shc")

uri_string = "https://api.bitbucket.org/2.0/repositories/mikevosskuhler/"+
                project_name
data_string = "name="+project_name

bb_response = requests.post(uri_string, auth=(username, password),
                            data=data_string)
json_response = bb_response.json()
clone_uri = json_response[u'links'][u'clone'][0][u'href']
repo_dir = os.path.abspath(os.path.join(file_dir, project_name))

git.Repo.clone_from(clone_uri, repo_dir)
os.chdir(repo_dir)

if pr_inputs or props or pr_shc:
    os.mkdir("pr")
    if pr_inputs:
        os.makedirs("pr/f_"+project_name+"_pr/local")
        touch("pr/f_"+project_name+"_pr/local/inputs.conf")
    if props:
        os.makedirs("pr/i_"+project_name+"/local")
        touch("pr/i_"+project_name+"/local/props.conf")
        touch("pr/i_"+project_name+"/local/transforms.conf")
    if pr_shc:
        os.makedirs("pr/s_se_"+project_name+"/local")
if et_inputs or st_inputs or ut_inputs or et_shc:
    os.mkdir("et")
    if et_inputs:
        os.makedirs("et/f_"+project_name+"_et/local")
        touch("et/f_"+project_name+"_et/local/inputs.conf")
    if st_inputs:
        os.makedirs("et/f_"+project_name+"_st/local")
        touch("et/f_"+project_name+"_st/local/inputs.conf")
    if ut_inputs:
        os.makedirs("et/f_"+project_name+"_ut/local")
        touch("et/f_"+project_name+"_ut/local/inputs.conf")
    if et_shc:
        os.makedirs("et/s_se_"+project_name+"/local")

os.chdir(repo_dir)
clone_uri_wpw = clone_uri.replace("@", ":"+password+"@")

def push(message):
    sh.git.add(".")
    sh.git.commit(m=message)
    sh.git.commit(clone_uri_wpw)
def create_checkout(branchname):
    sh.git.branch(branchname)
    sh.git.checkout(branchname)

sh.git.add(".")
sh.git.commit(m="initial commit")
sh.git.push(clone_uri_wpw)
# push("initial commit")
sh.git.branch("et")
sh.git.checkout("et")
# create_checkout("et")
sh.rm("-rf", "pr/")
sh.git.add(".")
sh.git.commit(m="initial commit for pr")
sh.git.push(clone_uri_wpw)
# push("initial commit in et")
sh.git.checkout("master")
sh.git.branch("pr")
sh.git.checkout("pr")
# create_checkout("pr")
sh.rm("-rf", "et")
sh.git.add(".")
sh.git.commit(m="initial commit for pr")
sh.git.push(clone_uri_wpw)
# push("initial commit for pr")
