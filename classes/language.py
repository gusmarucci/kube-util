# -*- coding: utf-8 -*-
#
#  kube-util.py
#
#  Copyright 2024
#  Autor......: Gustavo Marucci <gustavo@marucciviana.com.br>
#  Data.......: 07/11/2024
#  Descrição..: Kubernetes Utilities
#

import json

class Language(object):

	translation = None

	def __init__(self, locale: str = "pt_BR"):
		'''
		Constructor
		
		'''
		translation_file = f"locales/{locale}/argparse.json"
		try:
			with open(translation_file, "r") as t:
				self.translation = json.loads(t.read())

		except Exception as e:
			print(f"Fail to open \'argparse\' translation file located in path {translation_file}: {str(e)}")
			return 


	def argparse(self, text: str) -> str:
		'''
		argparse
		Translation of argparse

		'''
		try:
			return self.translation[text]
		except:
			return text

		
		
