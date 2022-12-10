import asyncio
from twocaptcha import TwoCaptcha

from PIL import Image
from os import listdir
from os.path import join

from conf import API_KEY

class BinderEditor:

	def __init__(self):
		self.standart_raw_path = "images_raw/"
		self.standart_path = "images/"
		
		self.standart_raw_cover_path = "special_raw/cover/"
		self.standart_cover_path = "special/cover/"
		
		self.standart_raw_avatar_path = "special_raw/avatar"
		self.standart_avatar_path = "special/avatar/"

	async def get_dir_images(self):
		return listdir(self.standart_raw_path)
	
	async def get_dir_cover(self):
		return listdir(self.standart_raw_cover_path)
	
	async def get_dir_avatar(self):
		return listdir(self.standart_raw_avatar_path)
	
	async def save_image(self, img, old_name, path):
		img.save(join(path, f"resize_{old_name}"))
	
	async def edit_img(self):
		images_list = await self.get_dir_images()
		images_opened_list = [
			Image.open(join(
				self.standart_raw_path,
				img_name
			))
			for img_name in images_list
		]
		for img_index in range(0, len(images_list) - 1):
			thumb = images_opened_list[img_index].resize((1143, 753))
			await self.save_image(
				thumb,
				images_list[img_index],
				self.standart_path
			)
		
		
		covers_list = await self.get_dir_cover()
		covers_opened_list = [
			Image.open(join(
				self.standart_raw_cover_path,
				cvr_name
			))
			for cvr_name in covers_list
		]
		for cvr_index in range(0, len(covers_list) - 1):
			thumb = covers_opened_list[cvr_index].resize((1143, 753))
			await self.save_image(
				thumb,
				covers_list[cvr_index],
				self.standart_cover_path
			)
		
		
		avatars_list = await self.get_dir_avatar()
		avatars_opened_list = [
			Image.open(join(
				self.standart_raw_avatar_path,
				av_name
			))
			for av_name in avatars_list
		]
		for av_index in range(0, len(avatars_list) - 1):
			thumb = avatars_opened_list[av_index].resize((1143, 753))
			await self.save_image(
				thumb,
				avatars_list[av_index],
				self.standart_avatar_path
			)

	async def captcha(self):
		solver = TwoCaptcha(API_KEY)
		id = solver.send(file='captcha.jpg')
		await asyncio.sleep(20)
		code = solver.get_result(id)
		return code