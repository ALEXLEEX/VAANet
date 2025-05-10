from core.utils import AverageMeter, process_data_item, run_model, calculate_accuracy

import os
import time
import torch

import matplotlib.pyplot as plt 

def val_epoch(epoch, data_loader, model, criterion, opt, writer, optimizer):
    print("# ---------------------------------------------------------------------- #")
    print('Validation at epoch {}'.format(epoch))
    model.eval()
    # print("end of model.eval()")
    preds_all, targets_all = [], [] 

    batch_time = AverageMeter()
    data_time = AverageMeter()
    losses = AverageMeter()
    accuracies = AverageMeter()
    # print("end of AverageMeter()")

    end_time = time.time()

    for i, data_item in enumerate(data_loader):
        visual, target, audio, visualization_item, batch_size = process_data_item(opt, data_item)
        data_time.update(time.time() - end_time)
        with torch.no_grad():
            output, loss = run_model(opt, [visual, target, audio], model, criterion, i)

        preds_all.append(output.detach().cpu())
        targets_all.append(target.cpu())

        acc = calculate_accuracy(output, target, 'pcc')

        losses.update(loss.item(), batch_size)
        accuracies.update(acc, batch_size)
        batch_time.update(time.time() - end_time)
        end_time = time.time()

        print('Validation: [', i, '/', len(data_loader), ']')

    writer.add_scalar('val/loss', losses.avg, epoch)
    writer.add_scalar('val/acc', accuracies.avg, epoch)
    print("Val loss: {:.4f}".format(losses.avg))
    print("Val PCC: {:.4f}".format(accuracies.avg))

    # ---------------- 预测分布 & 散点图 ---------------- #
    preds_all   = torch.cat(preds_all, dim=0)   # [N,2]
    targets_all = torch.cat(targets_all, dim=0) # [N,2]

    # 1) 直方图：Valence / Arousal 各一条
    writer.add_histogram('val/predV', preds_all[:, 0], epoch)
    writer.add_histogram('val/gtV',   targets_all[:, 0], epoch)
    writer.add_histogram('val/predA', preds_all[:, 1], epoch)
    writer.add_histogram('val/gtA',   targets_all[:, 1], epoch)

    # 2) GT(Ground Truth)‑Pred 散点图，直观看线性拟合
    fig, ax = plt.subplots(figsize=(3,3))
    ax.scatter(targets_all[:,0], preds_all[:,0], s=6, alpha=0.4)  # Valence
    ax.plot([-1,1], [-1,1], c='r', lw=1)                          # y=x 参考线
    ax.set_xlabel('GT V'); ax.set_ylabel('Pred V'); ax.set_title(f'E{epoch}')
    writer.add_figure('val/scatter_V', fig, epoch)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(3,3))
    ax.scatter(targets_all[:,1], preds_all[:,1], s=6, alpha=0.4)  # Arousal
    ax.plot([-1,1], [-1,1], c='r', lw=1)
    ax.set_xlabel('GT A'); ax.set_ylabel('Pred A'); ax.set_title(f'E{epoch}')
    writer.add_figure('val/scatter_A', fig, epoch)
    plt.close(fig)

    save_file_path = os.path.join(opt.ckpt_path, 'save_{}.pth'.format(epoch))
    states = {
        'epoch': epoch + 1,
        'state_dict': model.state_dict(),
        'optimizer': optimizer.state_dict(),
    }
    torch.save(states, save_file_path)
