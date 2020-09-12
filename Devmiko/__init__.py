import paramiko
import time
import re
import warnings
import sys
import logging
from tqdm import tqdm

warnings.filterwarnings(action='ignore', module='.*paramiko.*')


class DevnetException(Exception):
    pass


class TqdmWrap(tqdm):
    def view_progressbar(self, a, b):
        self.total = b
        self.update(a - self.n)


def set_debug(filename=None, level='DEBUG'):
    logger = logging.getLogger('paramiko')
    level = logging.getLevelName(level)
    logger.setLevel(level)

    fh = logging.FileHandler('paramiko.log' if not filename else filename)

    ch = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


class SSHClient:
    def __init__(self, debug=False, filename=None, level='DEBUG'):
        self.__conn = None
        self.channel = None
        self.output = ''
        self.default_string = r'(?:\$[\s]?)|(?:>[\s]?)|(?:#[\s]?)$'
        self.wait_time = 0.2
        self.buffer = 1024
        self.max_iterations = 100
        self.__password = ''
        self.logger = None
        self.debug = debug
        self.prompt = None

        if debug:
            self.logger = set_debug(filename, level)

    def connect(self, *args, **kwargs):
        self.__password = kwargs.get('password', '')
        expect_string = kwargs.get('expect_string', self.default_string)
        self.__conn = paramiko.SSHClient()
        self.__conn.load_system_host_keys()
        self.__conn.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        try:
            self.__conn.connect(*args, **kwargs)
            self.channel = self.__conn.invoke_shell(width=160, height=2048)
            self.channel.settimeout(5.0)
        except paramiko.ssh_exception as e:
            raise DevnetException(e)
        else:
            count = 0
            while True:
                if count >= self.max_iterations:
                    sys.stdout.write('Max iterations exceeded!')
                    break

                if self.channel.recv_ready():
                    count = 0
                    time.sleep(self.wait_time)

                    self.output += self.channel.recv(self.buffer).decode('UTF-8')
                    if re.search(expect_string, self.output, flags=re.IGNORECASE | re.MULTILINE):
                        break
                else:
                    count += 1
                    time.sleep(self.wait_time)

    def disconnect(self):
        if self.channel:
            self.channel.close()

        if self.__conn:
            self.__conn.close()

    def send_command(self, command='', expect_string=''):
        expect_string = self.default_string if not expect_string else expect_string

        count = 0
        session_output = ''
        while True:
            if count >= self.max_iterations:
                sys.stdout.write('Max iterations exceeded!')
                break

            if self.channel.send_ready():
                try:
                    self.channel.sendall(f'{command}\n')
                except paramiko.ssh_exception as e:
                    raise DevnetException(e)
                else:
                    time.sleep(self.wait_time)
                    break
            else:
                count += 1
                time.sleep(self.wait_time)

        count = 0
        while True:
            if count >= self.max_iterations:
                sys.stdout.write('Max iterations exceeded!')
                break

            if self.channel.recv_ready():
                count += 0
                time.sleep(self.wait_time)

                try:
                    string = self.channel.recv(self.buffer).decode('UTF-8')
                except paramiko.ssh_exception as e:
                    raise DevnetException(e)
                else:
                    if self.debug:
                        self.logger.debug(string)

                    if string:
                        if self.__password in string:
                            string = string.replace(self.__password, '*' * 20)

                    session_output += string
                    self.output += string
                    if re.search(expect_string, string, flags=re.IGNORECASE | re.MULTILINE):
                        self.prompt = session_output.splitlines()[-1]
                        return session_output
            else:
                count += 1
                time.sleep(self.wait_time)


class SFTPClient:
    def __init__(self):
        self.__conn = None
        self.channel = None

    def connect(self, *args, **kwargs):
        self.__conn = paramiko.SSHClient()
        self.__conn.load_system_host_keys()
        self.__conn.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        self.__conn.connect(*args, **kwargs)
        self.channel = self.__conn.open_sftp()

    def disconnect(self):
        if self.channel:
            self.channel.close()

        if self.__conn:
            self.__conn.close()

    def get_with_progressbar(self, remote_file=None, local_file=None):
        with TqdmWrap(ascii=True, unit='b', unit_scale=True) as progressbar:
            self.channel.get(remote_file, local_file, callback=progressbar.view_progressbar)

    def put_with_progressbar(self, local_file=None, remote_file=None):
        with TqdmWrap(ascii=True, unit='b', unit_scale=True) as progressbar:
            self.channel.put(local_file, remote_file, callback=progressbar.view_progressbar)


