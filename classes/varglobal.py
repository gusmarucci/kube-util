# -*- coding: utf-8 -*-
#
#  varglobal.py
#
#  Copyright 2024
#  Autor......: Gustavo Marucci <gustavo@marucciviana.com.br>
#  Data.......: 07/11/2024
#  Descrição..: Variáveis globais e instâncias singleton
#


class Global:
	base_path: str	= None							# Absolute path of the script
	commands: dict	= None							# ArgumentParser objects
	config			= None							# Configuration Object