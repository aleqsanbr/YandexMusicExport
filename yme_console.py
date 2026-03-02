import requests
import json
import re
import time
from datetime import datetime

def print_error(e):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "|", ">>>", e)

def send_welcome():
    print("=== Экспорт Яндекс Музыки === \n\n" +
          "Программа позволяет экспортировать любой плейлист Яндекс Музыки в текстовое " +
          "представление ИМЯ ИСПОЛНИТЕЛЯ - НАЗВАНИЕ ТРЕКА.\n\n" +
          "1. Скопируйте и вставьте ниже ссылку на плейлист вида:\n" +
          "   https://music.yandex.ru/users/USERNAME/playlists/PLAYLIST_ID\n" +
          "   Либо HTML-код плейлиста (кнопка «Поделиться» → «HTML код»).\n" +
          "   Инструкция: https://u-pov.ru/instructions/aleqs/1377\n\n" +
          "2. Если плейлист большой, может потребоваться некоторое время для обработки.\n" +
          "3. Если ссылка корректная, но возникает ошибка, то, вероятно, сработал 'бан' со " +
          "стороны Яндекса. В таком случае попробуйте еще раз через некоторое время или на " +
          "другом устройстве.\n" +
          "4. Предложения, критика и прочее принимаются тута: https://t.me/aleqsanbr")
    print("Также функционал доступен на сайте :) https://files.u-pov.ru/programs/YandexMusicExport")

def export_playlist(owner, kinds):
    uri = f"https://music.yandex.ru/handlers/playlist.jsx?owner={owner}&kinds={kinds}"
    response = requests.get(uri)
    response.raise_for_status()

    data = response.json()
    playlist_title = data['playlist']['title']
    tracks = data['playlist']['tracks']

    all_file = ""
    for track in tracks:
        artists_names = ", ".join(artist['name'] for artist in track['artists'])
        all_file += f"{artists_names} - {track['title']}\n"

    filename = f"{playlist_title}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(all_file)

    print(f"Плейлист сохранен в файл: {filename}")
    print("Поддержите работу сервиса: https://aleqsanbr.dev. Спасибо за использование! 💜")

def handle_message(uri_raw):
    try:
        uri_raw = uri_raw.strip()

        iframe_match = re.search(r'src="https://music\.yandex\.[^/]+/iframe/playlist/([^/]+)/([^"]+)"', uri_raw)
        new_format = re.match(r'https://music\.yandex\.[^/]+/playlists/', uri_raw)
        old_format = re.match(r'https://music\.yandex\.[^/]+/users/[^/]+/playlists/', uri_raw)

        if iframe_match:
            owner = iframe_match.group(1)
            kinds = iframe_match.group(2)
            export_playlist(owner, kinds)

        elif new_format:
            print("Ссылка нового формата! Получить HTML-код для экспорта:\n"
                  "1. Откройте ссылку в браузере\n"
                  "2. Нажмите «Поделиться» → «HTML код»\n"
                  "3. Скопируйте код и вставьте его сюда\n\n"
                  "Подробная инструкция: https://u-pov.ru/instructions/aleqs/1377")

        elif old_format:
            uri_parts = uri_raw.split('?')[0].split('/')
            owner = uri_parts[4]
            kinds = uri_parts[6]
            export_playlist(owner, kinds)

        else:
            print("Ошибка! Не удалось распознать ввод. Укажите ссылку старого формата, "
                  "ссылку нового формата или HTML-код плейлиста.\n"
                  "Инструкция: https://u-pov.ru/instructions/aleqs/1377")

    except (json.JSONDecodeError, requests.exceptions.RequestException) as e:
        print_error(e)
        print("Ошибка! Несуществующий плейлист или временный бан от Яндекса. Проверьте ссылку " +
              "и попробуйте еще раз через некоторое время или на другом устройстве.\n\n" +
              f"Дополнительная информация: {e}")
    except IndexError as e:
        print_error(e)
        print("Ошибка! Вероятно, некорректная ссылка. Проверьте, чтобы она была вида " +
              "https://music.yandex.ru/users/USERNAME/playlists/PLAYLIST_ID. Попробуйте еще раз.\n\n" +
              f"Дополнительная информация: {e}")
    except Exception as e:
        print_error(e)
        print("Ошибка! Проверьте правильность ссылки и попробуйте еще раз. " +
              "Также учтите, что из-за большого количества запросов может последовать временный " +
              "бан от Яндекса. В таком случае попробуйте с другого устройства или на сайте " +
              "https://files.u-pov.ru/programs/YandexMusicExport.\n\n" +
              f"Дополнительная информация: {e}")

if __name__ == "__main__":
    send_welcome()
    while True:
        try:
            uri_raw = input("\nВведите ссылку на плейлист или HTML-код: ")
            handle_message(uri_raw)
        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
        except Exception as e:
            print_error(e)
            time.sleep(15)
