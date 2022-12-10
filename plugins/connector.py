import asyncio

from aiohttp import ClientSession, ClientTimeout, ClientProxyConnectionError
from fake_useragent import UserAgent
from asyncio import sleep
from random import randint, choice 
from PIL import Image
from plugins.binder import Binder

binder = Binder('parameters.json')

class Connector:
	
	def __init__(self, token = None):
		self.timeout = ClientTimeout(5000)
		self.agent = UserAgent()
		self.limit = 3
		self.begin_url = 'https://api.vk.com/method/'
		self.end_url = f'access_token={token}&v=5.131'

	async def _process_raw_data(self, **data):
		processed_data = ''
		data_list = list(data.items())
		for item in data_list:
			processed_data += f'{item[0]}={item[1]}&'
		return processed_data

	async def _get_connect(self, url, proxy):
		async with ClientSession() as session:
			async with session.get(
					url,
					headers = {"user-agent": self.agent.random},
					proxy = proxy,
					timeout = self.timeout
				) as resp:
				#print(resp.status, url)
				if resp.status == 200:
					response = await resp.json()
					return response
		return 0

	async def _post_connect(self, url, data, proxy):
		async with ClientSession() as session:
			async with session.post(
					url,
					data = data,
					headers = {"user-agent": self.agent.random},
					proxy = proxy,
					timeout = self.timeout
			) as resp:
				response = await resp.read()
		return eval(f'dict({response.decode()})')

	async def _request(self, proxy = None, method = None, **kwargs):
		arguments = await self._process_raw_data(**kwargs)
		return await self._get_connect(f'{self.begin_url}{method}?{arguments}{self.end_url}', proxy)

	async def _get_server_upload_avatar(self, tid, proxy):
		resp = await self._request(
			proxy = proxy,
			method = 'photos.getOwnerPhotoUploadServer',
			owner_id = -tid
		)
		#print(resp)
		return eval(f'dict({resp})')

	async def _get_server_upload_cover(self, id, proxy, size):
		resp = await self._request(
			proxy = proxy,
			method = 'photos.getOwnerCoverPhotoUploadServer',
			group_id = id,
			crop_x =  0,
			crop_y = 0,
			crop_x2 = size[0],
			crop_y2  = size[1]
		)
		try:
			data = eval(f'dict({resp})')
			data['error'] = data['error']
		except KeyError:
			return 0
		else:
			return data

	async def _get_ids(self, responses:list):
		ids = []
		for response in responses:
			#print(response)
			try:
				ids.append(response['response']['id'])
			except KeyError:
				print(response['error']['error_code'], ' - ', response['error']['error_msg'])
				if response['error']['error_code'] == 14:
					captcha_kwargs = await binder.captcha_handle(sid = response['error']['captcha_sid'], vk_s = 1)
					return (14, captcha_kwargs)
				return [0]
		return ids

	async def group_create(self, name, proxy, **kwargs):
		await sleep(randint(120, 240))
		responses = []
		response = await self._request(
			proxy = proxy,
			method = 'groups.create',
			title = name,
			type = 'group',
			**kwargs
		)
		responses.append(response)
		ids = await self._get_ids(responses)
		try:
			err = ids[0]
		except IndexError:
			return ids
		return [ids]

	async def edit_group(self, ids, proxy):
		for id in ids:
			if not isinstance(id, list):
				resp = await self._request(
					proxy = proxy,
					method = 'groups.edit',
					group_id = id,
					wall = 3,
					topics = 0,
					photos = 2,
					video = 0,
					audio = 0,
					docs = 0,
					wiki = 0,
					main_section = 1,
					contacts = 0,
					places = 0,
					events = 0
				)
				#print(resp)
				await sleep(randint(5, 10))

	async def edit_albums(self, ids, proxy):
		album_ids = []
		#print(ids)
		for id in ids:
			if not isinstance(id, list):
				response = await self._request(
					proxy = proxy,
					method = 'photos.getAlbums',
					owner_id = -id
				)
				album_ids.append(response['response']['items'][0]['id'])
			await sleep(randint(5, 10))

		if len(album_ids) > 0:
			for index in range(len(album_ids) - 1):
				await self._request(
					proxy = proxy,
					method = 'photos.editAlbum',
					title = '1',
					upload_by_admins_only = 1,
					comments_disabled = 1,
					album_id = album_ids[index],
					owner_id = -ids[index]
				)

	async def upload_avatar(self, ids, proxy):
		post_ids = []
		for id in ids:
			if not isinstance(id, list):
				upload_url = (await self._get_server_upload_avatar(id, proxy))['response']['upload_url']
				photo = await binder.get_avatar()
				data = await self._post_connect(upload_url, {'photo': photo}, proxy)
				if data != 0:
					info = (await self._request(
						proxy = proxy,
						method = 'photos.saveOwnerPhoto',
						server = data['server'],
						hash = data['hash'],
						photo = data['photo']
					))['response']['post_id']
					await self._request(
						proxy = proxy,
						method = 'wall.delete',
						owner_id = -id,
						post_id = info
					)
					await sleep(randint(5, 10))

	async def upload_cover(self, ids, proxy):
		for id in ids:
			if not isinstance(id, list):
				photo = await binder.get_cover()
				image_size = Image.open(photo).size
				raw_response = await self._get_server_upload_cover(id, proxy, image_size)
				try:
					upload_url = raw_response['response']['upload_url']
				except KeyError:
					print(f'Обложка для {id} не загружена!')
				data = await self._post_connect(
					upload_url,
					{'photo': photo},
					proxy
				)
				await self._request(
					proxy = proxy,
					method = 'photos.saveOwnerCoverPhoto',
					hash = data['hash'],
					photo = data['photo']
				)

	async def upload_in_album(self, ids, proxy):
		for id in ids:
			if not isinstance(id, list):
				album_id = (await self._request(
					proxy = proxy,
					method = 'photos.getAlbums',
					owner_id = -id
				))['response']['items'][0]['id']

				if album_id != 0:
					upload_url = (await self._request(
						proxy = proxy,
						method = 'photos.getUploadServer',
						album_id = album_id,
						group_id = id
					))['response']['upload_url']

					photos = await binder.get_all_photos()
					for photo in photos:
						try:
							data = (await self._post_connect(
							upload_url,
							{'photo': photo},
							proxy
						))
							
							await self._request(
								proxy = proxy,
								method = 'photos.save',
								album_id = album_id,
								group_id = id,
								server = data['server'],
								photos_list = data['photos_list'],
								hash = data['hash']
							)
						except ClientProxyConnectionError:
							continue