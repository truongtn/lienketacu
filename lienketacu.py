#Author: nhattruong.blog
import requests
import urllib3, json, time
import traceback
import sys
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

target_file = "targets.txt"
username = ""
password_hash = ""
host = ""
port = ""
threads = 3

http_proxy = ""
https_proxy = ""

f = open(target_file,"r")
site_list = f.readlines()
for i in range(len(site_list)):
    site_list[i] = site_list[i][:-1]
print(site_list)

proxyDict = {
    "http": http_proxy,
    "https": https_proxy
}

s = requests.Session()
# login
data = {"email": username,
        "password": password_hash, "remember_me": "false",
        "logout_previous": "true"}
r = s.post("https://"+host+":"+port+"/api/v1/me/login", json=data, verify=False)
x = r.headers['X-Auth']
# kiem tra info
headers = {'x-auth': x}
r = s.get("https://"+host+":"+port+"/api/v1/info", verify=False, headers=headers)


# add a target
def add_site(list):
    global x
    data = {"targets": [], "groups": []}
    for i in list:
        data['targets'].append({"address": i, "description": "add tu dong"})
    headers = {'x-auth': x}
    # data = {
    #     "targets": [{"address": "https://1.com", "description": "1"}, {"address": "https://2.com", "description": "2"},
    #                 {"address": "https://3.com", "description": "3"}], "groups": []}
    r = s.post("https://"+host+":"+port+"/api/v1/targets/add", json=data, verify=False, headers=headers)
    print(r.json())
    return r.json()


# run a target
def run(target_id):
    global x
    headers = {'x-auth': x}
    data = {"profile_id": "11111111-1111-1111-1111-111111111111", "ui_session_id": "175162633513976c8e3d1856b917ebd6",
            "incremental": "false", "schedule": {"disable": "false", "start_date": None, "time_sensitive": "false"},
            "target_id": target_id}
    r = s.post("https://"+host+":"+port+"/api/v1/scans", json=data, verify=False, headers=headers)


# list all running targets
def list_scan():
    global x
    headers = {'x-auth': x}
    r = s.get("https://"+host+":"+port+"/api/v1/scans?l=100", json=data, verify=False, headers=headers)
    return r.json()


def check_current_scan(number):
    time.sleep(2)
    stt = 0
    a = list_scan()
    try:
        a = a['scans']
    except Exception as exc:
        print(traceback.format_exc())
        print(exc)
        return 1
    for i in a:
        if i['current_session']['status'] in ["processing","scheduled","queued"] :
            stt += 1
    if stt >= number:
        return 1
    else:
        return 0


# main
site_list_id = []
a = add_site(site_list)
for i in a['targets']:
    site_list_id.append(i['target_id'])
done = 0
stt = 0
while done == 0:
    if check_current_scan(threads) == 0:
        run(site_list_id[stt])
        stt += 1
    if stt == len(site_list_id):
        done = 1
print('All targets have been run!')
