import os
import io
import cv2
import uvicorn
from imageio import v3 as iio
from fastapi import FastAPI, Response, Request


app = FastAPI()


def get_img(name_img):
    """Просто читаем изображение"""
    return cv2.imread(f"./data/{name_img}.PNG", cv2.COLOR_BGR2RGB)


def get_start_point(list_img):
    """Находим позицию от которой будем печатать фотографии
    она меняется, так как если у нас одна цифра, то мы должны печатать ее ближе к краю
    """
    if len(list_img) == 3:
        return {'x': 280, 'y': 1231}
    if len(list_img) == 2:
        return {'x': 402, 'y': 1231}
    else:
        return {'x': 519, 'y': 1231}


def print_img_in_background(point, img, background):
    """Вставляем изображение на фон"""
    background[point['y']: point['y'] + img.shape[0], point['x']: point['x'] + img.shape[1]] = img
    return background


def add_space(start_point, img):
    """Делаем отступ между цифрами"""
    space = 32
    return {'x': start_point['x'] + len(img[0]) + space, 'y': start_point['y']}


def plot_number(str_numbers):
    background = get_img('background')
    list_img = [get_img(i) for i in str_numbers]
    start_point = get_start_point(list_img)
    for img in list_img:
        background = print_img_in_background(start_point, img, background)
        start_point = add_space(start_point, img)
    return background


@app.get('/please/{item_id}')
def number_to_img(item_id: str, request: Request):
    try:
        if len(item_id) > 3:
            return ValueError('Слишком длинное число')
        image = plot_number(item_id)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        with io.BytesIO() as buf:
            iio.imwrite(buf, image, format="PNG")
            im_bytes = buf.getvalue()
        return Response(content=im_bytes, media_type="image/png")
    except Exception as E:
        return str(E)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5005'))
    host = os.environ.get('HOST', '0.0.0.0')
    uvicorn.run("main:app", host=host, port=port, reload=True, workers=1)

#       https://dashboard.ngrok.com/get-started/setup
#       ngrok config add-authtoken 2DRH2lEHehPJvn1RFmkk0MMnVVM_6Y6L9utpiXcq2Cvwdo2ik
#       ngrok http 5005
#       add please/5
