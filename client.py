from datetime import datetime
import json
from json import JSONDecodeError
import re
import time
import requests
import subprocess


def get_config():
    f = open('config.json')
    try:
        data = json.load(f)
        return data
    except JSONDecodeError:
        print('check config.json File')


config = get_config()


# -----------getting file data------------------------------
def get_data():
    print('getting data from server\n')
    d = requests.get(config['host'] + '/status').text == 'True'
    if not d:
        d = requests.get(config['host'] + f'/data?worker={config["id"]}')
        with open(f'{config["id"]}.txt', 'w+') as f:
            f.write(d.text)
    else:
        print('password is cracked')


# -----------benchmarking job------------------------------
def run_hashcat_benchmarking():
    d = subprocess.run(['hashcat', '-m', '2500', '-b'], capture_output=True)
    d = d.stdout.decode('utf-8')
    # print(d)
    # extracting speed --- regex
    d = re.search(r"{}".format(config['benchmark_re']), d).group(0)
    if d:
        return d
    else:
        return None


# -----------running job------------------------------
def run_hash_cat():
    # getting file
    subprocess.run(['curl', '-O', f'{config["host"]}/static/handshake.hccapx'])

    d = subprocess.run(['hashcat', 'handshake.hccapx', '-m', '2500', f'{config["id"]}.txt'], capture_output=True)

    d = d.stdout.decode('utf-8')

    d = re.search(r"{}".format(config['status_re']), d).group(0)

    if d:
        if 'Cracked' in d:
            post_status(True)
        else:
            post_status(False)
        return d
    else:
        return None


# -----------sending job results------------------------------
def post_status(status):
    if status:
        requests.post(config['host'] + '/getWorkerStatus',
                      data={'status': 'Cracked', 'username': config['id']}
                      )
    else:
        requests.post(config['host'] + '/getWorkerStatus',
                      data={'status': 'Not Cracked and IDLE', 'username': config['id']}
                      )


# ----------basic details about worker----------------------------
def initial_heartbeat():
    benchmark = run_hashcat_benchmarking()
    requests.post(config['host'] + '/createWorker',
                  data={'username': config['id'], 'benchmark': benchmark})


# ------- check files available to crack---------------
def check_files_available():
    return True if requests.get(config['host'] + '/workstatus').status_code == 200 else False


# -----------waiting for job------------------------------
while True:
    try:
        if requests.get(config['host'] + '/status').status_code == 200:
            initial_heartbeat()

            hashCracked = False if requests.get(config['host'] + '/hash-cracked').text == 'failed' else True
            if check_files_available() and not hashCracked:
                get_data()
                print(run_hash_cat())
            else:
                post_status(status=False)
                x = datetime.now()
                print('$$--no files available : ', x.strftime('%x %X'))
                time.sleep(10)
    except requests.exceptions.ConnectionError:
        x = datetime.now()
        print('$$--server is offline : ', x.strftime('%x %X'))
        time.sleep(60 * 2)
