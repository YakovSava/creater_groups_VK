import asyncio

from asyncio import run, create_task, gather
from aiohttp import ClientOSError
from math import fsum

from plugins.connector import Connector
from plugins.binder import Binder

binder = Binder('parameters.json')

async def create_group_in_account(account_token:str = '', counter_group:int = 0, names:list = []):
	proxy = await binder.get_proxy()
	counter = 0
	if account_token != 0 and not isinstance(account_token, list):
		connector = Connector(token = account_token)
		ids = []
		counter_groups = 0
		try:
			while counter_groups < 3:
				try:
					id = await connector.group_create(names[counter_group + counter + counter_groups][:-1], proxy)
					if id[0] != 0 and id[0] != 14:
						print(f'Группа {names[counter_group + counter + counter_groups][:-1]} создана')
						ids.append(id[0][0])
						counter_groups += 1
					elif id[0] == 14:
						print('Обработка капчи...')
						id2 = await connector.group_create(names[counter_group + counter + counter_groups][:-1], proxy, **id[1])
						if id2[0] != 0 and id2[0] != 14:
							print(f'Группа {names[counter_group + counter + counter_groups][:-1]} создана')
							ids.append(id2[0][0])
							counter_groups += 1
						elif id2[0] == 14:
							print('Обработка не удалась, пропуск...')
						elif id2[0] == 0:
							print(f'Группа {names[counter_group + counter + counter_groups][:-1]} не создана')
					elif id[0] == 0:
						print(f'Группа {names[counter_group + counter + counter_groups][:-1]} не создана')
				except IndexError:
					break
			await connector.edit_group(ids, proxy)
			await connector.edit_albums(ids, proxy)
			await connector.upload_avatar(ids, proxy)
			await connector.upload_cover(ids, proxy)
			await connector.upload_in_album(ids, proxy)
			
			counter += counter_groups
			await binder.save_ids(ids = ids)
		except ClientOSError:
			pass
		else:
			print(f'Аккаунт - login: {account[0]}, password: {account[1]} - заблочен')
	return counter

async def main():
	await binder.resize_img()
	accounts_datas = await binder.get_account(counter)
	names = await binder.get_list()
	await binder.create_ids_file()
	tasks = []
	main_counter = 0
	for account in accounts_datas:
		proxy = await binder.get_proxy()
		if account != 0:
			login, password = account[0], account[1][:-1]
			token = await binder.get_token(
				login = login,
				password = password, 
				proxy = proxy
			)
			tasks.append(create_task(create_group_in_account(
				account_token = token,
				counter_group = main_counter,
				names = names[main_counter:]
			)))
			main_counter += 3
	responses = await gather(*tasks)

	print(f'Создано {fsum(responses)} групп')

if __name__ == '__main__':
	print('Запуск...')
	asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
