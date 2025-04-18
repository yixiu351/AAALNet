# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
from function import calc_mean_std, mean_variance_norm
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
decoder = nn.Sequential(
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(512, 256, (3, 3)),
    nn.ReLU(),
    nn.Upsample(scale_factor=2, mode='nearest'),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(256, 256, (3, 3)),
    nn.ReLU(),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(256, 256, (3, 3)),
    nn.ReLU(),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(256, 256, (3, 3)),
    nn.ReLU(),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(256, 128, (3, 3)),
    nn.ReLU(),
    nn.Upsample(scale_factor=2, mode='nearest'),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(128, 128, (3, 3)),
    nn.ReLU(),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(128, 64, (3, 3)),
    nn.ReLU(),
    nn.Upsample(scale_factor=2, mode='nearest'),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(64, 64, (3, 3)),
    nn.ReLU(),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(64, 3, (3, 3)),
)

vgg = nn.Sequential(
    nn.Conv2d(3, 3, (1, 1)),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(3, 64, (3, 3)),
    nn.ReLU(),  # relu1-1
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(64, 64, (3, 3)),
    nn.ReLU(),  # relu1-2
    nn.MaxPool2d((2, 2), (2, 2), (0, 0), ceil_mode=True),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(64, 128, (3, 3)),
    nn.ReLU(),  # relu2-1
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(128, 128, (3, 3)),
    nn.ReLU(),  # relu2-2
    nn.MaxPool2d((2, 2), (2, 2), (0, 0), ceil_mode=True),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(128, 256, (3, 3)),
    nn.ReLU(),  # relu3-1
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(256, 256, (3, 3)),
    nn.ReLU(),  # relu3-2
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(256, 256, (3, 3)),
    nn.ReLU(),  # relu3-3
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(256, 256, (3, 3)),
    nn.ReLU(),  # relu3-4
    nn.MaxPool2d((2, 2), (2, 2), (0, 0), ceil_mode=True),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(256, 512, (3, 3)),
    nn.ReLU(),  # relu4-1
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(512, 512, (3, 3)),
    nn.ReLU(),  # relu4-2
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(512, 512, (3, 3)),
    nn.ReLU(),  # relu4-3
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(512, 512, (3, 3)),
    nn.ReLU(),  # relu4-4
    nn.MaxPool2d((2, 2), (2, 2), (0, 0), ceil_mode=True),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(512, 512, (3, 3)),
    nn.ReLU(),  # relu5-1, this is the last layer used
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(512, 512, (3, 3)),
    nn.ReLU(),  # relu5-2
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(512, 512, (3, 3)),
    nn.ReLU(),  # relu5-3
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(512, 512, (3, 3)),
    nn.ReLU()  # relu5-4
)

class Whiten(torch.nn.Module):
    def __init__(self,eps=2e-5,train_mode=False):
        super().__init__()
        self.eps=eps
        self.train_mode=train_mode

    def cholesky_dec(self, conv, invert=False):
        cholesky = torch.linalg.cholesky if torch.__version__ >= '1.8.0' else torch.cholesky
        try:
            L = cholesky(conv)
        except RuntimeError:
            # print("Warning: Cholesky Decomposition fails")

            # train
            if self.train_mode:
                raise ('Cholesky Decomposition fails. Gradient infinity.')

            # eval
            iden = torch.eye(conv.shape[-1]).to(conv.device)
            eps = self.eps
            while True:
                try:
                    conv = conv + iden * eps
                    L = cholesky(conv)
                    break
                except RuntimeError:
                    eps = eps + self.eps

        if invert:
            L = torch.inverse(L)

        return L.to(conv.dtype)

    def whitening(self,x):
        mean = torch.mean(x, -1)
        mean = mean.unsqueeze(-1).expand_as(x)
        x = x - mean
        conv = (x @ x.transpose(-1, -2)).div(x.shape[-1] - 1)
        inv_L = self.cholesky_dec(conv, invert=True)
        whiten_x = inv_L @ x
        return whiten_x
    def forward(self,input):

        B, N, cH, cW = input.shape
        input = input.reshape(B, N, -1)
        output=self.whitening(input)
        return output.reshape(B, N, cH, cW)

