import cv2
import numpy as np
import json
import math
import base64


import torch as th
import torch

from torchvision import transforms
import torchio as tio

from models import Classifier



class ImgUtils():
    def __init__(self):
        print("init imgutils")

        #load pytorch model
        self.net = Classifier(out_channels=6, dims=[256, 256], use_bias=False)
        checkpoint_file="simple_coffee.ckpt"
        checkpoint = th.load(checkpoint_file, map_location="cpu")
        self.net.load_state_dict(checkpoint)

        self.tr =  [transforms.Normalize(mean=[0,0,0], std=[1,1,1]), transforms.Resize(size=[256,256])]


        self.p_class={1:"cerco", 2: "ferrugem", 3:"mantegosa", 4:"phoma", 0:'0', 5:'5'}


    def encodeImg(self, input_image):
        ret, imencoded = cv2.imencode(".png", input_image)

        print("imencoded2: ",imencoded.tostring())

        if not(ret):
            print("encodeImg:: Problem with imencode")
            return False, []

        file = {'image': ('image.png', imencoded.tostring(),
                          'image/png', {'Expires': '0'})}

        return True, file

    def decodeImg(self, request):
        imageReq = request
        
        image = np.asarray(bytearray(imageReq), dtype=np.uint8)

        img = cv2.imdecode(image, cv2.IMREAD_COLOR)
        im_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return im_rgb


    def predictImage(self, img):
        # image = tio.ScalarImage("0001_0007.png")[tio.DATA]
        # image = torch.permute(image,(3,0,1,2)).float()
        image = torch.tensor(img, dtype=torch.float)
        image = torch.unsqueeze(torch.permute(image, (2,1,0)),0)


        new_i = self.tr[0](image)
        new_i = self.tr[1](new_i)

        pred = self.net(new_i)
        
        pred = pred.argmax(1).detach().numpy()[0]

        return pred, self.p_class[int(pred)]
