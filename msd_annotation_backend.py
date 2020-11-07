import os
import json
import sys
from flask import Flask, jsonify, request, abort
import time
import logging

sys.path.append('/Users/lizijun/Documents/uiuc/platform/Annotation front+back/')
from task_distributor import DynamicTaskManager, Message

timestamp = time.strftime('%Y%m%d_%H%M', time.localtime())

# Load config file
with open('config.json', encoding = 'utf8') as f:
    config = json.load(f)

# Config logging
if not os.path.exists('./log'):
    os.mkdir('./log')
logging.basicConfig(
    #format = '%(asctime)s - %(message)s', 
    #datefmt = '%Y-%m-%d %H:%M:%S',
    format = '%(name)s: %(message)s', 
    level = logging.DEBUG, 
    filename='./log/log_{}.txt'.format(timestamp),
    filemode='w')
logging.root.addHandler(logging.StreamHandler(sys.stdout))
logging.info(json.dumps(config, indent = 4, sort_keys = True, ensure_ascii = False))

# Load all data
with open(config['data_fn'], encoding='utf8') as f:
    all_data = json.load(f)
    # all_data = [json.loads(k) for k in f]
all_data = all_data['data'][0]["paragraphs"]
logging.info('Original data: {}'.format(len(all_data)))

# if("id" not in all_data[0]):
#     for i in range(len(all_data)):
#         all_data[i]['id'] = str(i)

id_key = config['id_key']
# Load finish id list
finish_list = set()
if len(config['finish_fn']) > 0:
    logging.info('Find finished samples')
for fin_fn in config['finish_fn']:
    with open(fin_fn, encoding='utf8') as f:
        cur_fin = set([json.loads(k)[id_key] for k in f])
    logging.info('{}: {}'.format(fin_fn, len(cur_fin)))
    finish_list.update(cur_fin)
logging.info('Total finished samples: {}'.format(len(finish_list)))

# Filter data
all_data = [d for d in all_data if d[id_key] not in finish_list]
print(all_data[0])
logging.info('After filtering: {} samples'.format(len(all_data)))

save_fn = './anno_data/labeled_data_{}.txt'.format(timestamp)

pw = None if config['pw_fn'] is None else json.load(open(config['pw_fn'], encoding='utf8'))

# Get task manager object
my_task = DynamicTaskManager(all_data, save_fn, pw,
    id_key, config['num_worker'], config['timeout'])

app = Flask(__name__)
@app.route('/')
def info_page():
    with open('./home.html', 'r', encoding='utf8') as f:
        web = f.read()
    return web

@app.route('/get-data', methods = ['POST'])
def get_data():
    body = request.json
    u = body.get('user', '')
    p = body.get('password', '')
    message = my_task.get_user_data(u, p)
    return jsonify(message)

@app.route('/send-data', methods = ['POST'])
def send_data():
    body = request.json
    u = body.get('user', '')
    p = body.get('password', '')
    pid = body.get(id_key, '')
    result = body.get('label_result')
    message = my_task.save_label_result(u, pid, result, p)
    return jsonify(message)

@app.route('/authentication', methods = ['POST'])
def authenticate():
    body = request.json
    u = body.get('user', '')
    p = body.get('password', '')
    message = my_task.auth(u, p)
    if message is None:
        message = Message(100, 'Successful')
    return jsonify(message)

@app.route('/web/<fn>')
def get_web(fn):
    path = os.path.join('./web', fn)
    if os.path.exists(path):
        with open(path, encoding='utf8') as f:
            cont = f.read()
        return cont
    else:
        abort(404)


#-------------------
#  Administrator
#-------------------
@app.route('/admin/user')
def admin_web():
    his = my_task.info_user_history()
    return jsonify(his)

@app.route('/admin/reload-user-pw')
def reload_pw():
    my_task.passwd_table = json.load(open(config['pw_fn'], encoding='utf8'))
    return '0'

@app.route('/admin/cache')
def cache():
    res = my_task.info_working_task()
    return jsonify(res)

@app.route('/admin/cache/verbose')
def cache_verbose():
    res = my_task.info_working_task(True)
    return jsonify(res)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = config['port'], debug = False)

