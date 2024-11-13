# -*- coding: utf-8 -*-
#
#  http.py
#
#  Copyright 2024
#  Author.......: Gustavo Marucci <gustavo@marucciviana.com.br>
#  Date.........: 03/07/2024
#  Description..: Classe para envio de requisições HTTP
#

import  aiohttp
import  asyncio
import  socket
from    enum                    import Enum
from    classes.varglobal		import Global

class Methods(Enum):
	GET     = "GET"
	POST    = "POST"
	PUT     = "PUT"
	PATCH   = "PATCH"
	DELETE  = "DELETE"


class HTTP(object):
	
	def __init__(self):
		'''
		Constructor
		
		'''
		pass


	def get(self, url, headers: dict = None):
		'''
		get
		Method that executes the asyncronous get
		
		'''          
		return asyncio.run(self._request(url = url, method = Methods.GET, headers=headers))


	def post(self, url, headers: dict = None, data: dict = None):
		'''
		post
		Method that executes the asyncronous post
		
		'''           
		return asyncio.run(self._request(url = url, method = Methods.POST, headers=headers, data=data)) 
	

	def patch(self, url, headers: dict = None, data: dict = None):
		'''
		patch
		Method that executes the asyncronous patch
		
		'''           
		return asyncio.run(self._request(url = url, method = Methods.PATCH, headers=headers, data=data)) 


	async def  _request(self, url: str, method: Methods, headers: dict = dict(), data: any = None) -> dict | list | None:
		'''
		_request
		Execute the HTTP request
		
		'''
		
		# Default header - Specify here in every request the header must be sent
		defaultHeaders = {
			'Content-Type': 'application/json'
		}

		url = f"{Global.config.base_url}{url}" 

		connector = aiohttp.TCPConnector(
			verify_ssl		= False, 
			use_dns_cache 	= False,
			family			= socket.AF_INET
		)
		
		headers = {**headers, **defaultHeaders} if headers else defaultHeaders

		async with aiohttp.ClientSession( 
			connector	= connector,
		) as session:
			try:
				match method:
					case Methods.GET:
						response = await session.get(url, headers=headers)

					case Methods.POST:
						response = await session.post(url, headers=headers, json=data)

					case Methods.PUT:
						response = await session.put(url, headers=headers, json=data)

					case Methods.PATCH:
						response = await session.patch(url, headers=headers, json=data)
					
					case Methods.DELETE:
						response = await session.delete(url, headers=headers, json=data)
					
					case _:
						raise Exception("Method not supported")
				
				response.raise_for_status()
				return await response.json()


			except aiohttp.ClientError as e:
				Global.log.error(f"Client HTTP Error: {str(e)}")
				return None
			
			except Exception as e:
				Global.log.error(f"Error HTTP Rest API: {str(e)}")
				return None
			

   


	

		

