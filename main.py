# Программа по резервному копированию фото из профиля VK в папку на Яндекс диске.

import requests
import tqdm

from pprint import pprint
from urllib.parse import urlencode

# Получение токена от имени приложения
# APP_ID = '51828672'
# OAUTH_BASE_URL = 'https://oauth.vk.com/authorize' # открытие диалога авторизации
# params = {
#     'client_id': APP_ID,
#     'redirect_uri': 'https://oauth.vk.com/blank.html',
#     'display': 'page',
#     'scope': 'status, photos',
#     'response_type': 'token'
# }
#
# oauth_url = f'{OAUTH_BASE_URL}?{urlencode(params)}'
# print(oauth_url)

token_vk = 'vk1.a.X04Ko5bWhJJBUhjH-k5G0TAELwVZiJ_50IDmpTRDihWrbjb3ZJqu9s7zc2TMeg1AA5RQo8lMV0Bf4EX5rSQiR-Lr9Ca2SFSitsjlCH6ao8XyOrBUoyViOnS1jnGh-MSBu6G6Xuo41tqrx66YHknZ38N7CnqJeP47ENEJqMmyrrE_Y4f1WjY0b0Ylfyn4AWMcX9MMLGy0ZoiN3LN__f5WRQ'
token_yadisk = ''

# https://api.vk.com/method/METHOD?PARAMS&access_token=TOKEN&v=V

class VKAPIClient:
    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131'
        }

    def get_photos(self):
        params = self.get_common_params()
        params.update({'owner_id': self.user_id, 'album_id': 'profile', 'extended': 1, 'photo_sizes': 1})
        r = requests.get(
            f'{self.API_BASE_URL}/photos.get', params=params)
        # С запросом что-то пошло не так
        if r.status_code != 200:
           raise Exception(r.text)
        return r.json()

class YaKlient:
    API_BASE_URL = 'https://cloud-api.yandex.net'

# Пример как нужно передавать токен через заголовок (http - header)
# Authorization: OAuth 0c4181a7c2cf4521964a72ff57a34a07
    def __init__(self, token):
        self.headers = {'Authorization': f'OAuth {token}'}

   # Методом POST:
    # https: // cloud - api.yandex.net / v1 / disk / resources / upload
    # ? url = < ссылка на скачиваемый файл >
    # & path = < путь к папке, в которуюнужноскачатьфайл >
    # & [fields = < свойства, которые нужно включить вответ >]
    # & [disable_redirects = < признак запрета редиректов >]

    def upload_file (self, url, path):
        params = {'url': url, 'path': path}
        r = requests.post(
            f'{self.API_BASE_URL}/v1/disk/resources/upload', params=params, headers=self.headers)
        # Ожидаем код 202 (принято), а если не он то выводим ошибку
        if r.status_code != 202:
            raise Exception(r.text)
        return r.json()

# Методом PUT:
# https://cloud-api.yandex.net/v1/disk/resources
#  ? path=<путь к создаваемой папке>
#  & [fields=<свойства, которые нужно включить в ответ>]

    def create_folder (self, path):
        params = {'path': path}
        r = requests.put(
            f'{self.API_BASE_URL}/v1/disk/resources', params=params, headers=self.headers)
        # Ожидаем код 201 (папка создана), либо 409 (уже существует)
        if r.status_code not in [201, 409]:
            raise Exception(r.status_code, r.text)
        return r.json()

if __name__=='__main__':
    # Перед запуском удалить папку Progect вручную из Яндекс Диска
    # Инициализируем Яндекс Клиент и создаем папку для проекта
    ya_client = YaKlient(token_yadisk)
    ya_client.create_folder('disk:/Project')

    vk_client = VKAPIClient(token_vk, '15594498')
    photos_info = vk_client.get_photos()
    photos_list = photos_info['response']['items']
    for foto_info in tqdm.tqdm(photos_list):
        likes = foto_info['likes']['count']
        date = foto_info['date']
        sizes = foto_info['sizes']
        max_foto = max(sizes, key=lambda s: s['type'])
        ya_client.upload_file(max_foto['url'], f'disk:/Project/{likes}.jpg')