class FTDClient:
    def __init__(self, debug=False, filename=None, level='DEBUG'):
        self.__conn = None
        self.channel = None
        self.output = ''
        self.default_string = r'(?:\$[\s]?)|(?:>[\s]?)|(?:#[\s]?)$'
        self.wait_time = 0.2
        self.buffer = 1024
        self.max_iterations = 100
        self.__password = ''
        self.logger = None
        self.debug = debug
        self.system_hostname = None
        self.regular_mode = True
        self.diagnostic_cli_mode = False
        self.clish_mode = False
        self.lina_mode = False
        self.expert_mode = False
        self.prompt = None

        if debug:
            self.logger = set_debug(filename, level)

    def connect(self, *args, **kwargs):
        self.__password = kwargs.get('password', '')
        expect_string = kwargs.get('expect_string', self.default_string)
        self.__conn = paramiko.SSHClient()
        self.__conn.load_system_host_keys()
        self.__conn.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        try:
            self.__conn.connect(*args, **kwargs)
            self.channel = self.__conn.invoke_shell(width=160, height=2048)
            self.channel.settimeout(5.0)
        except paramiko.ssh_exception as e:
            raise DevnetException(e)
        else:
            count = 0
            while True:
                if count >= self.max_iterations:
                    sys.stdout.write('Max iterations exceeded!')
                    break

                if self.channel.recv_ready():
                    count = 0
                    time.sleep(self.wait_time)

                    self.output += self.channel.recv(self.buffer).decode('UTF-8')
                    if re.search(expect_string, self.output, flags=re.IGNORECASE | re.MULTILINE):
                        break
                else:
                    count += 1
                    time.sleep(self.wait_time)

    def disconnect(self):
        if self.channel:
            self.channel.close()

        if self.__conn:
            self.__conn.close()

    def send_command(self, command='', expect_string=''):
        expect_string = self.default_string if not expect_string else expect_string

        count = 0
        session_output = ''
        while True:
            if count >= self.max_iterations:
                sys.stdout.write('Max iterations exceeded!')
                break

            if self.channel.send_ready():
                try:
                    self.channel.sendall(f'{command}\n')
                except paramiko.ssh_exception as e:
                    raise DevnetException(e)
                else:
                    time.sleep(self.wait_time)
                    break
            else:
                count += 1
                time.sleep(self.wait_time)

        count = 0
        while True:
            if count >= self.max_iterations:
                sys.stdout.write('Max iterations exceeded!')
                break

            if self.channel.recv_ready():
                count += 0
                time.sleep(self.wait_time)

                try:
                    string = self.channel.recv(self.buffer).decode('UTF-8')
                except paramiko.ssh_exception as e:
                    raise DevnetException(e)
                else:
                    if self.debug:
                        self.logger.debug(string)

                    if string:
                        if self.__password in string:
                            string = string.replace(self.__password, '*' * 20)

                    session_output += string
                    self.output += string
                    if re.search(expect_string, string, flags=re.IGNORECASE | re.MULTILINE):
                        self.prompt = session_output.splitlines()[-1]
                        return session_output
            else:
                count += 1
                time.sleep(self.wait_time)

    def __enter_diagnostic_cli(self):
        output = self.send_command(command='system support diagnostic-cli')
        if re.search(r'(?:>[\s]?$)', output, flags=re.IGNORECASE | re.MULTILINE):
            output = self.send_command(command='enable', expect_string=r'([Pp]assword:\s)|(?:#[\s]?)$')
            if re.search(r'[Pp]assword: $', output, flags=re.IGNORECASE | re.MULTILINE):
                self.send_command(command='\n')
        self.send_command(command='terminal pager 0')

    def __enter_expert(self):
        output = self.send_command(command='expert')
        if re.search(r'(?:$[\s]?$)', output, flags=re.IGNORECASE | re.MULTILINE):
            output = self.send_command(command='sudo su', expect_string=r'([Pp]assword:\s)|(?:#[\s]?)$')
            if re.search(r'[Pp]assword: $', output, flags=re.IGNORECASE | re.MULTILINE):
                self.send_command(command=self.__password)

    def __enter_clish(self):
        output = self.send_command(command='expert')
        if re.search(r'(?:$[\s]?$)', output, flags=re.IGNORECASE | re.MULTILINE):
            output = self.send_command(command='sudo su', expect_string=r'([Pp]assword:\s)|(?:#[\s]?)$')
            if re.search(r'[Pp]assword: $', output, flags=re.IGNORECASE | re.MULTILINE):
                self.send_command(command=self.__password)
        self.send_command(command='clish')

    def __enter_lina(self):
        output = self.send_command(command='expert')
        if re.search(r'(?:$[\s]?$)', output, flags=re.IGNORECASE | re.MULTILINE):
            output = self.send_command(command='sudo su', expect_string=r'([Pp]assword:\s)|(?:#[\s]?)$')
            if re.search(r'[Pp]assword: $', output, flags=re.IGNORECASE | re.MULTILINE):
                self.send_command(command=self.__password)
        output = self.send_command(command='sfconsole')
        if re.search(r'(?:>[\s]?$)', output, flags=re.IGNORECASE | re.MULTILINE):
            output = self.send_command(command='enable', expect_string=r'([Pp]assword:\s)|(?:#[\s]?)$')
            if re.search(r'[Pp]assword: $', output, flags=re.IGNORECASE | re.MULTILINE):
                self.send_command(command='\n')
        self.send_command(command='terminal pager 0')

    def __exit_expert_mode(self):
        self.send_command(command='exit')
        self.send_command(command='exit')

    def __exit_lina_mode(self):
        self.send_command(command='exit')
        self.send_command(command='exit')
        self.send_command(command='exit')
        self.send_command(command='exit')

    def __exit_diagnostic_cli_mode(self):
        self.send_command(command='exit')
        self.send_command(command='exit')

    def __exit_clish_mode(self):
        self.send_command(command='exit')
        self.send_command(command='exit')
        self.send_command(command='exit')

    def enter_regular_mode(self):
        if self.regular_mode:
            pass
        elif self.diagnostic_cli_mode:
            self.__exit_diagnostic_cli_mode()
        elif self.lina_mode:
            self.__exit_lina_mode()
        elif self.expert_mode:
            self.__exit_expert_mode()
        elif self.clish_mode:
            self.__exit_clish_mode()

        self.regular_mode = True
        self.diagnostic_cli_mode = False
        self.lina_mode = False
        self.expert_mode = False
        self.clish_mode = False

    def enter_diagnostic_cli_mode(self):
        if self.regular_mode:
            self.__enter_diagnostic_cli()
        elif self.diagnostic_cli_mode:
            pass
        elif self.lina_mode:
            self.__exit_lina_mode()
            self.__enter_diagnostic_cli()
        elif self.expert_mode:
            self.__exit_expert_mode()
            self.__enter_diagnostic_cli()
        elif self.clish_mode:
            self.__exit_clish_mode()
            self.__enter_diagnostic_cli()

        self.regular_mode = False
        self.diagnostic_cli_mode = True
        self.lina_mode = False
        self.expert_mode = False
        self.clish_mode = False

    def enter_lina_mode(self):
        if self.regular_mode:
            self.__enter_lina()
        elif self.diagnostic_cli_mode:
            self.__exit_diagnostic_cli_mode()
            self.__enter_lina()
        elif self.lina_mode:
            pass
        elif self.expert_mode:
            output = self.send_command(command='sfconsole')
            if re.search(r'(?:>[\s]?$)', output, flags=re.IGNORECASE | re.MULTILINE):
                output = self.send_command(command='enable', expect_string=r'([Pp]assword:\s)|(?:#[\s]?)$')
                if re.search(r'[Pp]assword: $', output, flags=re.IGNORECASE | re.MULTILINE):
                    self.send_command(command='\n')
            self.send_command(command='terminal pager 0')
        elif self.clish_mode:
            self.send_command(command='exit')
            output = self.send_command(command='sfconsole')
            if re.search(r'(?:>[\s]?$)', output, flags=re.IGNORECASE | re.MULTILINE):
                output = self.send_command(command='enable', expect_string=r'([Pp]assword:\s)|(?:#[\s]?)$')
                if re.search(r'[Pp]assword: $', output, flags=re.IGNORECASE | re.MULTILINE):
                    self.send_command(command='\n')
            self.send_command(command='terminal pager 0')

        self.regular_mode = False
        self.diagnostic_cli_mode = False
        self.lina_mode = True
        self.expert_mode = False
        self.clish_mode = False

    def enter_expert_mode(self):
        if self.regular_mode:
            self.__enter_expert()
        elif self.diagnostic_cli_mode:
            self.__exit_diagnostic_cli_mode()
            self.__enter_expert()
        elif self.lina_mode:
            self.send_command(command='exit')
            self.send_command(command='exit')
        elif self.expert_mode:
            pass
        elif self.clish_mode:
            self.send_command(command='exit')

        self.regular_mode = False
        self.diagnostic_cli_mode = False
        self.lina_mode = False
        self.expert_mode = True
        self.clish_mode = False

    def enter_clish_mode(self):
        if self.regular_mode:
            self.__enter_clish()
        elif self.diagnostic_cli_mode:
            self.__exit_diagnostic_cli_mode()
            self.__enter_clish()
        elif self.lina_mode:
            self.send_command(command='exit')
            self.send_command(command='exit')
            self.send_command(command='clish')
        elif self.expert_mode:
            self.send_command(command='clish')
        elif self.clish_mode:
            pass

        self.regular_mode = False
        self.diagnostic_cli_mode = False
        self.lina_mode = False
        self.expert_mode = False
        self.clish_mode = True
