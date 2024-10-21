import argparse
import os

import torch
import torch.nn as nn
import torch.nn.parallel
import torch.optim
import torch.utils.data
import torch.utils.data.distributed
import torchvision.datasets as datasets
import torchvision.models as models
import torchvision.transforms as transforms


parser = argparse.ArgumentParser(description='PyTorch ImageNet Training')
parser.add_argument('--epochs',  type=int, metavar='E', nargs='?', default=2)
parser.add_argument('--save_every',  type=int, metavar='c', nargs='?', default=1)
parser.add_argument('--batch_size',  type=int, metavar='b', nargs='?', default=64)
parser.add_argument('data', metavar='DIR', nargs='?', default='imagenet',
                    help='path to dataset (default: imagenet)')


def main():
    # global best_acc1

    args = parser.parse_args()

    print(f"Number of Epochs: {args.epochs}")
    print(f"Save Every: {args.save_every}")
    print(f"Bach Size: {args.batch_size}")
    print(f"Data path: {args.data}")

    model = models.resnet50() # NOTE: model definition

    model = torch.nn.DataParallel(model).cuda()

    device = torch.device("cuda")
    # define loss function (criterion), optimizer, and learning rate scheduler
    criterion = nn.CrossEntropyLoss().to(device)

    optimizer = torch.optim.SGD(model.parameters(), 0.1,
                                momentum=0.9,
                                weight_decay=1e-4)
    
    """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""
    #scheduler = StepLR(optimizer, step_size=30, gamma=0.1)
    

    traindir = os.path.join(args.data, 'train')
    # valdir = os.path.join(args.data, 'val')
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

    # val_dataset = datasets.ImageFolder(
    #     valdir,
    #     transforms.Compose([
    #         transforms.Resize(256),
    #         transforms.CenterCrop(224),
    #         transforms.ToTensor(),
    #         normalize,
    #     ]))

    train_sampler = None
    # val_sampler = None

    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=args.batch_size, shuffle=(train_sampler is None),
        num_workers=4, pin_memory=True, sampler=train_sampler)

    # val_loader = torch.utils.data.DataLoader(
    #     val_dataset, batch_size=args.batch_size, shuffle=False,
    #     num_workers=args.workers, pin_memory=True, sampler=val_sampler)


    for epoch in range(0, args.epochs):

        print(f"Training epoch {epoch}")
        # train for one epoch
        train(train_loader, model, criterion, optimizer, epoch, device, args)

        # evaluate on validation set
        # acc1 = validate(val_loader, model, criterion, args)

        if epoch % args.save_every == 0:
            ckp = model.state_dict()
            PATH = "checkpoint.pt"
            torch.save(ckp, PATH)
            print(f"Epoch {epoch} | Training checkpoint saved at {PATH}")

        
        #scheduler.step()



def train(train_loader, model, criterion, optimizer, epoch, device, args):

    # switch to train mode
    model.train()

    for i, (images, target) in enumerate(train_loader):

        # move data to the same device as model
        images = images.to(device, non_blocking=True)
        target = target.to(device, non_blocking=True)

        # compute output
        output = model(images)
        loss = criterion(output, target)

        # compute gradient and do SGD step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()


if __name__ == '__main__':
    main()
