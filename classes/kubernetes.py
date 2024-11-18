# -*- coding: utf-8 -*-
#
#  kubernetes.py
#
#  Copyright 2024
#  Autor......: Gustavo Marucci <gustavo@marucciviana.com.br>
#  Data.......: 14/11/2024
#  Descrição..: Funcionalidades do kubectl 
#
#

import	base64
import	yaml
import	os

from	enum 				import Enum
from 	classes.varglobal	import Global


class UserType(Enum):
	ControllerManager 	= "controller-manager"
	Proxy				= "proxy"
	Scheduler			= "scheduler"
	Admin				= "admin"
	

class Kubernetes(object):

	pkey_path: str	= None
	csr_path: str	= None
	cert_path: str	= None

	def __init__(self) -> None:
		self.pkey_path	= os.path.join(Global.base_path, "pki", "keys")
		self.csr_path	= os.path.join(Global.base_path, "pki", "csr")
		self.cert_path	= os.path.join(Global.base_path, "pki", "crt")


	def read_certificate_file(self, file: str) -> str:
		'''
		read_certificate_file
		Le o arquivo de certificado e transforma em base64

		'''

		with open(file, 'rb') as f:
			pem_data = f.read()

		# Remove header and footer lines
		pem_data = pem_data.replace(b'-----BEGIN CERTIFICATE-----\n', b'')
		pem_data = pem_data.replace(b'-----END CERTIFICATE-----\n', b'')

		# Encode the remaining data in Base64
		base64_data = base64.b64encode(pem_data).decode('utf-8')

		return base64_data

	
	def set_kubeconfig(self, **param: dict) -> bool:
		'''
		set_kubeconfig
		Cria um arquivo kubeconfig
		
		'''

		output = None

		try:
			
			server			= param['server']
			cluster			= param['cluster']
			user			= param['user']
			certificate		= param['certificate']
			embended		= param['embended']		if 'embended' in param 	else False
			
			output = {
				"apiVersion": "v1",
				"clusters": [
					{
						"cluster": {
							"certificate-authority": "/var/lib/kubernetes/pki/ca.crt",
							"server": server
						},
						"name": cluster
					}
				],
				"contexts": [
					{
						"context": {
							"cluster": cluster,
							"user": user
						},
						"name": "default"
					}
				],
				"current-context": "default",
				"kind": "Config",
				"preferences": {},
				"users": [
					{
						"name": user,
						"user": dict()
					}
				]
			}

			if embended:
				ca		= self.read_certificate_file(os.path.join(self.cert_path, "ca.crt"))
				cert	= self.read_certificate_file(os.path.join(self.cert_path, f"{certificate}.crt"))
				key		= self.read_certificate_file(os.path.join(self.pkey_path, f"{certificate}.key"))

				output['clusters'][0]['cluster']['certificate-authority-data']	= ca
				output['users'][0]['user']['client-certificate-data']			= cert
				output['users'][0]['user']['client-key-data']					= key
			else:
				output['clusters'][0]['cluster']['certificate-authority']	= "/var/lib/kubernetes/pki/ca.crt"
				output['users'][0]['user']['client-certificate']			= f"/var/lib/kubernetes/pki/{certificate}.crt"
				output['users'][0]['user']['client-key']					= f"/var/lib/kubernetes/pki/{certificate}.key"


			file = os.path.join(Global.base_path, "kubeconfig", f"kube-{certificate}.kubeconfig")
			with open(file, "w") as f:
				yaml.dump(output, f, default_flow_style=False)

			return True
		
		except KeyError as e:
			print(f"Parâmetro faltando: {str(e)}")
			return False
		
		except Exception as e:
			print(f"Erro: {str(e)}")
			return False


