

# Overview

**fansd**是用来控制服务器的风扇转速的，可以实时修改`config.ini`配置文件，程序会实时读取。

# requirement

`sudo apt install -y ipmitool lm-sensors`

### 控制风扇转速

首先需要设置风扇转速可控，关闭风扇自动调整转速：`ipmitool raw 0x30 0x30 0x01 0x00`，该命令每次运行都需要执行一次。

要求服务器安装`ipmitool `,并且可以本地运行`ipmitool raw 0x30 0x30 0x02 0xff 0x32`这种命令。

ipmitool不仅可以控制风扇转速，也可以获取进风口(Inlet Temp)和出风口(Exhaust Temp)的温度

执行`ipmitool sensor list | grep -i temp`可以获取进风口出风口的温度。

### 获取CPU温度

安装`lm-sensors`命令，可以获取CPU温度。

执行命令:`sensors | awk '{print $3}'`获取CPU每个核心的温度。如205的机器，拥有两个cpu，单个cpu有14核心。

### 获取GPU温度

需要安装N卡驱动，需要可以正确执行命令`nvidia-smi`。

通过命令`nvidia-smi -q -d TEMPERATURE | grep 'GPU Current Temp'| awk '{print $5}'`获取GPU温度。

获取显卡的温度相关内容: `nvidia-smi -q -d TEMPERATURE`

输出如下，可以看到GPU本身有**Shutdown Temp**和**Slowdown Temp**，存在控制降频、自动关机的温度阈值。

```
==============NVSMI LOG==============

Timestamp                                 : Fri May  5 01:49:08 2023
Driver Version                            : 530.41.03
CUDA Version                              : 12.1

Attached GPUs                             : 2
GPU 00000000:04:00.0
    Temperature
        GPU Current Temp                  : 46 C
        GPU Shutdown Temp                 : 96 C
        GPU Slowdown Temp                 : 93 C
        GPU Max Operating Temp            : 86 C
        GPU Target Temperature            : N/A
        Memory Current Temp               : N/A
        Memory Max Operating Temp         : N/A

GPU 00000000:05:00.0
    Temperature
        GPU Current Temp                  : 45 C
        GPU Shutdown Temp                 : 96 C
        GPU Slowdown Temp                 : 93 C
        GPU Max Operating Temp            : 86 C
        GPU Target Temperature            : N/A
        Memory Current Temp               : N/A
        Memory Max Operating Temp         : N/A
```

# 温度记录

会记录目录在文件`record.log`中。
