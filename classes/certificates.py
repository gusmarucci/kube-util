# -*- coding: utf-8 -*-
#
#  certificates.py
#
#  Copyright 2024
#  Autor......: Gustavo Marucci <gustavo.marucci@l5.com.br>
#  Data.......: 07/11/2024
#  Descrição..: Controle manutenção dos certificados digitais necessários 
#               para o funcionamento dos serviços do Kubernetes
#
#
import 	os
import	re
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

		except:
			return False


	def read_certificate(self, name) -> None:
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
			return False

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
			cert.set_serial_number(1) 
			cert.gmtime_adj_notBefore(0)
			cert.gmtime_adj_notAfter(expires * 365 * 24 * 60 * 60)
			cert.set_issuer(self.ca_crt.get_subject())
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

	
	def get_extensions(self, extension_preset: str, iplist: list) -> list:
		'''
		get_extensions
		Retorna uma lista de extensões X.509

		'''
		# Define the IP list entries
		ip_entries = ", ".join([f"IP:{ip}" for ip in iplist]) if iplist else ""

		preset = dict(
			clientAuth = [
				crypto.X509Extension(b"basicConstraints", True, b"CA:FALSE"), 
				crypto.X509Extension(b"keyUsage", True, b"nonRepudiation, digitalSignature, keyEncipherment"), 
				crypto.X509Extension(b"extendedKeyUsage", True, b"clientAuth")
			],
			serverAuth = [
				crypto.X509Extension(b"basicConstraints", True, b"CA:FALSE"), 
				crypto.X509Extension(b"keyUsage", True, b"nonRepudiation, digitalSignature, keyEncipherment"), 
				crypto.X509Extension(b"extendedKeyUsage", True, b"serverAuth"), 
				crypto.X509Extension(b"subjectAltName", False, f"DNS:kubernetes, DNS:kubernetes.default, DNS:kubernetes.default.svc, " f"DNS:kubernetes.default.svc.cluster, DNS:kubernetes.default.svc.cluster.local, " f"IP:127.0.0.1, {ip_entries}".encode() )
			],
			altName = [
				crypto.X509Extension(b"basicConstraints", True, b"CA:FALSE"), 
				crypto.X509Extension(b"keyUsage", True, b"nonRepudiation, digitalSignature, keyEncipherment"), 
				crypto.X509Extension(b"subjectAltName", False, ip_entries.encode())
			]
		)

		return preset.get(extension_preset, None)
	

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
			
			# all certificates
			case _:
				self.all(new)


	def all(self, new: bool = False) -> None:
		'''
		all
		Create or update all certificates necessary to install Kubernetes

		'''
		print("All Certificates")


	def ca(self, new: bool = False) -> None:
		'''
		ca
		Create or update Certified Authority sign and certificates
		
		'''
		# Verify the key
		

	
	def API(self, new: bool = False) -> None:
		'''
		API
		Create or update API sign and certificates
		
		'''
		print("Certificate API")

	
	def admin(self, new: bool = False) -> None:
		'''
		admin
		Create or update admin user sign and certificates
		
		'''
		print("Certificate admin")

	
	def controller_manager(self, new: bool = False) -> None:
		'''
		controller_manager
		Create or update Controller Manager service user sign and certificates
		
		'''
		print("Certificate Controller Manager")

	
	def proxy(self, new: bool = False) -> None:
		'''
		proxy
		Create or update Proxy service user sign and certificates
		
		'''
		print("Certificate Proxy")

	
	def scheduler(self, new: bool = False) -> None:
		'''
		scheduler
		Create or update Scheduler service user sign and certificates
		
		'''
		print("Certificate Scheduler")



	"""
	Load balancer?
	sim - Nome (se não detectar, pedir o IP)

	Quantos Master?
	Qual o nome deles?
	
	Se não detectar o IP por DNS perguntar cada um

	"""