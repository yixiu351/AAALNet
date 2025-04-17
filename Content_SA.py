import torch.nn as nn
import torch
from whiten_transform import Whiten
from function import mean_variance_norm

class Content_SA(nn.Module):
    def __init__(self, in_dim):
        super(Content_SA, self).__init__()
        self.f = nn.Conv2d(in_dim, in_dim, (1, 1))
        self.g = nn.Conv2d(in_dim, in_dim, (1, 1))
        self.h = nn.Conv2d(in_dim, in_dim, (1, 1))
        self.softmax = nn.Softmax(dim=-1)
        self.out_conv = nn.Conv2d(in_dim, in_dim, (1, 1))
        self.whiten=Whiten()
    def forward(self, content_feat):
        content_whiten=self.whiten(content_feat)
        B, C, H, W = content_feat.size()
        F_Fc_norm = self.f(mean_variance_norm(content_whiten)).view(B, -1, H * W).permute(0, 2, 1)

        B, C, H, W = content_feat.size()
        G_Fs_norm = self.g(mean_variance_norm(content_whiten)).view(B, -1, H * W)

        energy = torch.bmm(F_Fc_norm, G_Fs_norm)
        attention = self.softmax(energy)

        H_Fs = self.h(content_feat).view(B, -1, H * W)
        out = torch.bmm(H_Fs, attention.permute(0, 2, 1))
        B, C, H, W = content_feat.size()
        out = out.view(B, C, H, W)
        out = self.out_conv(out)
        out += content_feat
        return out
#
# input=torch.randn(1,512,16,16)
# content_sa=Content_SA(in_dim=512)
# print(content_sa(input).shape)