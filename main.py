from flask import Flask, render_template, request
from random import sample, choice
from geocoder import get_coordinates
from PIL import Image
import requests

app = Flask(__name__)


def check_answer(city, correct_city):
    return city.lower() == correct_city.lower()


correct_city = None

@app.route('/', methods=['GET', 'POST'])
def main():
    global correct_city
    CITIES = ['Москва', 'Санкт-Петербург', 'Новосибирск']
    if request.method == 'GET':
        # Выбираем случайный город
        city = choice(CITIES)
        correct_city = city

        coords = get_coordinates(city)
        # print(f"city-> {city} | coords-> {coords}")

        types_of_zoom = [12, 13, 14, 15, 16]
        types_of_maps = ['sat', 'map', 'sat,skl']
        types_of_rotate = [0, 90, 180, 270]

        types_of_zoom = sample(types_of_zoom, len(types_of_zoom))
        types_of_maps = sample(types_of_maps, len(types_of_maps))

        for i in range(1, 4):
            zoom = types_of_zoom[i - 1]
            map_type = types_of_maps[i - 1]

            # формируем URL запроса для получения изображения
            url = f'https://static-maps.yandex.ru/1.x/?ll={coords[0]},{coords[1]}&z={zoom}&l={map_type}&size=450,450'

            # отправляем запрос и получаем изображение в ответ
            response = requests.get(url)
            image = response.content

            # сохраняем изображение в файл
            filename = f'static/img/city_{i}.png'
            with open(filename, 'wb') as f:
                f.write(image)
                if map_type == 'sat':
                    image = Image.open(filename)

                    rotate = choice(types_of_rotate)
                    rotated_image = image.rotate(rotate)

                    rotated_image.save(filename)

        return render_template('slides.html', cities=CITIES)
    elif request.method == 'POST':
        now_city = request.form.get('city')
        # print(f"correct_city-> {correct_city.lower()} | now_city-> {now_city.lower()}")
        if correct_city.lower() == now_city.lower():
            message = ['Правильно!',
                       f'Правильный город: {correct_city}',
                       f'Вы указали: {now_city}'
                       ]
        else:
            message = ['Не правильно!',
                       f'Правильный город: {correct_city}',
                       f'А вы указали: {now_city}'
                       ]
        return render_template('result.html', message=message)
if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