class RPAD(nn.Module):
    def __init__(self, in_channels=3):
        super(RPAD, self).__init__()
        def discriminator_block(in_filters, out_filters, normalize=True):
            layers = [nn.Conv2d(in_filters, out_filters, 4, stride=2, padding=1)]
            if normalize:
                layers.append(nn.InstanceNorm2d(out_filters))
            layers.append(nn.LeakyReLU(0.2, inplace=False))
            return layers

        class ResidualBlock(nn.Module):
            def __init__(self, in_channels):
                super(ResidualBlock, self).__init__()
                self.conv_block = nn.Sequential(
                    nn.Conv2d(in_channels, in_channels, 3, padding=1),
                    nn.InstanceNorm2d(in_channels),
                    nn.LeakyReLU(0.2, inplace=True),
                    nn.Conv2d(in_channels, in_channels, 3, padding=1),
                    nn.InstanceNorm2d(in_channels)
                )

            def forward(self, x):
                return x + self.conv_block(x)

        # Construct three discriminator models
        self.models = nn.ModuleList()
        self.score_models = nn.ModuleList()
        for i in range(3):
            self.models.append(
                nn.Sequential(
                    *discriminator_block(in_channels, 64, normalize=False),
                    ResidualBlock(64),
                    *discriminator_block(64, 128),
                    ResidualBlock(128),
                    *discriminator_block(128, 256),
                    ResidualBlock(256),
                    *discriminator_block(256, 512)
                )
            )
            self.score_models.append(
                nn.Sequential(
                    nn.Conv2d(512, 1, 3, padding=1)
                )
            )
        self.downsample = nn.Conv2d(in_channels, in_channels, 3, stride=2, padding=1, groups=in_channels)

    # Compute the MSE between model output and scalar gt
    def compute_loss(self, x, gt):
        _, outputs = self.forward(x)

        loss = sum([torch.mean((out - gt) ** 2) for out in outputs])
        return loss

    def forward(self, x):
        # print(x.shape)
        outputs = []
        feats = []
        for i in range(len(self.models)):
            feats.append(self.models[i](x))
            outputs.append(self.score_models[i](self.models[i](x)))
            x = self.downsample(x)

        class UpsampleToMatch(nn.Module):
            def __init__(self, in_channels, target_size):
                super(UpsampleToMatch, self).__init__()
                self.target_size = target_size

                self.upsample = nn.ConvTranspose2d(
                    in_channels,
                    in_channels,
                    kernel_size=4,
                    stride=2,
                    padding=1,
                    output_padding=0
                )

            def forward(self, x):
                while x.shape[2] < self.target_size[2] or x.shape[3] < self.target_size[3]:
                    x = self.upsample(x)
                return x

        def create_upsample_model(target_tensor):
            in_channels = target_tensor.size(1)
            target_size = target_tensor.size()
            return UpsampleToMatch(in_channels, target_size)
    

        feat = feats[0]
        upsample_model = create_upsample_model(feat).to(device)
        for i in range(1 ,len(feats)):
            feat += upsample_model(feats[i])
        return feat, outputs


class ASA(nn.Module):
    def __init__(self, in_planes):
        super(ASA, self).__init__()
        self.a = nn.Conv2d(in_planes, in_planes, (1, 1))
        self.b = nn.Conv2d(in_planes, in_planes, (1, 1))
        self.c = nn.Conv2d(in_planes, in_planes, (1, 1))
        self.d = nn.Conv2d(in_planes, in_planes, (1, 1))
        self.e = nn.Conv2d(in_planes, in_planes, (1, 1))
        self.o1 = nn.Conv2d(in_planes, in_planes, (1, 1))
        self.sm = nn.Softmax(dim=-1)
        self.out_conv1 = nn.Conv2d(in_planes, in_planes, (1, 1))
        self.out_conv2 = nn.Conv2d(in_planes, in_planes, (1, 1))
        self.content_sa = Content_SA(in_planes)

    def forward(self, content, style, aesthetic_feats):
        content = self.content_sa(content)
        if aesthetic_feats != None:
            A = self.a(aesthetic_feats)
        else:
            A = self.a(style)

        B = self.b(style)
        b, c, h, w = A.size()
        A = A.view(b, -1, w * h)  # C x HsWs
        b, c, h, w = B.size()
        B = B.view(b, -1, w * h).permute(0, 2, 1)  # HsWs x C
        AS = torch.bmm(A, B)  # C x C
        AS = self.sm(AS)  # aesthetic attention map

        C = self.c(style)
        b, c, h, w = C.size()
        C = C.view(b, -1, w * h)  # C x HsWs
        astyle = torch.bmm(AS, C)  # C x HsWs

        astyle = astyle.view(b, c, h, w)
        astyle = self.out_conv1(astyle)
        astyle += style

        O1 = self.o1(mean_variance_norm(astyle))
        O1 = O1.view(b, -1, w * h)  # C x HsWs

        D = self.d(mean_variance_norm(content))
        b, c, h, w = D.size()
        D = D.view(b, -1, w * h).permute(0, 2, 1)  # HcWc x C

        S = torch.bmm(D, O1)  # HcWc x HsWs
        S = self.sm(S)  # style attention map

        E = self.e(astyle)
        b, c, h, w = E.size()
        E = E.view(b, -1, w * h)  # C x HsWs
        O = torch.bmm(E, S.permute(0, 2, 1))  # C x HcWc

        b, c, h, w = content.size()
        O = O.view(b, c, h, w)
        O = self.out_conv2(O)
        O += content
        return O

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

