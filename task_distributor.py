import time
import json
from collections import OrderedDict
import os

def Message(status, status_text = None, data = None):
    msg = OrderedDict()
    msg['status'] = status
    if status_text is not None:
        msg['status_text'] = status_text
    if data is not None:
        msg['data'] = data
    return msg

def Task_U(user):
    task = OrderedDict()
    task['user'] = user
    task['start_time'] = time.time()
    task['end_time'] = None
    task['result'] = None
    return task

def is_timeout(t1, timeout):
    if timeout is None or time.time() - t1 < timeout:
        return False
    else:
        return True

def time_print(ts):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))

def search_list(L, key_func, x):
    for i, e in enumerate(L):
        if key_func(e) == x:
            return i, e
    return -1, None

def list_to_str(L, join_str = ' '):
    s_L = [str(k) for k in L]
    return join_str.join(s_L)

class DynamicTaskDistributor:
    def __init__(self, data, id_key, num_worker, timeout):
        self.available_data = list(data)
        self.id_key = id_key

        self.num_worker = num_worker
        self.timeout = timeout

        self.working_task = []
        '''
        {
            'data': data,
            'label_results': [
                {
                   'user': user,
                   'start_time'
                   'end_time'
                   'result' 
                },
                ...
            ]
        }
        '''
    
    def search_working_task(self, user):
        for task in self.working_task:
            for u_res in task['label_results']:
                if u_res['user'] == user and u_res['result'] is None:
                    u_res['start_time'] = time.time()  #update the start time
                    return task['data']
        return None

    def get_user_data(self, user):
        data = self.search_working_task(user)
        if data is not None:
            return Message(100, 'Successful', data)

        # search already allocated task
        for task in self.working_task:
            flag = False
            for u_res in task['label_results']:
                if u_res['user'] == user and u_res['result'] is None:
                    u_res['start_time'] = time.time()
                    flag = True
            if flag:
                return Message(100, 'Successful', task['data'])

        # scan working list sequencely
        for task in self.working_task:
            user_list =[k['user'] for k in task['label_results']]
            if user in user_list:
                continue

            # look whether there is vacancy
            if len(task['label_results']) < self.num_worker:
                task['label_results'].append(Task_U(user))
                return Message(100, 'Successful', task['data'])

            # look whether there is timeout user
            idx = None
            for i, u_res in enumerate(task['label_results']):
                if u_res['result'] is None and is_timeout(u_res['start_time'], self.timeout):
                    idx = i
                    break
            if idx is not None:
                task['label_results'].pop(idx)
                task['label_results'].append(Task_U(user))
                return Message(100, 'Successful', task['data'])

        if len(self.available_data) > 0:
            data = self.available_data.pop(0)
            self.working_task.append({'data': data, 'label_results': [Task_U(user)]})
            return Message(100, 'Successful', data)
        else:
            return Message(202, 'No data left')

    def save_label_result(self, user, data_id, label_result):
        task_idx, task = search_list(self.working_task, lambda k: k['data'][self.id_key], data_id)
        print(task)
        if task is None:
            print(data_id)
            print(self.working_task)
            return Message(202, 'Task timeout'), None  # No task

        _, u_res = search_list(task['label_results'], lambda k: k['user'], user)
        if u_res is None:
            print(user)
            print(task['label_results'])
            return Message(202, 'Task timeout'), None  # Have task, no user

        if u_res['result'] is not None:
            return Message(203, 'Repetitive submit'), None

        u_res['end_time'] = time.time()
        u_res['result'] = label_result
        count = [u_res['result'] is not None for u_res in task['label_results']]
        if sum(count) >= self.num_worker:
            _ = self.working_task.pop(task_idx)
            return Message(100, 'Successful'), task
        else:
            return Message(100, 'Successful'), None

class DynamicTaskManager(DynamicTaskDistributor):
    def __init__(self, all_data, save_file, passwd_table, id_key, num_worker, timeout):
        super(DynamicTaskManager, self).__init__(all_data, id_key, num_worker, timeout)
        
        self.save_file = save_file
        self.passwd_table = passwd_table

        self.user_history = {}
        self.count_f = 0
        self.count_t = 0

        save_dir = os.path.dirname(save_file)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    def auth(self, user, passwd):
        if self.passwd_table is not None:
            if user in self.passwd_table and passwd != self.passwd_table[user]:
                return Message(201, 'Authentication failed')
            if user not in self.passwd_table:
                return Message(201, 'Authentication failed')
        return None

    def convert_data(self, labeled_data):
        new_data = OrderedDict()
        new_data[self.id_key] = labeled_data['data'][self.id_key]
        new_data['label_results'] = []
        for u_res in labeled_data['label_results']:
            n_u_res = OrderedDict(u_res)
            n_u_res['start_time'] = time_print(u_res['start_time'])
            n_u_res['end_time'] = time_print(u_res['end_time'])
            new_data['label_results'].append(n_u_res)
        return new_data

    def get_user_data(self, user, passwd):
        message = self.auth(user, passwd)
        if message is not None:
            return message
        
        return super(DynamicTaskManager, self).get_user_data(user)

    def save_label_result(self, user, data_id, label_result, passwd):
        message = self.auth(user, passwd)
        if message is not None:
            return message

        message, labeled_data = super(DynamicTaskManager, self).save_label_result(user, data_id, label_result)

        if str(message['status'])[0] == '1':
            if user not in self.user_history:
                self.user_history[user] = []
            self.user_history[user].append(data_id)
            self.count_f += 1
        if labeled_data is not None:
            saved_data = self.convert_data(labeled_data)
            with open(self.save_file, 'a', encoding='utf8') as f:
                f.write(json.dumps(saved_data, ensure_ascii = False) + '\n')
            self.count_t += 1
        return message

    def info_user_history(self):
        info_uhis = OrderedDict()
        info_uhis['Finished task'] = self.count_t
        info_uhis['Annotation frequency'] = self.count_f
        info_uhis['user_history'] = [(u, len(his), list_to_str(his)) for u,his in self.user_history.items()]

        return info_uhis

    def info_working_task(self, verbose = False):
        str_wk = OrderedDict()
        for task in self.working_task:
            task_id = task['data'][self.id_key]
            str_wk[task_id] = []
            for u_res in task['label_results']:
                d = OrderedDict()
                d['user'] = u_res['user']
                d['start_time'] = time_print(u_res['start_time'])
                d['end_time'] = None if u_res['end_time'] is None else time_print(u_res['end_time'])
                if verbose:
                    d['result'] = u_res['result']
                str_wk[task_id].append(d)

        return str_wk


if __name__ == '__main__':
    dym_manager = DynamicTaskManager([], './save.txt', None, 'id', 2, None)

