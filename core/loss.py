import torch.nn as nn
import torch.nn.functional as f
from torch import Tensor
import torch
import numpy as np


class PCCEVE8(nn.Module):
    """
    0 Anger
    1 Anticipation
    2 Disgust
    3 Fear
    4 Joy
    5 Sadness
    6 Surprise
    7 Trust
    Positive: Anticipation, Joy, Surprise, Trust
    Negative: Anger, Disgust, Fear, Sadness
    """

    def __init__(self, lambda_0=0):
        super(PCCEVE8, self).__init__()
        self.POSITIVE = {1, 4, 6, 7}
        self.NEGATIVE = {0, 2, 3, 5}

        self.lambda_0 = lambda_0

        self.f0 = nn.CrossEntropyLoss(reduce=False)

    def forward(self, y_pred: Tensor, y: Tensor):
        batch_size = y_pred.size(0)
        weight = [1] * batch_size

        out = self.f0(y_pred, y)
        _, y_pred_label = f.softmax(y_pred, dim=1).topk(k=1, dim=1)
        y_pred_label = y_pred_label.squeeze(dim=1)
        y_numpy = y.cpu().numpy()
        y_pred_label_numpy = y_pred_label.cpu().numpy()
        for i, y_numpy_i, y_pred_label_numpy_i in zip(range(batch_size), y_numpy, y_pred_label_numpy):
            if (y_numpy_i in self.POSITIVE and y_pred_label_numpy_i in self.NEGATIVE) or (
                    y_numpy_i in self.NEGATIVE and y_pred_label_numpy_i in self.POSITIVE):
                weight[i] += self.lambda_0
        weight_tensor = torch.from_numpy(np.array(weight)).cuda()
        out = out.mul(weight_tensor)
        out = torch.mean(out)

        return out

# TODO 2. 把分类任务的损失换为回归任务的损失函数 
# CrossEntropyLoss -> MSELoss
def get_loss(opt):
    if opt.loss_func == 'ce':
        return nn.CrossEntropyLoss()
    elif opt.loss_func == 'mse':  # 添加回归任务的损失函数
        return nn.MSELoss()
    elif opt.loss_func == 'pcce_ve8':
        return PCCEVE8(lambda_0=opt.lambda_0)
    elif opt.loss_func == 'va_mse':
        def va_mse_loss(outputs, targets):
            assert outputs.shape == targets.shape, "Outputs and targets must have the same shape"
            assert outputs.shape[1] == 2, "The second dimension of outputs and targets must be 2 (representing V and A)"

            v_loss = nn.MSELoss()(outputs[:, 0], targets[:, 0]).cuda()
            a_loss = nn.MSELoss()(outputs[:, 1], targets[:, 1]).cuda()

            return (v_loss + a_loss) / 2

        return va_mse_loss
    else:
        raise Exception(f"Unknown loss function: {opt.loss_func}")
