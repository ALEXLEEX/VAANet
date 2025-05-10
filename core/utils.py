import os
import datetime
import shutil

from transforms.spatial import Preprocessing

import re
def _next_suffix(path):
    """若 path 已存在，则返回 path_1 / path_2 ... 中最小的可用路径"""
    if not os.path.exists(path):
        return path
    suffix = 1
    while True:
        new_path = f"{path}_{suffix}"
        if not os.path.exists(new_path):
            return new_path
        suffix += 1

def local2global_path(opt):
    if opt.root_path != '':
        opt.video_path = os.path.join(opt.root_path, opt.video_path)
        opt.audio_path = os.path.join(opt.root_path, opt.audio_path)
        opt.annotation_path = os.path.join(opt.root_path, opt.annotation_path)
        if opt.debug:
            opt.result_path = "debug"
        opt.result_path = os.path.join(opt.root_path, opt.result_path)
        if opt.expr_name == '':
            now = datetime.datetime.now()
            now = now.strftime('result_%Y%m%d_%H%M%S')
            opt.result_path = os.path.join(opt.result_path, now)
        # else:
        #     opt.result_path = os.path.join(opt.result_path, opt.expr_name)

        #     if os.path.exists(opt.result_path):
        #         shutil.rmtree(opt.result_path)
        #     os.mkdir(opt.result_path)
        else:
            opt.result_path = os.path.join(opt.result_path, opt.expr_name)

            # 若 --overwrite，直接删 否则自动找下一个不冲突的目录
            if os.path.exists(opt.result_path):
                if getattr(opt, "overwrite", False):
                    shutil.rmtree(opt.result_path)
                else:
                    opt.result_path = _next_suffix(opt.result_path)
            os.makedirs(opt.result_path, exist_ok=True)

        opt.log_path = os.path.join(opt.result_path, "tensorboard")
        opt.ckpt_path = os.path.join(opt.result_path, "checkpoints")
        if not os.path.exists(opt.log_path):
            os.makedirs(opt.log_path)
        # if not os.path.exists(opt.ckpt_path):
            # os.mkdir(opt.ckpt_path)
        if not os.path.exists(opt.ckpt_path):
            os.makedirs(opt.ckpt_path)
    else:
        raise Exception


def get_spatial_transform(opt, mode):
    if mode == "train":
        return Preprocessing(size=opt.sample_size, is_aug=True, center=False)
    elif mode == "val":
        return Preprocessing(size=opt.sample_size, is_aug=False, center=True)
    elif mode == "test":
        return Preprocessing(size=opt.sample_size, is_aug=False, center=False)
    else:
        raise Exception


class AverageMeter(object):
    """Computes and stores the average and current value"""

    def __init__(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


def process_data_item(opt, data_item):
    visual, target, audio, visualization_item = data_item
    target = target.cuda()

    visual = visual.cuda()
    audio = audio.cuda()
    assert visual.size(0) == audio.size(0)
    batch = visual.size(0)
    return visual, target, audio, visualization_item, batch


def run_model(opt, inputs, model, criterion, i=0, print_attention=True, period=30, return_attention=False):
    visual, target, audio = inputs
    outputs = model(visual, audio)
    y_pred, alpha, beta, gamma = outputs
    loss = criterion(y_pred, target)
    if i % period == 0 and print_attention:
        print('====alpha====')
        print(alpha[:, 0, :])
        print('====beta====')
        print(beta[:, 0, 0:512:32])
        print('====gamma====')
        print(gamma)
    if not return_attention:
        return y_pred, loss
    else:
        return y_pred, loss, [alpha, beta, gamma]

# TODO 3. 正确率函数换为 R2、MSE、PCC
# def calculate_accuracy(outputs, targets):
#     batch_size = targets.size(0)
#     values, indices = outputs.topk(k=1, dim=1, largest=True)
#     pred = indices
#     pred = pred.t()
#     correct = pred.eq(targets.view(1, -1))
#     n_correct_elements = correct.float()
#     n_correct_elements = n_correct_elements.sum()
#     n_correct_elements = n_correct_elements.item()
#     return n_correct_elements / batch_size


import torch

def calculate_accuracy(outputs, targets, metric='r2'):
    """
    计算 V 和 A 两个维度的正确率，并返回平均值。

    参数：
        outputs (torch.Tensor): 模型的输出，形状为 [batch_size, 2]。
        targets (torch.Tensor): 目标值，形状为 [batch_size, 2]。
        metric (str): 评价指标类型，可选 'r2', 'mse', 或 'pcc'。

    返回：
        float: V 和 A 两个维度的平均正确率。
    """
    assert outputs.shape == targets.shape, "Outputs and targets must have the same shape"
    assert outputs.shape[1] == 2, "The second dimension of outputs and targets must be 2 (representing V and A)"

    # 分别计算 V 和 A 的指标
    results = []
    for i in range(2):  # 遍历 V 和 A 两个维度
        output = outputs[:, i]
        target = targets[:, i]

        if metric == 'r2':
            # 计算 R²
            residual_sum_of_squares = torch.sum((target - output) ** 2)
            total_sum_of_squares = torch.sum((target - torch.mean(target)) ** 2)
            r2_score = 1 - residual_sum_of_squares / total_sum_of_squares
            results.append(r2_score.item())

        elif metric == 'mse':
            # 计算 MSE
            mse = torch.mean((output - target) ** 2)
            results.append(mse.item())

        elif metric == 'pcc':
            # 计算 Pearson Correlation Coefficient (PCC)
            mean_output = torch.mean(output)
            mean_target = torch.mean(target)

            covariance = torch.sum((output - mean_output) * (target - mean_target))
            std_output = torch.sqrt(torch.sum((output - mean_output) ** 2))
            std_target = torch.sqrt(torch.sum((target - mean_target) ** 2))

            std_output_val = std_output.item()
            std_target_val = std_target.item()

            if std_output_val < 1e-9 or std_target_val < 1e-9: # 检查标准差是否过小
                # 如果其中一个标准差为0（或非常小），则相关性未定义或为0
                # 如果协方差也为0，那么可以认为是0相关性
                # 如果协方差不为0，但标准差为0，这是一种退化情况，PCC未定义
                pcc_value = 0.0 # 或者 torch.nan，取决于您想如何处理这种情况
                if covariance.item() == 0.0 and (std_output_val < 1e-9 and std_target_val < 1e-9):
                    pcc_value = 1.0 # 如果两者都是常数且相同，可以认为是完全相关（尽管这有点特殊）
                                    # 或者更安全地设为0.0，因为没有“变化”可以关联
                elif covariance.item() == 0.0:
                     pcc_value = 0.0
                else:
                    # pcc_value = torch.nan # 如果协方差非0，但标准差为0，则确实是 NaN
                    print("pcc_value = Nan\n")
                    pcc_value = 0.0
            else:
                pcc = covariance / (std_output * std_target)
                pcc_value = pcc.item()

            # results.append(pcc.item())
            results.append(pcc_value)

        else:
            raise ValueError(f"Unknown metric: {metric}")

    # 返回 V 和 A 的平均值
    print("V PCC: " + str(results[0]) + " A PCC: " + str(results[1]))
    return sum(results) / len(results)