class Transform(nn.Module):
    def __init__(self, in_planes):
        super(Transform, self).__init__()
        self.ASA_4_1 = ASA(in_planes=in_planes)
        self.ASA_5_1 = ASA(in_planes=in_planes)
        self.merge_conv_pad = nn.ReflectionPad2d((1, 1, 1, 1))
        self.merge_conv = nn.Conv2d(in_planes, in_planes, (3, 3))

    def forward(self, content4_1, style4_1, content5_1, style5_1, aesthetic_feats=None):
        self.upsample_content4_1 = nn.Upsample(size=(content4_1.size()[2], content4_1.size()[3]), mode='nearest')
        self.upsample_style4_1 = nn.Upsample(size=(style4_1.size()[2], style4_1.size()[3]), mode='nearest')
        self.upsample_style5_1 = nn.Upsample(size=(style5_1.size()[2], style5_1.size()[3]), mode='nearest')
        if aesthetic_feats != None:
            return self.merge_conv(self.merge_conv_pad(self.ASA_4_1(content4_1, style4_1, self.upsample_style4_1(
                aesthetic_feats)) + self.upsample_content4_1(
                self.ASA_5_1(content5_1, style5_1, self.upsample_style5_1(aesthetic_feats)))))
        else:
            return self.merge_conv(self.merge_conv_pad(
                self.ASA_4_1(content4_1, style4_1, aesthetic_feats) + self.upsample_content4_1(
                    self.ASA_5_1(content5_1, style5_1, aesthetic_feats))))


