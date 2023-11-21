import cv2
import numpy as np
import json
import math
import base64


import torch as th
import torch

from torchvision import transforms
# import torchio as tio

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


    def predictCAMImage(self, img):
        image = torch.tensor(img, dtype=torch.float)
        image = torch.unsqueeze(torch.permute(image, (2,1,0)),0)

        
        new_i = self.tr[0](image)
        new_i = self.tr[1](new_i)

        print(img.shape, image.shape, new_i.shape)

        pred = self.net(new_i)
        
        pred_i = pred.argmax(1).detach().numpy()[0]

        # get the gradient of the output with respect to the parameters of the model
        pred[:,pred_i].backward()

        # pull the gradients out of the model
        gradients = self.net.get_activations_gradient()

        # pool the gradients across the channels
        pooled_gradients = torch.mean(gradients, dim=[0, 2, 3])

        # get the activations of the last convolutional layer
        activations = self.net.get_activations(new_i).detach()

        # weight the channels by corresponding gradients
        for i in range(64):
            activations[:, i, :, :] *= pooled_gradients[i]
            
        # average the channels of the activations
        heatmap = torch.mean(activations, dim=1).squeeze()

        # relu on top of the heatmap
        # expression (2) in https://arxiv.org/pdf/1610.02391.pdf
        heatmap = np.maximum(heatmap, 0)

        # normalize the heatmap
        heatmap /= torch.max(heatmap)


        heatmap2 = heatmap.detach().numpy()

        heatmap2 = cv2.resize(heatmap2, (img.shape[1], img.shape[0]))
        heatmap2 = np.uint8(255 * heatmap2)
        heatmap2 = cv2.applyColorMap(heatmap2, cv2.COLORMAP_JET)
        heatmap2 = cv2.cvtColor(heatmap2, cv2.COLOR_BGR2RGB)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        superimposed_img = heatmap2 * 0.4 + img * .6
        superimposed_img = superimposed_img.astype(int)

        cv2.imwrite('./map.jpg', superimposed_img)

        return pred_i, self.p_class[int(pred_i)], superimposed_img, heatmap2
