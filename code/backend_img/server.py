from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
import json
import base64
import numpy as np
import cv2
import os

from utils import ImgUtils


PORT = 3030

imut = ImgUtils()

# classify an image
# payload: {"image": binary_image}
# example {"image": b'\x89PNG\r\n....}
class ClassifyHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST')

    def post(self):

        print("[POST]  /classify")
        visitorEntry = self.get_body_argument('visitorEntry', default='false')

        imgReq = self.request.files['image'][0]['body']

        img = imut.decodeImg(imgReq)

        #classify an image
        pred_v, pred_c = imut.predictImage(img)

        print(pred_v, pred_c)

        self.write({"pred_v" : f'{pred_v}', "pred_c": f'{pred_c}'})


# classify an image
# payload: {"image": binary_image}
# example {"image": b'\x89PNG\r\n....}
class GradCAMHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST')

    def post(self):

        print("[POST]  /gradcam")
        visitorEntry = self.get_body_argument('visitorEntry', default='false')

        imgReq = self.request.files['image'][0]['body']

        img = imut.decodeImg(imgReq)

        #classify an image
        pred_v, pred_c, camimg, cam = imut.predictCAMImage(img)

        outi = cv2.imencode('.png', camimg)[1]
        outcami = cv2.imencode('.png', cam)[1]

        ret1 = "data:image/png;base64," + \
                base64.b64encode(outi).decode('utf-8')

        ret2 = "data:image/png;base64," + \
                base64.b64encode(outcami).decode('utf-8')

        self.write({"pred_v" : f'{pred_v}', "pred_c": f'{pred_c}', 'sup_img': ret1, 'cam_img': ret2})



def make_app():
    print("Plant, running on port", PORT)
    urls = [("/plant/classify", ClassifyHandler), ("/plant/gradcam", GradCAMHandler)]
    return Application(urls)


if __name__ == '__main__':
    app = make_app()
    app.listen(PORT)
    print("[APP] SERVER LISTENING..")
    IOLoop.instance().start()
