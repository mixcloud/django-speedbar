import time

from mixcloud.speedbar.modules import ThreadLocalSingleton

class StackRecorder(ThreadLocalSingleton):
    key = 'stackrecorder'

    def __init__(self):
        super(StackRecorder, self).__init__()
        self.root = None
        self.stack = []
        self.stack_id = 0

    def push_stack(self, action_type, label):
        entry = {
            'id': str(self.stack_id),
            'range': { 'start': int(time.time()*1000) },
            'operation' : {
                'type': action_type,
                'label': label,
            },
            'children': [],
        }
        self.stack_id += 1
        if len(self.stack):
            self.stack[-1]['children'].append(entry)
        else:
            self.root = entry
        self.stack.append(entry)

    def pop_stack(self):
        tip = self.stack[-1]
        tip['range']['end'] = int(time.time() * 1000)
        tip['range']['duration'] = tip['range']['end'] - tip['range']['start']
        self.stack.pop()

    def get_metrics(self):
        return {}

    def speedtracer_log(self, trace_id):
        return {
            'trace': {
                'id': str(self.stack_id),
                'application': 'Speedbar',
                'date': time.time(),
                'range': self.root['range'],
                'frameStack': self.root,
            }
        }