class Net(nn.Module):
    def __init__(self, encoder, decoder, discriminator):
        super(Net, self).__init__()
        enc_layers = list(encoder.children())
        self.enc_1 = nn.Sequential(*enc_layers[:4])  # input -> relu1_1
        self.enc_2 = nn.Sequential(*enc_layers[4:11])  # relu1_1 -> relu2_1
        self.enc_3 = nn.Sequential(*enc_layers[11:18])  # relu2_1 -> relu3_1
        self.enc_4 = nn.Sequential(*enc_layers[18:31])  # relu3_1 -> relu4_1
        self.enc_5 = nn.Sequential(*enc_layers[31:44])  # relu4_1 -> relu5_1

        self.transform = Transform(in_planes=512)
        self.decoder = decoder
        self.discriminator = discriminator
        self.cross_entropy_loss = nn.CrossEntropyLoss()
        self.sm=nn.Softmax(dim=-1)
        self.mse_loss = nn.MSELoss()
        # fix the encoder
        for name in ['enc_1', 'enc_2', 'enc_3', 'enc_4', 'enc_5']:
            for param in getattr(self, name).parameters():
                param.requires_grad = False

    # extract relu1_1, relu2_1, relu3_1, relu4_1, relu5_1 features from input image
    def encode_with_intermediate(self, input):
        results = [input]
        for i in range(5):
            func = getattr(self, 'enc_{:d}'.format(i + 1))
            results.append(func(results[-1]))
        return results[1:]

    # content loss
    def calc_content_loss(self, input, target, norm=False):
        if (norm == False):
            return self.mse_loss(input, target)
        else:
            return self.mse_loss(mean_variance_norm(input), mean_variance_norm(target))

    # style loss
    def calc_style_loss(self, input, target):
        input_mean, input_std = calc_mean_std(input)
        target_mean, target_std = calc_mean_std(target)
        return self.mse_loss(input_mean, target_mean) + \
               self.mse_loss(input_std, target_std)

    def attention_map(self, input1, input2):
        F = mean_variance_norm(input1)
        G = mean_variance_norm(input2)
        b, c, h, w = F.size()
        F = F.view(b, -1, w * h).permute(0, 2, 1)
        b, c, h, w = G.size()
        G = G.view(b, -1, w * h)
        S = torch.bmm(F, G)

        n = h * w
        T = torch.zeros((b, n, n - 1))

        for i in range(b):
            T[i] = S[i].flatten()[1:].view(n - 1, n + 1)[:, :-1].reshape(n, n - 1)
        T = self.sm(T / 100)

        return T

    def attention_loss(self, content, stylization):
        attention_map1 = self.attention_map(content, content)
        attention_map2 = self.attention_map(stylization, stylization)
        return self.mse_loss(attention_map1, attention_map2)

    def forward(self, content, style, aesthetic=False):
        style_feats = self.encode_with_intermediate(style)
        content_feats = self.encode_with_intermediate(content)
        if aesthetic:
            aesthetic_s_feats, _ = self.discriminator(style)
            stylized = self.transform(content_feats[3], style_feats[3], content_feats[4], style_feats[4],
                                      aesthetic_s_feats)
        else:
            stylized = self.transform(content_feats[3], style_feats[3], content_feats[4], style_feats[4])

        g_t = self.decoder(stylized)
        g_t_feats = self.encode_with_intermediate(g_t)

        # content loss
        loss_c = self.calc_content_loss(g_t_feats[3], content_feats[3], norm=True) + self.calc_content_loss(
            g_t_feats[4], content_feats[4], norm=True)
        # style loss
        loss_s = self.calc_style_loss(g_t_feats[0], style_feats[0])
        for i in range(1, 5):
            loss_s += self.calc_style_loss(g_t_feats[i], style_feats[i])

        # content attention loss
        loss_attention1 = self.attention_loss(content_feats[3], g_t_feats[3])
        loss_attention2 = self.attention_loss(content_feats[4], g_t_feats[4])
        loss_attention = loss_attention1 + loss_attention2

        # adversarial loss
        loss_gan_d = self.discriminator.compute_loss(style, 1) + self.discriminator.compute_loss(g_t.detach(), 0)
        loss_gan_g = self.discriminator.compute_loss(g_t, 1)

        if aesthetic:  # other losses in stage II
            # loss_AR1
            aesthetic_g_t_feats, _ = self.discriminator(g_t)
            Igt = self.decoder(
                self.transform(g_t_feats[3], g_t_feats[3], g_t_feats[4], g_t_feats[4], aesthetic_g_t_feats))
            l_identity1 = self.calc_content_loss(Igt, g_t)
            Fgt = self.encode_with_intermediate(Igt)
            l_identity2 = self.calc_content_loss(Fgt[0], g_t_feats[0])
            for i in range(1, 5):
                l_identity2 += self.calc_content_loss(Fgt[i], g_t_feats[i])

            # loss_AR2
            loss_aesthetic = self.calc_style_loss(aesthetic_g_t_feats, aesthetic_s_feats)

        else:  # other losses in stage I
            # identity loss
            Icc = self.decoder(self.transform(content_feats[3], content_feats[3], content_feats[4], content_feats[4]))
            Iss = self.decoder(self.transform(style_feats[3], style_feats[3], style_feats[4], style_feats[4]))

            l_identity1 = self.calc_content_loss(Icc, content) + self.calc_content_loss(Iss, style)
            Fcc = self.encode_with_intermediate(Icc)
            Fss = self.encode_with_intermediate(Iss)
            l_identity2 = self.calc_content_loss(Fcc[0], content_feats[0]) + self.calc_content_loss(Fss[0],style_feats[0])
            for i in range(1, 5):
                l_identity2 += self.calc_content_loss(Fcc[i], content_feats[i]) + self.calc_content_loss(Fss[i],style_feats[i])
            loss_aesthetic = 0

        l_identity = 50 * l_identity1 + l_identity2
        return g_t, loss_c,loss_attention, loss_s, loss_gan_d, loss_gan_g, l_identity, loss_aesthetic
