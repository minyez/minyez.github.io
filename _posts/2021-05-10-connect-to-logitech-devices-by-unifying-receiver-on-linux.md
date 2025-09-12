---
title: Connect to Logitech devices by Unifying Receiver on Linux (CN)
date: 2021-05-10 09:46:59 +0800
categories: [programming,]
tags: [Linux, Logitech, USB]
lang: zh-CN
math: false
comments: true
---

使用 USB 接收器使 Logitech 设备正确接入 Linux.
本文是对链接[^1]的重述. 具体步骤如下.

## 第一步: 编译文件

将下面的代码拷贝为 `unifying_pair.c`
```c
/*
* Copyright 2011 Benjamin Tissoires 
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see .
*/

#include <linux/input.h>
#include <linux/hidraw.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>

#define USB_VENDOR_ID_LOGITECH                  (__u32)0x046d
#define USB_DEVICE_ID_UNIFYING_RECEIVER         (__s16)0xc52b
#define USB_DEVICE_ID_UNIFYING_RECEIVER_2       (__s16)0xc532

int main(int argc, char **argv)
{
    int fd;
    int res;
    struct hidraw_devinfo info;
    char magic_sequence[] = {0x10, 0xFF, 0x80, 0xB2, 0x01, 0x00, 0x00};

    if (argc == 1) {
        errno = EINVAL;
        perror("No hidraw device given");
        return 1;
    }

    /* Open the Device with non-blocking reads. */
    fd = open(argv[1], O_RDWR|O_NONBLOCK);

    if (fd < 0) {
        perror("Unable to open device");
        return 1;
    }

    /* Get Raw Info */
    res = ioctl(fd, HIDIOCGRAWINFO, &info);
    if (res < 0) {
        perror("error while getting info from device");
    } else {
        if (info.bustype != BUS_USB ||
            info.vendor != USB_VENDOR_ID_LOGITECH ||
            (info.product != USB_DEVICE_ID_UNIFYING_RECEIVER &&
             info.product != USB_DEVICE_ID_UNIFYING_RECEIVER_2)) {
                errno = EPERM;
                perror("The given device is not a Logitech "
                        "Unifying Receiver");
                return 1;
        }
    }

    /* Send the magic sequence to the Device */
    res = write(fd, magic_sequence, sizeof(magic_sequence));
    if (res < 0) {
        printf("Error: %d\n", errno);
        perror("write");
    } else if (res == sizeof(magic_sequence)) {
        printf("The receiver is ready to pair a new device.\n"
        "Switch your device on to pair it.\n");
    } else {
        errno = ENOMEM;
        printf("write: %d were written instead of %ld.\n", res,
                sizeof(magic_sequence));
        perror("write");
    }
    close(fd);
    return 0;
}
```

编译
```bash
$ gcc -o unifying_pair unifying_pair.c
```

## 第二步: 寻找 USE 接收器的设备号

接入 USB Receiver. 然后在终端输入以下命令
```bash
$ grep -H NAME /sys/class/hidraw/hidraw*/device/uevent
/sys/class/hidraw/hidraw0/device/uevent:HID_NAME=Compx 2.4G Receiver
/sys/class/hidraw/hidraw1/device/uevent:HID_NAME=Compx 2.4G Receiver
/sys/class/hidraw/hidraw2/device/uevent:HID_NAME=Logitech USB Receiver
```

可以看到 `hidraw2` 对应的是 USB 接收器. 

## 第三步: 配对

在得到第二步设备号后, 在保持要连接设备关闭的情况下 sudo 执行

```bash
$ sudo ./unifying_pair /dev/hidraw2
```

此时再打开 MX Keys 或者 MX Master 3 等 Logitech 设备, 切换到未被占据的端口, 即可正确连接.

-----

[^1]: <https://wiki.archlinux.org/title/Logitech_Unifying_Receiver>
