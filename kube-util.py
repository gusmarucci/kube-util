#!/usr/bin/python3

# -*- coding: utf-8 -*-
#
#  kube-util.py
#
#  Copyright 2024
#  Autor......: Gustavo Marucci <gustavo@marucciviana.com.br>
#  Data.......: 07/11/2024
#  Descrição..: Kubernetes Utilities
#

# Force UTF-8 output
import	os
import 	sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Check Python version (requires 3.12 or later)
version = sys.version_info
if version.major < 3 or version.minor < 12:
	print("Requires Python version 3.12 or later")
	sys.exit(5)

# Global imports
from 	classes.argparser		import ArgParser
from	classes.config			import Config
from	classes.varglobal		import Global

if __name__ == "__main__":

	# Absolute path
	Global.base_path    = os.path.dirname(os.path.abspath(__file__))

	print(Global.base_path)
	
	# Install de configuration
	Config.install()

	# Parse the arguments
	ArgParser()
