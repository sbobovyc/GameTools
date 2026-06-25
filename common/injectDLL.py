import argparse
import sys
import os
import pymem.process
import win32api
import win32con
import win32process


def load_dll(pid, filename):
    handle = pymem.process.open(pid, debug=True)
    try:
        return pymem.process.inject_dll_from_path(handle, filename)
    finally:
        pymem.process.close_handle(handle)


def get_process_name(process):
    name = process.szExeFile
    if isinstance(name, bytes):
        name = name.split(b"\x00", 1)[0].decode("mbcs", "replace")
    else:
        name = str(name).split("\x00", 1)[0]
    return name


def find_pid_by_name(name):
    name = os.path.basename(name).lower()
    for process in pymem.process.list_processes():
        process_name = get_process_name(process)
        if process_name.lower() == name:
            return process.th32ProcessID
    return None


def create_suspended_process(exe_path):
    startup_info = win32process.STARTUPINFO()
    current_directory = os.path.dirname(exe_path)
    try:
        process_information = win32process.CreateProcess(
            exe_path,
            None,
            None,
            None,
            False,
            win32con.CREATE_SUSPENDED,
            None,
            current_directory,
            startup_info,
        )
    except Exception as error:
        raise RuntimeError(f"failed to create suspended process: {error}") from error
    return process_information


def main():
    parser = argparse.ArgumentParser(description='Inject dll into process')
    parser.add_argument('-p', '--pid', type=int, help='Proces PID')
    parser.add_argument('-n', '--name', type=str, help='Process name')
    parser.add_argument('-e', '--exe', type=str, help='Executable')
    parser.add_argument('-d', '--dll', default=None, help='DLL file')
    parser.add_argument('-l', '--list', default=False, action='store_true', help='List processes')

    args = parser.parse_args()

    if args.list:
        for process in pymem.process.list_processes():
            print(f"{process.th32ProcessID}:\t{get_process_name(process)}")
        sys.exit(0)

    if args.dll is None:
        parser.error("--dll is required unless --list is used")

    targets = [args.pid is not None, args.name is not None, args.exe is not None]
    if sum(targets) != 1:
        parser.error("exactly one of --pid, --name, or --exe is required")

    dll_full_path = os.path.abspath(args.dll)

    if args.exe is not None:
        # Launch paused process, inject the DLL, then resume the target's primary thread.
        exe_full_path = os.path.abspath(args.exe)
        process_information = None
        resumed = False
        try:
            try:
                process_information = create_suspended_process(exe_full_path)
            except RuntimeError as error:
                parser.error(str(error))
            process_handle, thread_handle, pid, _thread_id = process_information
            print(f"Injecting {args.dll} into {pid}")
            load_dll(pid, dll_full_path)
            win32process.ResumeThread(thread_handle)
            resumed = True
        finally:
            if process_information is not None:
                if not resumed:
                    try:
                        win32process.TerminateProcess(process_handle, 1)
                    except Exception:
                        pass
                win32api.CloseHandle(process_handle)
                win32api.CloseHandle(thread_handle)
        sys.exit(0)

    pid = args.pid

    if args.name is not None:
        pymem.process.set_debug_privilege("SeDebugPrivilege", True)
        pid = find_pid_by_name(args.name)
        if pid is None:
            sys.exit(0)

    print(f"Injecting {args.dll} into {pid}")
    load_dll(pid, dll_full_path)


if __name__ == "__main__":
    main()


