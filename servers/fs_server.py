print(f"[FS]: Server started on PID {pid}")

has_changes = False
write_commands = ['write', 'mkdir', 'rmfile', 'rmdir']

tim = timer(-1)

def saver(t):
    nonlocal has_changes
    if has_changes:
        has_changes = False
        fs.save()

tim.init(mode=timer.PERIODIC, period=500, callback=saver)

while True:
    msg = await recv(0, pid) 
    
    cmd = msg.get('cmd')
    path = msg.get('path')
    reply_pipe = msg.get('reply_pipe')
    client_pid = msg.get('client_pid')
    
    if cmd in write_commands:
        has_changes = True

    result = None
    try:
        if cmd == "ls":
            result = fs.ls(path)
        elif cmd == "cat":
            result = fs.cat(path)
        elif cmd == "write":
            fs.write(path, msg.get('data', ''), msg.get('perms', 'r-w-d'))
            result = "ok"
        elif cmd == 'pwd':
            result = fs.pwd()
        elif cmd == 'rmfile':
            result = fs.rmfile(path)
        elif cmd == 'rmdir':
            result = fs.rmdir(path)
        elif cmd == 'mkdir':
            fs.mkdir(path, msg.get('perms', 'd'))
            result = 'ok'
        elif cmd == 'cd':
            fs.cd(path)
            result = 'ok'
        elif cmd == 'isdir':
            result = fs.isdir(path)
        elif cmd == 'isfile':
            result = fs.isfile(path)
    except Exception as e:
        result = f"error: {str(e)}"

    await send(reply_pipe, result, pid)