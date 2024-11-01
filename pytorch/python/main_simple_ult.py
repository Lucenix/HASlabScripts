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
parser.add_argument("--batch_size", type=int, default=64)
parser.add_argument("--dist", type=bool, default=False)
parser.add_argument("--model", default="resnet50")
parser.add_argument("--enable_log", type=bool, default=False)
parser.add_argument('data', metavar='DIR', nargs='?', default='imagenet',
                    help='path to dataset (default: imagenet)')

log = None

def log_print(string):
    print(string)

def log_no_print(string): 
    return

def main():
    global log

    args = parser.parse_args()

    log = log_print if args.enable_log else log_no_print
    # global best_acc1

    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

    log("Your Computer Name is:" + hostname)
    log("Your Computer IP Address is:" + IPAddr)


    log(f"Data path: {args.data}")
    log(f"Number of Epochs: {args.epochs}")
    log(f"Save Every: {args.save_every}")

    train_loader, train_sampler, model, criterion, optimizer, device_id, args = load_training_objects(args)

    log(f"{datetime.datetime.now()}: Training begin")

    for epoch in range(1, args.epochs + 1):

        log(f"{datetime.datetime.now()}: Training epoch {epoch}")

        if train_sampler != None:
            train_sampler.set_epoch(epoch)

        log(f"Training epoch {epoch}")
        # train for one epoch
        train(train_loader, model, criterion, optimizer, epoch, device_id, args)

        log(f"{datetime.datetime.now()}: Trained epoch {epoch}")

        # evaluate on validation set
        # acc1 = validate(val_loader, model, criterion, args)

        if args.save_every != 0 and epoch % args.save_every == 0:
            ckp = model.state_dict()
            PATH = "checkpoint.pt"
            log(f"{datetime.datetime.now()}: Epoch {epoch} | Saving checkpoint at {PATH}")
            torch.save(ckp, PATH)
            log(f"{datetime.datetime.now()}: Epoch {epoch} | Checkpoint saved at {PATH}")

        
        #scheduler.step()

def load_training_objects(args):

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

    model = models.__dict__[args.model]() # NOTE: model definition

    if args.dist:

        torch.distributed.init_process_group(backend='nccl', init_method='env://')

        device_id = int(os.environ["LOCAL_RANK"])

        torch.cuda.set_device(device_id)

        train_sampler = torch.utils.data.distributed.DistributedSampler(train_dataset, shuffle=True)

        model = model.cuda(device_id)
        model = torch.nn.parallel.DistributedDataParallel(model,device_ids=[device_id])

    else:

        device_id = torch.device("cuda")
        train_sampler = None
        model = model.cuda(device_id)

    # define loss function (criterion), optimizer, and learning rate scheduler
    criterion = nn.CrossEntropyLoss().cuda(device_id)

    optimizer = torch.optim.SGD(model.parameters(), 0.1,
                                momentum=0.9,
                                weight_decay=1e-4)

    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=args.batch_size, shuffle=(train_sampler is None),
        num_workers=4, pin_memory=True, sampler=train_sampler)

    return train_loader, train_sampler, model, criterion, optimizer, device_id, args


def train(train_loader, model, criterion, optimizer, epoch, device_id, args):
    global log

    # switch to train mode
    model.train()

    for i, (images, target) in enumerate(train_loader):

        log(f"    {datetime.datetime.now()}: Start Training Iteration {i}")

        # move data to the same device as model
        log(f"        {datetime.datetime.now()}: Moving data to the same device as model")
        images = images.cuda(device_id, non_blocking=True)
        target = target.cuda(device_id, non_blocking=True)

        # compute output
        log(f"        {datetime.datetime.now()}: Computing output")
        output = model(images)
        log(f"        {datetime.datetime.now()}: Computing Loss")
        loss = criterion(output, target)

        # compute gradient and do SGD step
        optimizer.zero_grad()
        log(f"        {datetime.datetime.now()}: Compute gradient")
        loss.backward()
        log(f"        {datetime.datetime.now()}: SGD step")
        optimizer.step()

        log(f"    {datetime.datetime.now()}: Ended Training Iteration {i}")

if __name__ == '__main__':
    main()
