import threading, queue, time, uuid, logging

log = logging.getLogger('task-runner')
_TASKS = {}
_JOBS = {}
_Q = queue.Queue()

class Worker(threading.Thread):
    daemon = True
    def run(self):
        while True:
            job_id = _Q.get()
            job = _JOBS.get(job_id, {})
            try:
                name = job.get('name'); args = job.get('args', {})
                fn = _TASKS.get(name)
                if not fn:
                    raise ValueError(f'Unknown task: {name}')
                job['status']='running'; job['started_at']=time.time()
                res = fn(**args) if isinstance(args, dict) else fn(args)
                job['result']=res; job['status']='done'; job['finished_at']=time.time()
            except Exception as e:
                job['error']=str(e); job['status']='failed'; job['finished_at']=time.time()
            finally:
                _JOBS[job_id]=job; _Q.task_done()

for _ in range(2):
    Worker().start()

def task_sleep(seconds: int = 1):
    time.sleep(int(seconds)); return {'slept': int(seconds)}

try:
    import requests as _req
    def task_http_get(url: str, timeout: int = 10):
        r = _req.get(url, timeout=timeout)
        return {'status': r.status_code, 'len': len(r.content)}
except Exception:
    def task_http_get(url: str, timeout: int = 10):
        return {'error': 'requests not installed'}

_TASKS.update({'sleep': task_sleep, 'http_get': task_http_get})

def register(name, fn):
    _TASKS[name]=fn

def submit(name, args=None):
    job_id = str(uuid.uuid4())
    _JOBS[job_id] = {'status':'queued','result':None,'error':None,'name':name,'args':args or {},'started_at':None,'finished_at':None}
    _Q.put(job_id)
    return job_id

def status(job_id):
    return _JOBS.get(job_id, {'status':'unknown'})
