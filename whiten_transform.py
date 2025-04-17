import torch

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

#
# input=torch.randn(1,3,16,16)
# whiten=Whiten()
# output=whiten(input)
# print(output.shape)

