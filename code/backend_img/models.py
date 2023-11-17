from torch import nn
import torch
import torch as th

import torch.nn.functional as F


def conv(in_channels, out_channels, use_bias=False):
    return nn.Sequential(
        nn.BatchNorm2d(in_channels),
        nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=use_bias),
        nn.ReLU(inplace=True),
        nn.MaxPool2d(kernel_size=2,stride=2, padding=0, dilation=1),
    )

class Classifier(nn.Module):
    def __init__(self, dims=[400,400], out_channels=2, use_bias=False, freeze_bn=False):
        super().__init__()
        #TODO: vary architecture
        
        self.conv1 = conv(3, 16)
        self.conv2 = conv(16,32)
        self.conv3 = conv(32,64)

        self.fc1 = nn.Linear(64 * int(dims[0]/8) * int
        (dims[1]/8), 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, out_channels)

        self._initialize_weights()

        if freeze_bn:
            self.freeze_bn()
            
        # placeholder for the gradients
        self.gradients = None

    def forward(self, x):

        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        
        h = x.register_hook(self.activations_hook)

        x = torch.flatten(x, 1)

        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)

        return x


    def _initialize_weights(self):
        for module in self.modules():
            if isinstance(module, nn.Conv2d) or isinstance(module, nn.Linear):
                nn.init.kaiming_normal_(module.weight)
                if module.bias is not None:
                    module.bias.data.zero_()
            elif isinstance(module, nn.BatchNorm2d):
                module.weight.data.fill_(1)
                module.bias.data.zero_()

    def freeze_bn(self):
        for module in self.modules():
            if isinstance(module, nn.BatchNorm2d):
                module.eval()
                
    # hook for the gradients of the activations
    def activations_hook(self, grad):
        self.gradients = grad
        
    # method for the gradient extraction
    def get_activations_gradient(self):
        return self.gradients
    
    # method for the activation exctraction
    def get_activations(self, x):
        ret = self.conv1(x)
        ret = self.conv2(ret)
        ret = self.conv3(ret)
        return ret