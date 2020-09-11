# Devmiko

---
![PyPI - Status](https://img.shields.io/pypi/status/Devmiko)
![PyPI - Format](https://img.shields.io/pypi/format/Devmiko)
![GitHub](https://img.shields.io/github/license/vsantiago113/Devmiko)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/vsantiago113/Devmiko)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Devmiko)

A SSH client for systems network automation.

## Documentation
[Paramiko - SFTPClient](http://docs.paramiko.org/en/stable/api/sftp.html 'SFTPClient')<br />
[Paramiko - SSHClient](http://docs.paramiko.org/en/stable/api/client.html 'SSHClient')

## Dependencies
Paramiko

## How to install
```ignorelang
$ pip install Devmiko
```

## Usage
The client.output holds the full output from all the commands you sent.

#### SSHClient example
```python
import Devmiko

client = Devmiko.SSHClient(debug=False, filename=None, level='DEBUG')
client.connect('remote_host', username='myusername', password='mypassword')

client.send_command('ls')
client.send_command('sudo su', expect_string=r'^.*Password: $')
client.send_command('mypassword')
print(client.output)

client.disconnect()
```

Turn on debugging to help you troubleshoot issues with the SSH connection
```python
import Devmiko

client = Devmiko.SSHClient(debug=True, filename='mylogfile.log', level='DEBUG')
```

You can pass arguments and keyword arguments to the paramiko connection method. Check out the paramiko docs
```python
import Devmiko

client = Devmiko.SSHClient()
client.connect(*args, **kwargs)
```

How to break out of a prompt? You have to pass the keyword argument expect_string with a regex
```python
import Devmiko

client = Devmiko.SSHClient()
client.connect('remote_host', username='myusername', password='mypassword')

client.send_command('sudo su', expect_string=r'^.*Password: $') # Here we are breaking the prompt at Password:
client.send_command('mypassword')

client.disconnect()
```

Using Paramiko methods from the Devmiko channel
```python
import Devmiko
import re

client = Devmiko.SSHClient()
client.connect('remote_host', username='myusername', password='mypassword')

client.channel.sendall('ls\n')
output = ''
while True:
    temp_output = client.channel.recv(4096).encode('UTF-8')
    output += temp_output
    if re.search(r'>\s$', temp_output, flags=re.IGNORECASE | re.MULTILINE):
        break

print(output)

client.disconnect()
```

#### SFTPClient example
For the SFTPClient you need to use the client.channel and use the paramiko methods
```python
import Devmiko

client = Devmiko.SFTPClient()
client.connect('remote_host', username='myusername', password='mypassword')

client.channel.chdir(path='/tmp')
output = client.channel.getcwd()
print(output)
output = client.channel.listdir(path='.')
print(output)
client.channel.get('/tmp/Cleanup.log', 'Downloads/Cleanup.log')

client.disconnect()
```

#### Download Files with Progressbar
```python
import Devmiko

client = Devmiko.SFTPClient()
client.connect('remote_host', username='myusername', password='mypassword')

client.get_with_progressbar(remote_file='/tmp/myfile.tar', local_file='Downloads/myfile.tar')

client.disconnect()
```

#### Upload Files with Progressbar
```python
import Devmiko

client = Devmiko.SFTPClient()
client.connect('remote_host', username='myusername', password='mypassword')

client.put_with_progressbar(local_file='myfile.tar', remote_file='/tmp/myfile.tar')

client.disconnect()
```

#### FTDClient example
The FTDClient include the different Command Line Modes of the FTD so you can enter or switch from mode to mode.
```python
import Devmiko

client = Devmiko.FTDClient(debug=False, filename=None, level='DEBUG')
client.connect('remote_host', username='myusername', password='mypassword')

client.send_command(command='show managers')

client.enter_lina_mode()
client.send_command(command='show run | include hostname')

client.enter_clish_mode()
client.send_command(command='show managers')
client.send_command(command='show failover')

client.enter_diagnostic_cli_mode()
client.send_command(command='show run | include hostname')

client.enter_expert_mode()
client.send_command(command='ls /tmp')

client.enter_regular_mode()
client.send_command(command='show managers')
client.send_command(command='show network')


print(client.output)
client.disconnect()
```
