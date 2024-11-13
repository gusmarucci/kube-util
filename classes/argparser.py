# -*- coding: utf-8 -*-
#
#  argparser.py
#
#  Copyright 2024
#  Author.......: Gustavo Marucci <gustavo@marucciviana.com.br>
#  Date.........:  11/11/2024
#  Description..: Classe para envio de requisições HTTP
#
import	gettext
from	classes.language		import Language
from	classes.varglobal		import Global
from 	classes.certificates	import Certificates
from	classes.installer		import Installer

# Argument Parser Library
gettext.gettext = Language().argparse
from	argparse 				import ArgumentParser


class ArgParser(object):
	
	def __init__(self) -> None:
		'''
		Constructor

		'''
		self.run()


	def run(self) -> None:
		'''
		run
		Run the argument parsing

		'''
		kube_util			= ArgumentParser(description="Kubernetes Utilites")
		command_parser		= kube_util.add_subparsers(dest="comando", required=True)
				
		Global.commands 		= dict(
			cert 	= dict(
				parser 		= command_parser.add_parser("cert", help="Comandos relacionados a manutenção dos certificados digitais"),
				sub_parser	= None
			),
			install = dict(
				parser 		= command_parser.add_parser("install", help="Comandos relacionados a instalação dos serviços"),
				sub_parser	= None
			),
		)

		# Certificate
		Global.commands["cert"]['parser'].set_defaults(func=Certificates().execute)

		Global.commands["cert"]['sub_parser'] = Global.commands['cert']['parser'].add_subparsers(dest='type')
		Global.commands["cert"]['sub_parser'].add_parser("all",						help="Cria ou atualiza todos os certificados")
		Global.commands["cert"]['sub_parser'].add_parser("api",						help="Cria ou atualiza o certificado do serviço de API")
		Global.commands["cert"]['sub_parser'].add_parser("ca",						help="Cria ou atualiza o certificado da Autoridade Certificadora")
		Global.commands["cert"]['sub_parser'].add_parser("admin",					help="Cria ou atualiza o certificado do usuário admin")
		Global.commands["cert"]['sub_parser'].add_parser("controller-manager",		help="Cria ou atualiza o certificado do serviço Controller Manager")
		Global.commands["cert"]['sub_parser'].add_parser("proxy",					help="Cria ou atualiza o certificado do serviço Proxy dos Worker nodes")
		Global.commands["cert"]['sub_parser'].add_parser("scheduler",				help="Cria ou atualiza o certificado do serviço de Scheduler")

		Global.commands["cert"]['parser'].add_argument("--new", action="store_true")
		Global.commands["cert"]['parser'].add_argument("--update", action="store_true")
		

		# Install Services
		Global.commands["install"]['parser'].set_defaults(func=Installer().execute)	

		args = kube_util.parse_args()
		args.func(args)
