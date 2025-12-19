# Pech
A complete rework of the PearKernel.

Of course, a main.py is already written for you to make it easier to understand what's going on.

I highly recommend reading up on IPC (real "adult" pipes, not those mailbox-style ones).

By checking out the FS server source code, the main.py file, and reading about Mach 3.0, you’ll be able to dive right in.

# Why am I so sure?
Simple: the Pech kernel doesn't have things like "61 system calls."

Everything is crystal clear:

Want to read a file? Send a message to the FS server.

Here is what an FS message looks like:

{"client_pid": <your pid>, "reply_pipe": <pipe id for the response>, "cmd": <command>,

"path": <any vfs path (recommended to read files.txt)>, "data": <data to write, only for 'write' command>,

"permissions": <permissions (see below), only for 'mkdir' and 'write'>}

# Kernel Concepts
Here they are:
* The Kernel is a Process Assistant: It should only help get the work done, not do the work for the process.
* Security and Stability Above All: The kernel must prevent a process from doing anything malicious by any means necessary.
* Zero Tolerance for Risk: Anything that compromises security (e.g., dangerous libraries) must be nullified.
* Servers provide Safety: Servers allow processes to perform operations more securely.
* IPC is Everything: IPC is the best thing ever invented. Any kernel version without IPC cannot be considered "Pech-like."
* Dynamic Programs are Vital: Without them, the VFS can be considered worthless.
* VFS is its own thing: VFS is not just a controller for physical filesystems. It is a separate filesystem with its own files.
* Everything in its Place: No redundant "utility" files with 600 lines of code.

# Permissions
A lightweight permission structure:

For files:

* r or nr (Read / No Read)
* w or nw (Write / No Write)
* d or cd (Delete / Cannot Delete)

Note: Changing permissions is currently not supported.

For folders:

Only d or cd.

# Support
Here is my Gmail:

dimasoft976@gmail.com

Feel free to write whatever you want there.

Happy developing!
