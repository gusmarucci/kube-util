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

from classes.varglobal			import Global

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