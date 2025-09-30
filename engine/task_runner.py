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

# Workspace KPI tasks
def task_compute_kpis(data_dir: str = 'data', write: bool = True, verbose: bool = False):
    """Compute KPIs and optionally write metrics file."""
    import subprocess
    import sys
    cmd = [sys.executable, f'{data_dir}/tools/compute_kpis.py', '--data-dir', data_dir]
    if write:
        cmd.append('--write')
    if verbose:
        cmd.append('--verbose')
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        'returncode': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr
    }

def task_build_dashboard(data_dir: str = 'data', days: int = 7, verbose: bool = False):
    """Build HTML dashboard from metrics files."""
    import subprocess
    import sys
    cmd = [sys.executable, f'{data_dir}/tools/build_dashboard.py', 
           '--data-dir', data_dir, '--days', str(days)]
    if verbose:
        cmd.append('--verbose')
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        'returncode': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr
    }

def task_dispatch_alerts(data_dir: str = 'data', flush: bool = False, 
                        dry_run: bool = False, verbose: bool = False):
    """Dispatch queued alerts outside quiet hours."""
    import subprocess
    import sys
    cmd = [sys.executable, f'{data_dir}/tools/alert_dispatch.py', '--data-dir', data_dir]
    if flush:
        cmd.append('--flush')
    if dry_run:
        cmd.append('--dry-run')
    if verbose:
        cmd.append('--verbose')
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        'returncode': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr
    }

# Register workspace tasks
_TASKS.update({
    'compute_kpis': task_compute_kpis,
    'build_dashboard': task_build_dashboard,
    'dispatch_alerts': task_dispatch_alerts
})

def register(name, fn):
    _TASKS[name]=fn

def submit(name, args=None):
    job_id = str(uuid.uuid4())
    _JOBS[job_id] = {'status':'queued','result':None,'error':None,'name':name,'args':args or {},'started_at':None,'finished_at':None}
    _Q.put(job_id)
    return job_id

def status(job_id):
    return _JOBS.get(job_id, {'status':'unknown'})
