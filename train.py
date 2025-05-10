from core.utils import AverageMeter, process_data_item, run_model, calculate_accuracy

import time


def train_epoch(epoch, data_loader, model, criterion, optimizer, opt, class_names, writer):
    print("# ---------------------------------------------------------------------- #")
    print('Training at epoch {}'.format(epoch))
    model.train()
    # print("end of model.train()")

    batch_time = AverageMeter()
    data_time = AverageMeter()
    losses = AverageMeter()
    accuracies = AverageMeter()
    # print("end of AverageMeter()")

    end_time = time.time()

    for i, data_item in enumerate(data_loader):
        visual, target, audio, visualization_item, batch_size = process_data_item(opt, data_item)
        data_time.update(time.time() - end_time)
        # print("end of process_data_item()")
        
        output, loss = run_model(opt, [visual, target, audio], model, criterion, i, print_attention=False)
        # print("end of run_model()")

        # 获取这个batch的PCC也就是8个pred和real相关性多少
        acc = calculate_accuracy(output, target, 'pcc')

        # 求加入这个batch之后的整个epoch平均loss
        losses.update(loss.item(), batch_size)
        accuracies.update(acc, batch_size)

        # Backward and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        batch_time.update(time.time() - end_time)
        end_time = time.time()

        iter = (epoch - 1) * len(data_loader) + (i + 1)
        writer.add_scalar('train/batch/loss', losses.val, iter)
        writer.add_scalar('train/batch/acc', accuracies.val, iter)

        # 
        opt.debug = True
        # 
        if opt.debug:
            print('Epoch: [{0}][{1}/{2}]\t'
                  'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
                  'Data {data_time.val:.3f} ({data_time.avg:.3f})\t'
                  'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
                  'PCC {acc.val:.3f} ({acc.avg:.3f})'.format(
                epoch, i + 1, len(data_loader), batch_time=batch_time, data_time=data_time, loss=losses, acc=accuracies))
            print()

    # ---------------------------------------------------------------------- #
    print("Epoch Time: {:.2f}min".format(batch_time.avg * len(data_loader) / 60))
    print("Train loss: {:.4f}".format(losses.avg))
    # print("Train acc: {:.4f}".format(accuracies.avg))
    print("Train PCC: {:.4f}".format(accuracies.avg))
    
    writer.add_scalar('train/epoch/loss', losses.avg, epoch)
    writer.add_scalar('train/epoch/acc', accuracies.avg, epoch)
