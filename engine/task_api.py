from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from . import task_runner

router = APIRouter(prefix='/engine/tasks', tags=['engine-tasks'])

class TaskIn(BaseModel):
    name: str
    args: dict | None = None

@router.post('/submit')
def submit_task(task: TaskIn):
    if task.name not in task_runner._TASKS:
        raise HTTPException(status_code=400, detail=f'Unknown task: {task.name}')
    job_id = task_runner.submit(task.name, task.args or {})
    return {'ok': True, 'job_id': job_id}

@router.get('/status/{job_id}')
def get_status(job_id: str):
    return task_runner.status(job_id)

@router.get('/list')
def list_tasks():
    return {'available': sorted(list(task_runner._TASKS.keys()))}
