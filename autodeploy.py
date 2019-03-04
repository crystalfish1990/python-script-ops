#!/bin/python36
# coding: utf-8

# 模块导入
import os
import paramiko
import fnmatch
import shutil
import time


# 初始化需要部署的项目名称,主机,分支
ALL_SERVICE = {
	'lzgsl-iac-1.1.0-SNAPSHOT': [['lz1', 'lz3'], 'gsl'],
  'lzsh-firm-1.1.0-SNAPSHOT': [['lz1', 'lz3'], 'sh'],
}

# 初始化匹配的文件后缀, 上传文件规定以tar.gz结尾
patterns = ['*.tar.gz']

os.chdir('/root/upload')
def is_file_match(filename, patterns):
	for pattern in patterns:
		if fnmatch.fnmatch(filename, pattern):
			return True
	return False

def find_specific_files(root, patterns=['*'], exclude_dirs=[]):
	for root, dirnames, filenames in os.walk(root):
		for filename in filenames:
			if is_file_match(filename, patterns):
				yield os.path.join(root, filename)
		for d in exclude_dirs:
			if d in dirnames:
				dirnames.remove(d)

for item in find_specific_files(".", patterns):
	shutil.unpack_archive(item)

deploySrv = []
for file in os.listdir('.'):
	if os.path.isdir(file):
		deploySrv.append(file)

private_key = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
for service in deploySrv:
	print(service)
	timestramp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
	for hostname in ALL_SERVICE[service][0]:
		transport = paramiko.Transport(sock=(hostname, 9527))
		transport.connect(username='root', pkey=private_key)
		sftp = paramiko.SFTPClient.from_transport(transport)
		ssh = paramiko.SSHClient()
		ssh._transport = transport
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		if ALL_SERVICE[service][1] == 'sh':
			sftp.rename('/data/lianzi-sh/{0}/lib'.format(service), '/data/lianzi-sh/{0}/lib-{1}'.format(service, timestramp))
			sftp.mkdir('/data/lianzi-sh/{0}/lib'.format(service))
			localSrvPath = '/root/upload/{}/lib'.format(service)
			remoteBasePath = '/data/lianzi-sh/{}'.format(service)
			remoteDeployPath = '/data/lianzi-sh/{}/lib'.format(service)
			for file in os.listdir(localSrvPath):
				localPath = os.path.join(localSrvPath, file)
				remotePath = os.path.join(remoteDeployPath, file)
				sftp.put(localpath=localPath, remotepath=remotePath)
			#ssh.exec_command('sh {}/bin/restart.sh'.formath(remoteBasePath))
		elif ALL_SERVICE[service][1] == 'gsl':
			sftp.rename('/data/lianzi/{0}/lib'.format(service), '/data/lianzi/{0}/lib-{1}'.format(service, timestramp))
			sftp.mkdir('/data/lianzi/{0}/lib'.format(service))
			localSrvPath = '/root/upload/{}/lib'.format(service)
			remoteBasePath = '/data/lianzi/{}'.format(service)
			remoteDeployPath = '/data/lianzi/{}/lib'.format(service)
			for file in os.listdir(localSrvPath):
				localPath = os.path.join(localSrvPath, file)
				remotePath = os.path.join(remoteDeployPath, file) 
				sftp.put(localpath=localPath, remotepath=remotePath)
			#ssh.exec_command('sh {}/bin/restart.sh'.format(remoteBasePath))
