from kernel.ipc import *
from kernel.proc import *
from kernel.fs import *
import uasyncio as asyncio
from machine import *

procs = {fs_proc.pid: fs_proc}
pipes = []

async def send(pipe_id, data, pid):
    if pid not in procs or pipe_id not in procs[pid].pipes:
        print(f"[KERNEL]: Send Error: PID {pid} has no pipe {pipe_id}")
        return 0
    pipe_obj, side = procs[pid].pipes[pipe_id]
    await pipe_obj.write(side, data)

async def recv(pipe_id, pid):
    if pid not in procs or pipe_id not in procs[pid].pipes:
        print(f"[KERNEL]: Recv Error: PID {pid} has no pipe {pipe_id}")
        return 0
    pipe_obj, side = procs[pid].pipes[pipe_id]
    return await pipe_obj.read(side)

def create_proc(func_text, prio):
    p = Proc(func_text, prio)
    procs[p.pid] = p
    return p.pid

def create_pipe():
    global pipes
    pipes.append(Pipe())
    return len(pipes) - 1

def connect(pid, local_id, global_id, side):
    if pid not in procs: return 0
    procs[pid].pipes[local_id] = (pipes[global_id], side)
    
async def run_proc(pid):
    p = procs[pid]
    p.state = RUNNING
    
    ctx = {
        "pid": pid, "send": send, "recv": recv, "asyncio": asyncio,
        "os": None, "eval": None, "SLEEP_TIME": 0.020,
        "create_pipe": create_pipe,
        "connect": lambda local_id, side: connect(pid, local_id, create_pipe(), side),
        "machine": None, "gc": None, "micropython": None,
        "__import__": None, "importlib": None,
        "timer": Timer
    }
    if p.server:
        ctx['fs'] = fs
    
    wrapper = f"async def _task_{pid}():\n"
    for line in p.func.split('\n'):
        if line.strip(): wrapper += f"    {line}\n"
    
    try:
        exec(compile(wrapper, f"<task_{pid}>", 'exec'), ctx)
        await ctx[f"_task_{pid}"]()
    except Exception as err:
        print(f"[KERNEL]: Error in task {pid}: {err}")
    finally:
        if p.server:
            return 0
        p.state = CLOSED

async def scheduler():
    print("[KERNEL]: Scheduler started.")
    
    for pid in sorted(procs.keys(), key=lambda p: procs[p].prio, reverse=True):
        procs[pid].state = RUNNING
        asyncio.create_task(run_proc(pid))
    
    while True:
        for pid, p in procs.items():
            if p.server and p.state == CLOSED:
                asyncio.create_task(run_proc(pid))
        
        active_procs = [p for p in procs.values() if p.state == RUNNING]
        if not active_procs:
            print("[KERNEL]: All processes finished. System idle.")
        
        await asyncio.sleep(0.020)

def boot():
    print("[BOOT]: Initializing Kernel...")
    
    fs_bus = create_pipe() 

    fs_pid = fs_proc.pid
    for p_id, p in procs.items():
        if p.server:
            connect(p_id, 0, fs_bus, 0) 
        else:
            connect(p_id, 0, fs_bus, 1) 
            reply_bus = create_pipe()
            connect(p_id, 1, reply_bus, 0)
            connect(fs_pid, p_id, reply_bus, 1)
        
    print(f"[BOOT]: {len(procs)} processes linked via Pech-pipes.")