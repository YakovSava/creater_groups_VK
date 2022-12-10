import asyncio

from aiofiles import open as _open
from os.path import join
from os import listdir, remove
from random import choice
from aiohttp import ClientSession
from twocaptcha import TwoCaptcha

from plugins.editor import BinderEditor

open_sync = open
edit = BinderEditor()

class Binder:

	def __init__(self, json_name:str = ''):
		self.json_name = json_name

	async def get_parameters(self):
		async with _open(join('plugins/parameters/', self.json_name), 'r', encoding = 'utf-8') as json_parameter:
			lines = await json_parameter.read()
		return eval(f'dict({lines})')

	async def _get_photo(self, name):
		parameters = await self.get_parameters()
		return open_sync(name, 'rb')
	
	async def get_avatar(self):
		parameters = await self.get_parameters()
		return await self._get_photo(join(parameters['photo_avatar'], choice(listdir(parameters['photo_avatar']))))

	async def get_cover(self):
		parameters = await self.get_parameters()
		return await self._get_photo(join(parameters['photo_cover'], choice(listdir(parameters['photo_cover']))))

	async def get_all_photos(self):
		parameters = await self.get_parameters()
		all_photo = listdir(parameters['photo_path'])
		photos = []
		for photo in all_photo:
			photo = await self._get_photo(join(parameters['photo_path'], photo))
			photos.append(photo)
		return photos

	async def get_proxy(self):
		parameters = await self.get_parameters()
		async with _open(parameters['proxys'], 'r', encoding = 'utf-8') as file:
			line = (choice(await file.readlines())).split(':')
			url = f'http://{line[2]}:{line[3]}@{line[0]}:{line[1]}'
		return url

	async def get_account(self, num:int = 0):
		accounts = []
		try:
			parameters = await self.get_parameters()

			async with _open(parameters['accounts'], 'r', encoding = 'utf-8') as file:
				lines = (await file.readlines())

			for line in lines:
				accounts.append(line.split(':'))

			return accounts
		except IndexError:
			return 0

	async def get_list(self):
		parameters = await self.get_parameters()
		async with _open(parameters['names'], 'r', encoding = 'utf-8') as file:
			lines = await file.readlines()
		return lines

	async def get_token(self, login = None, password = None, **kwargs):
		#print(login, password)
		async with ClientSession() as session:
			async with session.get(f'https://oauth.vk.com/token?grant_type=password&client_id=2274003&client_secret=hHbZxrka2uZ6jB1inYsH&username=+{login}&password={password}', **kwargs) as resp:
				response = await resp.json()
		try:
			return response['access_token']
		except KeyError:
			try:
				a = response['redirect_uri']
				print('Требуется валидация пользователя')
			except KeyError:
				try:
					a = response['error']
					print(f'Ошибка! {response["error"]}')
				except KeyError as e:
					return 0
				else:
					return 0
			else:
				return [a]

	async def create_ids_file(self):
		async with _open('groups.txt', 'w', encoding = 'utf-8') as file:
			file.write('')

	async def save_ids(self, ids:list = []):
		async with _open('groups.txt', 'a', encoding = 'utf-8') as file:
			for id in ids:
				await file.write(f'https://vk.com/club{id[0][0]}\n')

	async def resize_img(self):
		return await edit.edit_img()

	async def captcha_handle(self, sid = 000, vk_s = 0):
		async with ClientSession() as session:
			async with session.get(f'https://api.vk.com/captcha.php?sid={sid}?s=1') as resp:
				async with _open('captcha.jpg', 'wb') as photo:
					await photo.write(resp.content)
		solver = await edit.captcha(
			sid = sid,
			vk_s = vk_s
		)
		remove('captcha.jpg')
		return solver