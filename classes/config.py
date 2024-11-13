# -*- coding: utf-8 -*-
#
#  config.py
#
#  Copyright 2024
#  Autor......: Gustavo Marucci <gustavo.marucci@l5.com.br>
#  Data.......: 11/11/2024
#  Descrição..: Controla as configs definidas
#
#

import	os
import	sys
import	socket
import 	ipaddress
import	yaml

from	classes.varglobal import Global

# Constants
CONFIG_FILE			= "kube-util.conf"
YES					= [ "y", "s", "yes", "yeah", "yeap", "sim", "si" ]
NO					= [ "n", "no", "não", "nao", "naum", "na" ]
SUPPORTED_VERSION 	= [ 'v1' ]

# Configuration object
class InstanceMachine(object):

	def __init__(self, hostname: str = None, ip: str = None ) -> None:
		self.hostname	= hostname
		self.ip 		= ip
		
	hostname: str	= None
	ip: str			= None


class CIDR(object):

	def __init__(self, service: str = None, pod: str = None, instance: str = None ) -> None:
		self.service	= service
		self.pod 		= pod
		self.instance	= instance
		
	service: str	= None
	pod: str		= None
	instance: str	= None


class Cluster(object):
	name: str						= None
	cidr: CIDR						= None
	loadbalancer: InstanceMachine	= None
	master_nodes: list				= []
	worker_nodes: list				= []


# Exception class
class ReadConfigFail(Exception): 
	def __init__(self, mensagem): 
		super().__init__(mensagem) 
		self.mensagem = mensagem


