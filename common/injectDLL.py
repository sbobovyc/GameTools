from __future__ import print_function
import argparse
import sys
import os
import winappdbg
from winappdbg import Process, System


def load_dll(pid, filename):
    # Instance a Process object.
    process = Process(pid)
    
    # Load the DLL library in the process.
    process.inject_dll(filename)


parser = argparse.ArgumentParser(description='Inject dll into process')
parser.add_argument('-p', '--pid', type=int, help='Proces PID')
parser.add_argument('-n', '--name', type=str, help='Process name')
parser.add_argument('-e', '--exe', type=str, help='Executable')
parser.add_argument('-f', '--file', default=None, help='DLL file')
parser.add_argument('-l', '--list', default=False, action='store_true', help='List processes')

args = parser.parse_args()

system = System()
pid = args.pid

#process = system.start_process(args.exe)#, bSuspended=True)
#process = winappdbg.win32.CreateProcess(args.exe)
#print(process)
# Lookup the threads in the process.
#process.scan_threads()

# For each thread in the process...
#for thread in process.iter_threads():
#    print(thread)
    # Resume the thread execution.
    #thread.resume()


if args.list:
    # Now we can enumerate the running processes.
    for process in system:
        print("%d:\t%s" % (process.get_pid(), process.get_filename()))
    sys.exit(0)

if args.name is not None:
    System.request_debug_privileges()    
    process = system.find_processes_by_filename(args.name)
    if len(process) == 0:
        sys.exit(0)        
    pid = process[0][0].get_pid()

if args.file is not None:
    print("Injecting %s into %s" % (args.file, pid))
    file_full_path = os.path.abspath(args.file)
    load_dll(pid, file_full_path)



