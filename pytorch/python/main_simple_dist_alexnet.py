import argparse
import os

import socket

import torch
import torch.nn as nn
import torch.nn.parallel
import torch.optim
import torch.utils.data as data
import torch.utils.data.distributed
import torchvision.datasets as datasets
import torchvision.models as models
import torchvision.transforms as transforms
import datetime

parser = argparse.ArgumentParser(description='PyTorch ImageNet Training')
parser.add_argument('--epochs',  type=int, metavar='E', nargs='?', default=2)
parser.add_argument('--save_every',  type=int, metavar='c', nargs='?', default=1)
parser.add_argument("--local-rank", "--local_rank", type=int)
parser.add_argument('data', metavar='DIR', nargs='?', default='imagenet',
                    help='path to dataset (default: imagenet)')


def main():
    # global best_acc1

    args = parser.parse_args()

    print(f"Data path: {args.data}")
    print(f"Number of Epochs: {args.epochs}")
    print(f"Save Every: {args.save_every}")

    torch.distributed.init_process_group(backend='nccl', init_method='env://')

    device_id = int(os.environ["LOCAL_RANK"])

    torch.cuda.set_device(device_id)

    model = models.alexnet() # NOTE: model definition

    #model = torch.nn.parallel.DistributedDataParallel(model).cuda()
    model = model.cuda(device_id)
    model = torch.nn.parallel.DistributedDataParallel(model,device_ids=[device_id])

    # define loss function (criterion), optimizer, and learning rate scheduler
    criterion = nn.CrossEntropyLoss().cuda(device_id)

    optimizer = torch.optim.SGD(model.parameters(), 0.1,
                                momentum=0.9,
                                weight_decay=1e-4)
    
    traindir = os.path.join(args.data, 'train')
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])

    train_dataset = datasets.ImageFolder(
        traindir,
        transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            normalize,
        ]))

    train_sampler = data.distributed.DistributedSampler(train_dataset, shuffle=True)

    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=64, shuffle=(train_sampler is None),
        num_workers=4, pin_memory=True, sampler=train_sampler)

    # val_loader = torch.utils.data.DataLoader(
    #     val_dataset, batch_size=args.batch_size, shuffle=False,
    #     num_workers=args.workers, pin_memory=True, sampler=val_sampler)

    print(f"{datetime.datetime.now()}: Training begin")

    for epoch in range(0, args.epochs):

        train_sampler.set_epoch(epoch)

        print(f"{datetime.datetime.now()}: Training epoch {epoch}")
        # train for one epoch
        train(train_loader, model, criterion, optimizer, epoch, device_id, args)
        print(f"{datetime.datetime.now()}: Trained epoch {epoch}")

        # evaluate on validation set
        # acc1 = validate(val_loader, model, criterion, args)

        if epoch % args.save_every == 0:
            ckp = model.state_dict()
            PATH = "checkpoint.pt"
            print(f"{datetime.datetime.now()}: Epoch {epoch} | Saving checkpoint at {PATH}")
            torch.save(ckp, PATH)
            print(f"{datetime.datetime.now()}: Epoch {epoch} | Checkpoint saved at {PATH}")

        
        #scheduler.step()



def train(train_loader, model, criterion, optimizer, epoch, device_id, args):

    # switch to train mode
    model.train()

    for i, (images, target) in enumerate(train_loader):
        print(f"    {datetime.datetime.now()}: Start Training Iteration {i}")

        # move data to the same device as model
        print(f"        {datetime.datetime.now()}: Moving data to the same device as model")
        images = images.to(device_id, non_blocking=True)
        target = target.to(device_id, non_blocking=True)

        # compute output
        print(f"        {datetime.datetime.now()}: Computing output")
        output = model(images)
        print(f"        {datetime.datetime.now()}: Computing Loss")
        loss = criterion(output, target)

        # compute gradient and do SGD step
        optimizer.zero_grad()
        print(f"        {datetime.datetime.now()}: Compute gradient")
        loss.backward()
        print(f"        {datetime.datetime.now()}: SGD step")
        optimizer.step()

        print(f"    {datetime.datetime.now()}: End Training Iteration {i}")

if __name__ == '__main__':
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

    print("Your Computer Name is:" + hostname)
    print("Your Computer IP Address is:" + IPAddr)

    main()
