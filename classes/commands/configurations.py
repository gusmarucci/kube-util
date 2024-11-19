# -*- coding: utf-8 -*-
#
#  configurations.py
#
#  Copyright 2024
#  Autor......: Gustavo Marucci <gustavo@marucciviana.com.br>
#  Data.......: 14/11/2024
#  Descrição..: Comandos de manutenção de configuração do Kubernetes
#
#

import 	sys

from	classes.config				import Cluster
from 	classes.varglobal			import Global
from 	classes.kubernetes			import Kubernetes

class Configurations(object):
    
	def execute(self, args) -> None:
		'''
		execute
		Roda o programa solicitado por argumento

		'''
		args 	= vars(args)

		# New or update certificates		
		new		= args['new'] or (args['new'] == False and args['update'] == False)
		new 	= False if args['update'] else new

		# Read configuration
		Global.config.run()
				
		match args['type']:

			case "admin":
				self.admin(new)
			
			case "controller-manager":
				self.controller_manager(new)
				
			case "proxy":
				self.proxy(new)
			
			case "scheduler":
				self.scheduler(new)
				
			case "encrypt":
				self.encrypt(new)
				
			case _:
				self.admin(new)
				self.controller_manager(new)
				self.proxy(new)
				self.scheduler(new)
				self.encrypt(new)


	def admin(self, new: bool) -> None:
		'''
		admin
		Cria o arquivo de config para o admin
		
		'''
		print("Gerando config \"admin\"...")

		# CLuster config
		config: Cluster = Global.config.values

		if not config:
			print("Erro: As configs do Cluster já deveriam ter sido lidas... Finalizando...")
			sys.exit(1)

		# Load balancer?
		if not hasattr(config, "loadbalancer") or config.loadbalancer is None:
			server = f"https://{config.master_nodes[0].ip}:6443"
		else:
			server = f"https://{config.loadbalancer.ip}:6443"
			
		kube = Kubernetes()
		if kube.set_kubeconfig(
			server 		= server,
			cluster 	= config.name,
			user		= "admin",
			certificate = "admin",
			embedded 	= True
		):
			print("Config \"admin\" gerado com sucesso.")


	def controller_manager(self, new: bool) -> None:
		'''
		controller_manager
		Cria o arquivo de config para o Controller Manager
		
		'''
		print("Gerando config \"Controller Manager\"...")

		# CLuster config
		config: Cluster = Global.config.values

		if not config:
			print("Erro: As configs do Cluster já deveriam ter sido lidas... Finalizando...")
			sys.exit(1)
			
		kube = Kubernetes()
		if kube.set_kubeconfig(
			server 		= "https://127.0.0.1:6443",
			cluster 	= config.name,
			user		= "system:kube-controller-manager",
			certificate = "controller-manager"
		):
			print("Config \"Controller Manager\" gerado com sucesso.")


	def proxy(self, new: bool) -> None:
		'''
		proxy
		Cria o arquivo de config para o Kube proxy
		
		'''
		print("Gerando config \"Serviço Proxy\"...")

		# CLuster config
		config: Cluster = Global.config.values

		# Load balancer?
		if not hasattr(config, "loadbalancer") or config.loadbalancer is None:
			server = f"https://{config.master_nodes[0].ip}:6443"
		else:
			server = f"https://{config.loadbalancer.ip}:6443"

		if not config:
			print("Erro: As configs do Cluster já deveriam ter sido lidas... Finalizando...")
			sys.exit(1)
			
		kube = Kubernetes()
		if kube.set_kubeconfig(
			server 		= server,
			cluster 	= config.name,
			user		= "system:kube-proxy",
			certificate = "proxy"
		):
			print("Config \"Serviço Proxy\" gerado com sucesso.")

	
	def scheduler(self, new: bool) -> None:
		'''
		scheduler
		Cria o arquivo de config para o Kube proxy
		
		'''
		print("Gerando config \"Serviço Scheduler\"...")

		# CLuster config
		config: Cluster = Global.config.values

		if not config:
			print("Erro: As configs do Cluster já deveriam ter sido lidas... Finalizando...")
			sys.exit(1)
			
		kube = Kubernetes()
		if kube.set_kubeconfig(
			server 		= "https://127.0.0.1:6443",
			cluster 	= config.name,
			user		= "system:kube-scheduler",
			certificate = "proxy"
		):
			print("Config \"Serviço Scheduler\" gerado com sucesso.")


	def encrypt(self, new) -> None:
		'''
		encrypt
		Cria o arquivo de criptografia para o API Server

		'''
		print("Gerando config \"Criptografia\"...")
		kube = Kubernetes()
		if kube.set_encrypt():
			print("Config \"Criptografia\" gerado com sucesso.")
