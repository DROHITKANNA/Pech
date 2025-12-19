import ujson
from kernel.proc import *
from machine import Timer

class VFS:
    def __init__(self):
        with open('user/files.txt', 'r', -1, 'utf-8') as f:
            code = f.read().split('\n')
            self.files = ujson.loads(code[0])
            self.dirs = set(ujson.loads(code[1])) 
            self.permissions = ujson.loads(code[2])
        self.cwd = '/home'
        
    def parse_perms(self, perms):
        return perms.split('-')

    def resolve_path(self, path):
        if path == '.':
            return self.cwd
        elif path.startswith('/'):
            return path
        return self.cwd + '/' + path

    def ls(self, path):
        if path not in self.dirs:
            return f'ls: cannot access \'{path}\': No such directory'
        contents = []
        for p in self.files:
            if p.startswith(path) and p != path:
                rel = p[len(path):].lstrip('/')
                if '/' not in rel or rel.split('/')[0] == '':
                    contents.append(rel.split('/')[0])
        for d in self.dirs:
            if d.startswith(path) and d != path:
                rel = d[len(path):].lstrip('/')
                if '/' not in rel:
                    contents.append(rel + '/')
        return list(sorted(set(contents))) if contents else ''
    
    def isdir(self, path):
        return True if path in self.dirs else False
    
    def isfile(self, path):
        return True if path in self.files else False

    def cat(self, path):
        if path in self.permissions.keys() and self.parse_perms(self.permissions[path])[0] == 'nr':
            return 'cat: cannot read, not have access to read.'
        src = self.files.get(path, f'cat: {path}: No such file')
        if src[0] == 'text':
            return src[1]
        return src

    def write(self, path, data,  permissions='r-w-d'):
        if path in self.permissions.keys() and self.parse_perms(self.permissions[path])[1] == 'nw':
            return 'echo: cannot write, not have access to write.'
        else:
            self.permissions[path] = permissions
        self.files[path] = data
        parts = path.strip('/').split('/')
        for i in range(1, len(parts)):
            self.dirs.add('/' + '/'.join(parts[:i]))
        
    def mkdir(self, path, permissions='d'):
        if path in self.dirs:
            return f'mkdir: cannot create directory {path}: File exists'
        self.dirs.add(path)
        self.permissions[path] = permissions
    
    def rmdir(self, path):
        if not path in self.dirs:
            return f'rmdir: {path}: No such dir'
        elif self.parse_perms(self.permissions[path])[0] == 'cd':
            return 'rmdir: cannot delete dir, not have access to delete'
        self.dirs.remove(path)
    
    def rmfile(self, path):
        if not path in self.files:
            return f'rmfile: {path}: No such file'
        elif self.parse_perms(self.permissions[path])[0] == 'cd':
            return 'rmfile: cannot delete file, not have access to delete'
        del self.files[path]
        
    def cd(self, path):
        if not path in self.dirs:
            return f'cd: {path}: No such dir'
        self.cwd = self.resolve_path(path)
    
    def pwd(self):
        return self.cwd
    
    def save(self):
        with open('user/files.txt', 'w', -1, 'utf-8') as r:
            r.write(ujson.dumps(self.files) + '\n')
            r.write(ujson.dumps(list(self.dirs)) + '\n') 
            r.write(ujson.dumps(self.permissions))
            
fs = VFS()

fs_server = None
with open('/servers/fs_server.py', 'r', -1, 'utf-8') as f:
    fs_server = f.read()

fs_proc = Proc(fs_server, 0, True)
