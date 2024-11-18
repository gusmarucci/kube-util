# -*- coding: utf-8 -*-
#
#  certificates.py
#
#  Copyright 2024
#  Autor......: Gustavo Marucci <gustavo@marucciviana.com.br>
#  Data.......: 07/11/2024
#  Descrição..: Controle manutenção dos certificados digitais necessários 
#               para o funcionamento dos serviços do Kubernetes
#
#
import 	os
import	re
import 	sys
import	ipaddress
from 	OpenSSL							import crypto
from 	classes.varglobal				import Global


class Certificates(object):

	pkey_path: str	= None
	csr_path: str	= None
	cert_path: str	= None

	def __init__(self) -> None:
		self.pkey_path	= os.path.join(Global.base_path, "pki", "keys")
		self.csr_path	= os.path.join(Global.base_path, "pki", "csr")
		self.cert_path	= os.path.join(Global.base_path, "pki", "crt")


	def read_pkey(self, name: str) -> crypto.PKey | None:
		'''
		read_pkey
		Le a chave privada do arquivo

		'''

		try:
			# Private key file absolute path
			file = f"{self.pkey_path}/{name}.key"

			with open(file, "rb") as k: 
				key_pem = k.read() 
			
			return crypto.load_privatekey(crypto.FILETYPE_PEM, key_pem) 
		
		except:
			return None

		
	def gen_pkey(self, name: str) -> bool:
		'''
		pkey
		Gera a chave privada

		'''
		try:
			# Private key file absolute path
			file = f"{self.pkey_path}/{name}.key"

			# 2048 private key gen
			private_key = crypto.PKey() 
			private_key.generate_key(crypto.TYPE_RSA, 2048) 
			
			# Save it
			with open(file, "wb") as k: 
				k.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key))

			return True

		except Exception as e:
			print(f"Falha ao gerar a chave privada: {str(e)}")
			return False
		

	def read_csr(self, name: str) -> crypto.X509Req | None:
		'''
		read_csr
		Lê o arquivo de CSR

		'''
		try:
			# CSR file absolute path
			file = f"{self.csr_path}/{name}.csr"

			with open(file, "rb") as c: 
				csr_data = c.read() 
			
			return crypto.load_certificate_request(crypto.FILETYPE_PEM, csr_data)
		
		except:
			return None
		

	def gen_csr(self, name: str, subject: str, extensions: list = None) -> bool:
		'''
		gen_csr
		Gerar a solicitação de certificado
	
		'''
		# try to open the key
		try:
			pkey = self.read_pkey(name)
			if pkey is None:
				raise
		except:
			print(f"Falha ao abrir a chave privada.")
			return False
		
		# Extract CN and O from the subject string
		pattern = r"/CN=(?P<CN>[^/]+)/O=(?P<O>[^/]+)" 
		match = re.search(pattern, subject)
		
		if not match or not match.group("CN") or not match.group("O"):
			print(f"Campo \"subject\" inválido: \"{subject}\"")
			return False
				
		
		# Create a sign request
		try:
			req = crypto.X509Req()
			req.get_subject().CN = match.group("CN")
			req.get_subject().O = match.group("O") 
			req.set_pubkey(pkey)
			

			# Add extenstions if exists
			if extensions:
				req.add_extensions(extensions)

			req.sign(pkey, 'sha256')
			
			# Salvar a solicitação em um arquivo
			file = f"{self.csr_path}/{name}.csr"
			
			with open(file, "wb") as csr_file: 
				csr_file.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, req))
			
			return True

		except Exception as e:
			print(f"Falha ao gerar csn de \"{name}\": {str(e)}")
			return False


	def read_certificate(self, name) -> crypto.X509:
		'''
		read_certificate
		Le os dados do certificado

		'''
		try:
			file = f"{self.cert_path}/{name}.crt"
			with open(file, "rb") as c: 
				cert_data = c.read() 
			
			return crypto.load_certificate(crypto.FILETYPE_PEM, cert_data) 
		
		except:
			return None

	def gen_certificate(self, name:str, extensions: list = None, expires:int = 3) -> bool:
		'''
		gen_certificate
		Gera o certificado digital com o número de anos de validade. 
		Default: Emite certificados de 3 anos de validade
		
		'''
		
		# Try to open the key
		try:
			pkey = self.read_pkey(name)
			if pkey is None:
				raise
		except:
			print(f"Falha ao abrir a chave privada.")
			return False
		
		# Try open the CSR
		try:
			csr_req = self.read_csr(name)
			if csr_req is None:
				raise
		except:
			print(f"Falha ao abrir a chave privada.")
			return False
		
		# Try to open CA cert
		if not name.lower() == "ca":
			try:
				ca_crt = self.read_certificate("ca")
				if ca_crt is None:
					raise
			except:
				print(f"Falha em abrir o certificado da Autoridade Certificadora")
				return False
		
		# Generate certificate
		try:
			cert = crypto.X509()
			if not name.lower() == "ca":
				cert.set_issuer(ca_crt.get_subject()) 
			else:
				cert.set_issuer(csr_req.get_subject())

			cert.set_serial_number(1) 
			cert.gmtime_adj_notBefore(0)
			cert.gmtime_adj_notAfter(expires * 365 * 24 * 60 * 60)
			cert.set_subject(csr_req.get_subject()) 
			cert.set_pubkey(csr_req.get_pubkey()) 
			if extensions:
				cert.add_extensions(extensions) 
			cert.sign(pkey, 'sha256')

		except Exception as e:
			print(f"Falha em gerar o certificado {name}: {str(e)}")
			return False
		
		# Save to file
		try:
			file = f"{self.cert_path}/{name}.crt"
			with open(file, "wb") as c:
				c.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

			return True

		except Exception as e:
			print(f"Falha em salvar o certificado {name}: {str(e)}")
			return False

	
	def get_extensions(self, extension_preset: str, iplist: list = []) -> list:
		'''
		get_extensions
		Retorna uma lista de extensões X.509

		'''
		# Define the IP list entries 
		ip_entries = ", ".join([f"IP:{ip}" for ip in iplist]) if iplist else ""

		match extension_preset:
			case "clientAuth":
				return [
					crypto.X509Extension(b"basicConstraints", True, b"CA:FALSE"), 
					crypto.X509Extension(b"keyUsage", True, b"nonRepudiation, digitalSignature, keyEncipherment"), 
					crypto.X509Extension(b"extendedKeyUsage", True, b"clientAuth")
				]
			
			case "serverAuth":
				return [
					crypto.X509Extension(b"basicConstraints", True, b"CA:FALSE"), 
					crypto.X509Extension(b"keyUsage", True, b"nonRepudiation, digitalSignature, keyEncipherment"), 
					crypto.X509Extension(b"extendedKeyUsage", True, b"serverAuth"), 
					crypto.X509Extension(b"subjectAltName", False, f"DNS:kubernetes, DNS:kubernetes.default, DNS:kubernetes.default.svc, " f"DNS:kubernetes.default.svc.cluster, DNS:kubernetes.default.svc.cluster.local, " f"IP:127.0.0.1, {ip_entries}".encode() )
				]
			
			case "altName":
				return [
					crypto.X509Extension(b"basicConstraints", True, b"CA:FALSE"), 
					crypto.X509Extension(b"keyUsage", True, b"nonRepudiation, digitalSignature, keyEncipherment"), 
					crypto.X509Extension(b"subjectAltName", False, ip_entries.encode())
				]

			case _:
				return None
	

	def execute(self, args) -> None:
		'''
		execute
		
		'''
		args 	= vars(args)

		# New or update certificates
		new		= args['new'] or (args['new'] == False and args['update'] == False)
		new 	= False if args['update'] else new

		# Read configuration
		Global.config.run()

		match args['type']:

			case "ca":
				self.ca(new)
			
			case "api":
				self.API(new)

			case "admin":
				self.admin(new)

			case "controller-manager":
				self.controller_manager(new)
			
			case "proxy":
				self.proxy(new)
			
			case "scheduler":
				self.scheduler(new)
			
			case "etcd":
				self.etcd(new)
			
			# all certificates
			case _:
				self.all(new)


	def all(self, new: bool = False) -> None:
		'''
		all
		Create or update all certificates necessary to install Kubernetes

		'''
		self.ca()
		self.API()
		self.admin()
		self.controller_manager()
		self.proxy()
		self.scheduler()
		self.etcd()


	def ca(self, new: bool = False) -> None:
		'''
		ca
		Create or update Certified Authority sign and certificates
		
		'''
		# Verify the key
		ca_key = os.path.join(self.pkey_path, "ca.key")
		if not os.path.exists(ca_key):
			print("Vamos primeiro criar uma chave privada para a Autoridade Certificadora...")
			if not self.gen_pkey("ca"):
				sys.exit(5)
			print("Chave privada da Autoridade Certificadora gerada.\n")
				
		# Generate CSR
		print("Criando CSR para Autoridade Certificadora...")
		if not self.gen_csr(
			name 		= "ca", 
			subject		= "/CN=KUBERNETES-CA/O=Kubernetes"
		):
			sys.exit(5)
		print("- CSR gerado!\n")

		# Sign a certificate
		print("Assinando um certificado para Autoridade Certificadora...")
		if not self.gen_certificate("ca"):
			sys.exit(5)
		print("- Certificado gerado!\n")

	
	def API(self, new: bool = False) -> None:
		'''
		API
		Create or update API sign and certificates
		
		'''
		
		#
		# API Server certificate
		#

		iplist = []
		try:
			cidr 			= 	ipaddress.ip_network(Global.config.values.cidr.service)
			api_server_ip 	= cidr[1]

			iplist.append(api_server_ip)

		except Exception as e:
			print("Não foi possível determinar o IP do Kubernetes API Server")
			sys.exit(5)

		# Verify the key
		kube_apiserver_key = os.path.join(self.pkey_path, "kube-apiserver.key")
		if not os.path.exists(kube_apiserver_key):
			print("Vamos primeiro criar uma chave privada para o serviço API Server...")
			if not self.gen_pkey("kube-apiserver"):
				sys.exit(5)
			print("Chave privada do serviço API Server gerada.\n")
				
		# Generate CSR
		print("Criando CSR para serviço API Server...")
		
		# IP list
		for item in Global.config.values.master_nodes:
			iplist.append(item.ip)

		try:
			iplist.append(Global.config.values.loadbalancer.ip)
		except:
			pass
		
		extensions = self.get_extensions("serverAuth", iplist)
		if not self.gen_csr(
			name 		= "kube-apiserver", 
			subject		= "/CN=kube-apiserver/O=Kubernetes",
			extensions	= extensions
		):
			sys.exit(5)
		print("- CSR gerado!\n")

		# Sign a certificate
		print("Assinando um certificado para serviço API Server...")
		if not self.gen_certificate("kube-apiserver", extensions):
			sys.exit(5)
		print("- Certificado gerado!\n")


		#
		# API Server Kubelet Client (Certificate for Kubelet)
		#

		# Verify the key
		api_kubelet_key = os.path.join(self.pkey_path, "apiserver-kubelet-client.key")
		if not os.path.exists(api_kubelet_key):
			print("Vamos primeiro criar uma chave privada para o serviço API Server para Kubelet Client...")
			if not self.gen_pkey("apiserver-kubelet-client"):
				sys.exit(5)
			print("Chave privada do serviço API Server para Kubelet Client gerada.\n")

		# Generate CSR
		print("Criando CSR para serviço API Server para Kubelet Client...")
				
		extensions = self.get_extensions("clientAuth")
		if not self.gen_csr(
			name 		= "apiserver-kubelet-client", 
			subject		= "/CN=kube-apiserver-kubelet-client/O=system:masters",
			extensions	= extensions
		):
			sys.exit(5)
		print("- CSR gerado!\n")

		# Sign a certificate
		print("Assinando um certificado para serviço API Server para Kubelet Client...")
		if not self.gen_certificate("apiserver-kubelet-client", extensions):
			sys.exit(5)
		print("- Certificado gerado!\n")

	
	def admin(self, new: bool = False) -> None:
		'''
		admin
		Create or update admin user sign and certificates
		
		'''
		# Verify the key
		admin_key = os.path.join(self.pkey_path, "admin.key")
		if not os.path.exists(admin_key):
			print("Vamos primeiro criar uma chave privada para o usuário admin...")
			if not self.gen_pkey("admin"):
				sys.exit(5)
			print("Chave privada do usuário admin gerada.\n")
				
		# Generate CSR
		print("Criando CSR para o certificado do usuário admin...")
		if not self.gen_csr(
			name 		= "admin", 
			subject		= "/CN=admin/O=system:masters"
		):
			sys.exit(5)
		print("- CSR gerado!\n")

		# Sign a certificate
		print("Assinando o certificado do usuário admin...")
		if not self.gen_certificate("admin"):
			sys.exit(5)
		print("- Certificado gerado!\n")

	
	def controller_manager(self, new: bool = False) -> None:
		'''
		controller_manager
		Create or update Controller Manager service user sign and certificates
		
		'''
		# Verify the key
		cm_key = os.path.join(self.pkey_path, "kube-controller-manager.key")
		if not os.path.exists(cm_key):
			print("Vamos primeiro criar uma chave privada para o serviço Controller Manager...")
			if not self.gen_pkey("kube-controller-manager"):
				sys.exit(5)
			print("Chave privada do serviço Controller Manager gerada.\n")
				
		# Generate CSR
		print("Criando CSR para o certificado do serviço Controller Manager...")
		if not self.gen_csr(
			name 		= "kube-controller-manager", 
			subject		= "/CN=system:kube-controller-manager/O=system:kube-controller-manager"
		):
			sys.exit(5)
		print("- CSR gerado!\n")

		# Sign a certificate
		print("Assinando o certificado do serviço Controller Manager...")
		if not self.gen_certificate("kube-controller-manager"):
			sys.exit(5)
		print("- Certificado gerado!\n")

	
	def proxy(self, new: bool = False) -> None:
		'''
		proxy
		Create or update Proxy service user sign and certificates
		
		'''
		# Verify the key
		proxy_key = os.path.join(self.pkey_path, "kube-proxy.key")
		if not os.path.exists(proxy_key):
			print("Vamos primeiro criar uma chave privada para o serviço Proxy...")
			if not self.gen_pkey("kube-proxy"):
				sys.exit(5)
			print("Chave privada do serviço Proxy gerada.\n")
				
		# Generate CSR
		print("Criando CSR para o certificado do serviço Proxy...")
		if not self.gen_csr(
			name 		= "kube-proxy", 
			subject		= "/CN=system:kube-proxy/O=system:node-proxier"
		):
			sys.exit(5)
		print("- CSR gerado!\n")

		# Sign a certificate
		print("Assinando o certificado do serviço Proxy...")
		if not self.gen_certificate("kube-proxy"):
			sys.exit(5)
		print("- Certificado gerado!\n")

	
	def scheduler(self, new: bool = False) -> None:
		'''
		scheduler
		Create or update Scheduler service user sign and certificates
		
		'''
		# Verify the key
		sched_key = os.path.join(self.pkey_path, "kube-scheduler.key")
		if not os.path.exists(sched_key):
			print("Vamos primeiro criar uma chave privada para o serviço Scheduler...")
			if not self.gen_pkey("kube-scheduler"):
				sys.exit(5)
			print("Chave privada do serviço Scheduler gerada.\n")
				
		# Generate CSR
		print("Criando CSR para o certificado do serviço Scheduler...")
		if not self.gen_csr(
			name 		= "kube-scheduler", 
			subject		= "/CN=system:kube-scheduler/O=system:node-proxier"
		):
			sys.exit(5)
		print("- CSR gerado!\n")

		# Sign a certificate
		print("Assinando o certificado do serviço Scheduler...")
		if not self.gen_certificate("kube-scheduler"):
			sys.exit(5)
		print("- Certificado gerado!\n")


	def etcd(self, new: bool = False) -> None:
		'''
		etcd
		Create or update etcd sign and certificates
		
		'''
		iplist = [ "127.0.0.1" ]
	
		# Verify the key
		kube_apiserver_key = os.path.join(self.pkey_path, "etcd.key")
		if not os.path.exists(kube_apiserver_key):
			print("Vamos primeiro criar uma chave privada para o serviço ETCD...")
			if not self.gen_pkey("etcd"):
				sys.exit(5)
			print("Chave privada do serviço ETCD gerada.\n")
				
		# Generate CSR
		print("Criando CSR para serviço ETCD...")
		
		# IP list
		for item in Global.config.values.master_nodes:
			iplist.append(item.ip)
		
		extensions = self.get_extensions("altName", iplist)
		if not self.gen_csr(
			name 		= "etcd", 
			subject		= "/CN=etcd-server/O=Kubernetes",
			extensions	= extensions
		):
			sys.exit(5)
		print("- CSR gerado!\n")

		# Sign a certificate
		print("Assinando um certificado para serviço API Server...")
		if not self.gen_certificate("etcd", extensions):
			sys.exit(5)
		print("- Certificado gerado!\n")

