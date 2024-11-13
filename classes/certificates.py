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

from classes.varglobal				import Global
from classes.config					import Config

class Certificates(object):


	def execute(self, args):
		'''
		execute
		
		'''
		args 	= vars(args)

		# New or update certificates
		new		= args['new'] or (args['new'] == False and args['update'] == False)
		new 	= False if args['update'] else new

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
		print("Certificate CA")

	
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