# Main class
class Config(object):

	values: Cluster = None
	
	@staticmethod
	def install():
		'''
		install
		Instala o Singletron
		
		'''
		Global.config = Config()


	def check_config(self):
		'''
		check_config
		Verifica se existe alguma config existente
		
		'''
		return os.path.exists(CONFIG_FILE)
	

	def read(self) -> bool:
		'''
		read
		Le as configurações do arquivo. Retorna True se conseguiu ou False se não.
		
		'''
		try:
			# Read config file
			with open(CONFIG_FILE, 'r') as f:
				data = yaml.safe_load(f)

			# Validate config
			self.values = Cluster()

			# Metadata
			if data['version'] not in SUPPORTED_VERSION:
				versions = ', '.join(SUPPORTED_VERSION)
				raise ReadConfigFail(f"Versões de config suportadas: \"{versions}\": Valor encontrado: \"{data['version']}\"")
			
			if data['kind'] != 'kube-util':
				raise ReadConfigFail(f"O valor do campo \"kind\" suportado é \"kube-util\": Valor encontrado: {data['kind']}")
						
			self.values.name = data['metadata']['name']

			# Load balancer
			if 'loadbalancer' in data['spec']:
				self.values.loadbalancer = InstanceMachine(
					hostname	= data['spec']['loadbalancer']['name'],
					ip			= data['spec']['loadbalancer']['ip']
				)
			
			# Master nodes
			for item in data['spec']['masterNodes']:
				self.values.master_nodes.append(
					InstanceMachine(
						hostname	= item['name'],
						ip			= item['ip']
					)
				)

			# Worker nodes
			for item in data['spec']['workerNodes']:
				self.values.worker_nodes.append(
					InstanceMachine(
						hostname	= item['name'],
						ip			= item['ip']
					)
				)

			# CIDR's
			self.values.cidr = CIDR()
			self.values.cidr.service 	= data['spec']['cidr']['service']
			self.values.cidr.pod 		= data['spec']['cidr']['pod']
			self.values.cidr.instance	= data['spec']['cidr']['instance']

			return True
		

		except ReadConfigFail as r:
			# Message
			print (f"Falha ao ler arquivo de configuração: {str(r)}\n")

			# Clear config object
			self.values = None

			return False
		
		except KeyError as k:
			# Message
			print (f"Arquivo de configuração inválido: Valor {str(k)} não encontrado\n")

			# Clear config object
			self.values = None

			return False

		except Exception:
			# Message
			print (f"Não foi possivel ler os dados do cluster.\n")

			# Clear config object
			self.values = None

			return False
		

	def write(self) -> bool:
		'''
		write
		Salva as configurações em um arquivo

		'''
		try:
			if self.values is None:
				raise Exception("Não há configuração para ser salva")
			
			data = dict(
				version 	= "v1",
				kind		= "kube-util",
				metadata 	= dict(
					name		= self.values.name,
				),
				spec		= dict(
					cidr	= dict(
						service 	= self.values.cidr.service,
						pod 		= self.values.cidr.pod,
						instance	= self.values.cidr.instance
					),
					masterNodes = [ dict(ip=item.ip, name=item.hostname) for item in self.values.master_nodes ],
					workerNodes = [ dict(ip=item.ip, name=item.hostname) for item in self.values.worker_nodes ],
				)
			)

			if hasattr(self.values, 'loadbalancer') and self.values.loadbalancer is not None:
				data['spec']['loadbalancer'] = dict(
					ip 		= self.values.loadbalancer.ip,
					name 	= self.values.loadbalancer.name
				)

			with open(CONFIG_FILE, 'w') as f: 
				yaml.dump(data, f, default_flow_style=False)
			
			return True
		

		except Exception as e:
			# Message
			print (f"Não foi possivel gravar os dados do cluster: {str(e)}")

			return False
	

	def print(self) -> None:
		'''
		print
		Mostra as configs na tela

		'''
		if self.values is None:
			return
		
		lb = "Sim" if hasattr(self.values, "loadbalancer") and self.values.loadbalancer is not None else "Não"
		
		print(f"*** Configurações salvas do cluster \"{self.values.name}\"\n")
		print(f"Nome do cluster ................: {self.values.name}")
		print(f"Load balancer ..................: {lb}")
		print(f"Quantidade de Master nodes .....: {len(self.values.master_nodes)}")
		print(f"Quantidade de Worker nodes .....: {len(self.values.worker_nodes)}")

		print(f"\n**** CIDR's ****")
		print(f"CIDR de serviço ................: {self.values.cidr.service}")
		print(f"CIDR dos PODs ..................: {self.values.cidr.pod}")
		print(f"CIDR das instâncias ............: {self.values.cidr.instance}")

		print(f"\n**** Master Nodes ****")
		for i,v in enumerate(self.values.master_nodes):
			print(f"Nome do hostname Master {i + 1:02} .....: {v.hostname}")
			print(f"IP do Master {i + 1:02} ................: {v.ip}")

		print(f"\n**** Worker Nodes ****")
		for i,v in enumerate(self.values.worker_nodes):
			print(f"Nome do hostname Worker {i + 1:02} .....: {v.hostname}")
			print(f"IP do Worker {i + 1:02} ................: {v.ip}")


	def yes_no(self, value: str) -> bool | None:
		'''
		yes_or_no
		Retorna True se Sim, False se Não ou None se não respondeu

		'''
		# clean up the answer
		value = value.lower()
		value = value.strip()

		if value in YES:
			return True
		
		elif value in NO:
			return False
		
		else:
			return None

	
	def ask_yes_no(self, message: str, fail_message: str = "Valor inválido") -> bool:
		'''
		ask_yes_no
		Faz uma pergunta e retorna verdadeiro se sim, ou false se não.

		'''
		while True:
			try:
				question = input(message)
			except:
				return False

			value = self.yes_no(question)
			if value is None:
				print (f"{fail_message}: {question}")
				continue
			break

		return value
	

	def ask(self, message: str, fail_message: str = "Valor inválido") -> str:
		'''
		ask
		Pergunta por um input e se não responder pergunta se quer interromper o programa

		'''
		while True:
			try:
				name = input(message)
			except:
				name = None

			if not name:
				if self.ask_yes_no(f"\n{fail_message}. Deseja cancelar (S/N)? "):
					print("Processo interrompido.")
					sys.exit(1)

			else:
				break

		return name
	

	def ip_address(self, hostname: str) -> str | None:
		'''
		ip_address
		Pega o endereço IP ou retorna None se não conseguir

		'''
		try:
			hostname = hostname.strip()
			return socket.gethostbyname(hostname)
		
		except Exception as e:
			print(f"Não consegui obter o endereço de \"{hostname}\": {str(e)}")
			return None
		

	def parse_ip_address(self, ip: str) -> bool:
		'''
		parse_ip_address
		Verifica se o valor é um IPv4 ou IPv6

		'''
		try: 
			ipaddress.ip_address(ip) 
			return True 
		
		except Exception as e: 
			print(f"Não me parece que {ip} se pareça com um endereço de IP. Erro: {str(e)}")
			return False
		
		
	def parse_cidr(self, cidr: str) -> bool:
		'''
		parse_cidr
		Retorna True se for um cidr válido ou False se não.

		'''
		try: 
			ipaddress.ip_network(cidr, strict=False) 
			return True 
		except Exception as e: 
			print(f"Não me parece que {cidr} se pareça com uma rede válida. Erro: {str(e)}")
			return False
		
	
	def ip_belongs_cidr(self, ip, cidr) -> bool:
		'''
		ip_belongs_cidr
		Verifica se o IP digitado pertence ao cidr

		'''
		try: 
			network = ipaddress.ip_network(cidr, strict=False) 
			address = ipaddress.ip_address(ip) 
			return address in network 
		
		except: 
			return False



	def run(self) -> None:
		'''
		run
		Faz com que a config seja armazenada no objeto. Ou por questionário, ou pelo arquivo de config
		
		'''
		if not self.read():
			answer = self.ask_yes_no("Vou perguntar as informações necessárias antes de começar. Tudo bem (S/N) ? ")
			if not answer:
				sys.exit(1)

			self.questions()

		else:
			self.print()


	def questions(self) -> None:
		'''
		questions
		Roda uma sequencia de perguntas para gerar um arquivo de configuração
		
		'''
		cidr_service	= None
		cidr_pods		= None
		cidr_instance	= None
		loadbalancer 	= None
		loadbalancer_ip	= None

		masters			= None
		workers			= None

		# Cluster name
		self.values = Cluster()
		self.values.name = self.ask("Digite o nome do Cluster: ")

		# Service CIDR
		self.values.cidr = CIDR()
		while True:
			cidr_service = self.ask("Digite a rede de serviço (CIDR - Exemplo: 10.96.0.0/16): ")
			if self.parse_cidr(cidr_service):
				break

		self.values.cidr.service = cidr_service
		
		# PODs CIDR
		while True:
			cidr_pods = self.ask("Digite a rede dos PODs (CIDR - Exemplo: 192.168.0.0/16): ")
			if self.parse_cidr(cidr_pods):
				break
		
		self.values.cidr.pod = cidr_pods

		# Instance CIDR
		while True:
			cidr_instance = self.ask("Digite a rede das instâncias (CIDR - Exemplo: 10.100.0.0/16): ")
			if self.parse_cidr(cidr_instance):
				break

		self.values.cidr.instance = cidr_instance

		# How many master?
		while True:
			masters = self.ask("Quantos master nodes haverão no control plane (digite um número inteiro maior que 1): ")
			if masters is None:
				continue

			try:
				masters = int(masters)
			except:
				print(f"Valor inválido: {masters}")
				continue

			if masters < 1:
				print("Vey. Precisa, pelo menos de 1 master node no control plane.")
				continue

			if masters > 10:
				print("Esse script foi limitado para guardar até 10 replicas de Master node no control plane. Digite um valor menor que 10.")
				continue

			break

		# More than one, need a load balancer
		if masters > 1:

			loadbalancer = self.ask("Nome da instância que vai rodar o Load Balancer: ")
		
			# Try to get Load balance IP address
			loadbalancer_ip = self.ip_address(loadbalancer)
			if loadbalancer_ip and not self.ip_belongs_cidr(loadbalancer_ip, cidr_instance):
				print(f"O IP detectado não pertence a rede \"{cidr_instance}\"")
				loadbalancer_ip = None

			if loadbalancer_ip is None:
				while True:
					loadbalancer_ip = self.ask("IP da instância que vai rodar o Load Balance: ")
					if not self.parse_ip_address(loadbalancer_ip):
						continue
					
					if not self.ip_belongs_cidr(loadbalancer_ip, cidr_instance):
						print(f"O IP que você especificou não pertence a rede \"{cidr_instance}\"")
						continue
					
					break
			
			self.values.loadbalancer = InstanceMachine(
				hostname=loadbalancer,ip=loadbalancer_ip
			)
				

		# Nome das instâncias Master:
		self.values.master_nodes = []
		for i in range(masters):

			master_name = self.ask(f"Nome da instância que vai rodar o Master Node {i + 1}: ")
			master_ip 	= self.ip_address(master_name)
			if master_ip and not self.ip_belongs_cidr(master_ip, cidr_instance):
				print(f"O IP detectado não pertence a rede \"{cidr_instance}\"")
				master_ip = None

			if master_ip is None:
				while True:
					master_ip = self.ask(f"IP da instância que vai rodar o Master Node {i + 1}: ")
					if not self.parse_ip_address(master_ip):
						continue
					
					if not self.ip_belongs_cidr(master_ip, cidr_instance):
						print(f"O IP que você especificou não pertence a rede \"{cidr_instance}\"")
						continue
					
					break
	
			self.values.master_nodes.append(
				InstanceMachine(
					hostname=master_name, ip=master_ip
				)
			)

		

		# How many worker nodes?
		self.values.worker_nodes = []
		while True:
			workers = self.ask("Quantos worker nodes (digite um número inteiro maior que 1): ")
			if workers is None:
				continue

			try:
				workers = int(workers)
			except:
				print(f"Valor inválido: {workers}")
				continue

			if workers < 1:
				print("Vey. Precisa, pelo menos de 1 worker node no cluster.")
				continue

			if workers > 10:
				print("Esse script foi limitado para criar até 10 worker nodes no cluster. Digite um valor menor que 10.")
				continue

			break

		for i in range(workers):

			worker_name = self.ask(f"Nome da instância que vai rodar o Worker Node {i + 1}: ")
			worker_ip 	= self.ip_address(worker_name)
			if worker_ip and not self.ip_belongs_cidr(worker_ip, cidr_instance):
				print(f"O IP detectado não pertence a rede \"{cidr_instance}\"")
				worker_ip = None

			if worker_ip is None:
				while True:
					worker_ip = self.ask(f"IP da instância que vai rodar o Worker Node {i + 1}: ")
					if not self.parse_ip_address(worker_ip):
						continue
					
					if not self.ip_belongs_cidr(worker_ip, cidr_instance):
						print(f"O IP que você especificou não pertence a rede \"{cidr_instance}\"")
						continue
					
					break
	
			self.values.worker_nodes.append(
				InstanceMachine(
					hostname = worker_name, ip = worker_ip
				)
			)

		# Salva a config
		self.write()	

	
		

		
		
		





		

