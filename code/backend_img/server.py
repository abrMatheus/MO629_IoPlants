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

        '''
        if(visitorEntry == 'true'):
            img = ImgUtils.gammaCorr(img, gamma=0.7)

        cropped_face = ImgUtils.biggestFace(img)

        if(DEBUG):
            cv2.imshow("crop Image", img)
            cv2.waitKey(500)
            cv2.destroyAllWindows()

        hasFace = False
        ret = None
        if not(cropped_face is None):
            hasFace = True
            crop_rgb = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
            outImage = cv2.imencode('.png', crop_rgb)[1]
            ret = "data:image/png;base64," + \
                base64.b64encode(outImage).decode('utf-8')

        self.write({"image": ret, "hasFace": hasFace})
        '''
        self.write({"pred_v" : f'{pred_v}', "pred_c": f'{pred_c}'})





def make_app():
    print("Plant, running on port", PORT)
    urls = [("/plant/classify", ClassifyHandler)]
    return Application(urls)


if __name__ == '__main__':
    app = make_app()
    app.listen(PORT)
    print("[APP] SERVER LISTENING..")
    IOLoop.instance().start()
