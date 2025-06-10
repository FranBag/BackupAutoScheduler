import paramiko

router_ip = "192.168.56.120"
username = "usuario"
password = "pass"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(router_ip, username=username, password=password)

stdin, stdout, stderr = ssh.exec_command("/interface print")
print(stdout.read().decode())

ssh.close()
