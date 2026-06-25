import argparse
import json
import sys
import os
import subprocess
import textwrap
import pymem.process
import win32api
import win32con
import win32process


STEAM_ENV_TEMPLATE_FILENAME = "steam-env.json"

STEAM_ENV_TEMPLATE = {
    "SteamClientLaunch": "1",
    "SteamEnv": "1",
    "SteamPath": r"C:\Program Files (x86)\Steam",
    "ValvePlatformMutex": "c:/program files (x86)/steam/steam.exe",
}


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


def load_env_file(filename):
    with open(filename, "r", encoding="utf-8") as env_file:
        env = json.load(env_file)
    if not isinstance(env, dict):
        raise ValueError("env file must contain a JSON object")
    return {str(key): str(value) for key, value in env.items()}


def parse_env_vars(env_vars):
    env = {}
    for item in env_vars or []:
        key, separator, value = item.partition("=")
        if separator == "" or key == "":
            raise ValueError("--env values must use KEY=VALUE with a non-empty key")
        env[key] = value
    return env


def build_environment(env_file=None, env_vars=None):
    if env_file is None and not env_vars:
        return None

    environment = os.environ.copy()
    if env_file is not None:
        environment.update(load_env_file(env_file))
    environment.update(parse_env_vars(env_vars))
    return environment


def build_steam_env_template(steam_id):
    steam_id = str(steam_id)
    env = {
        "SteamAppId": steam_id,
        "SteamGameId": steam_id,
        "SteamOverlayGameId": steam_id,
    }
    env.update(STEAM_ENV_TEMPLATE)
    return env


def write_steam_env_template(steam_id, filename=STEAM_ENV_TEMPLATE_FILENAME):
    with open(filename, "x", encoding="utf-8") as template_file:
        json.dump(build_steam_env_template(steam_id), template_file, indent=4)
        template_file.write("\n")


def create_suspended_process(exe_path, command_line=None, environment=None):
    startup_info = win32process.STARTUPINFO()
    current_directory = os.path.dirname(exe_path)

    try:
        process_information = win32process.CreateProcess(
            exe_path,
            command_line,
            None,
            None,
            False,
            win32con.CREATE_SUSPENDED,
            environment,
            current_directory,
            startup_info,
        )
    except Exception as error:
        raise RuntimeError(f"failed to create suspended process: {error}") from error
    return process_information


def main():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""\
            Inject a DLL into a running Windows process by PID or process name, or
            launch an executable suspended, inject the DLL before the primary thread
            resumes, and then continue the process.

            Launch mode supports optional target command-line arguments and custom
            environment variables through --env or --env-file. Use
            --generate-steam-env-template to create a starter steam-env.json file.
            """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('-p', '--pid', type=int, help='Proces PID')
    parser.add_argument('-n', '--name', type=str, help='Process name')
    parser.add_argument('-e', '--exe', type=str, help='Executable')
    parser.add_argument('-d', '--dll', default=None, help='DLL file')
    parser.add_argument('-l', '--list', default=False, action='store_true', help='List processes')
    parser.add_argument('--env', action='append', default=None, metavar='KEY=VALUE',
                        help='Environment variable for --exe launch mode')
    parser.add_argument('--env-file', default=None, help='JSON env file for --exe launch mode')
    parser.add_argument('--generate-steam-env-template', default=None, metavar='STEAM_ID',
                        help='Write a Steam env JSON template and exit')
    parser.add_argument(
        '--exe-command-line',
        nargs=argparse.REMAINDER,
        default=None,
        help='Pass the executable path and optional remaining arguments as the launch command line',
    )

    args = parser.parse_args()

    if args.generate_steam_env_template is not None:
        try:
            write_steam_env_template(args.generate_steam_env_template)
        except FileExistsError:
            parser.error(f"{STEAM_ENV_TEMPLATE_FILENAME} already exists")
        print(f"Wrote {STEAM_ENV_TEMPLATE_FILENAME}")
        sys.exit(0)

    if args.list:
        for process in pymem.process.list_processes():
            print(f"{process.th32ProcessID}:\t{get_process_name(process)}")
        sys.exit(0)

    if args.dll is None:
        parser.error("--dll is required unless --list is used")

    targets = [args.pid is not None, args.name is not None, args.exe is not None]
    if sum(targets) != 1:
        parser.error("exactly one of --pid, --name, or --exe is required")

    if args.exe_command_line is not None and args.exe is None:
        parser.error("--exe-command-line requires --exe")

    if (args.env is not None or args.env_file is not None) and args.exe is None:
        parser.error("--env and --env-file require --exe")

    dll_full_path = os.path.abspath(args.dll)

    if args.exe is not None:
        # Launch paused process, inject the DLL, then resume the target's primary thread.
        exe_full_path = os.path.abspath(args.exe)
        command_line = None
        if args.exe_command_line is not None:
            command_line = subprocess.list2cmdline([exe_full_path] + args.exe_command_line)
        try:
            environment = build_environment(args.env_file, args.env)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            parser.error(str(error))
        process_information = None
        resumed = False
        try:
            try:
                process_information = create_suspended_process(exe_full_path, command_line, environment)
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
