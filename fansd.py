# encoding: utf-8
import re
import subprocess
import shlex
import time
from configparser import ConfigParser

def getConfig():
    config = ConfigParser()
    config.read("config.ini", encoding='UTF-8')
    return config

def getInletTemp():
    """获取进气口温度"""
    pass

def getExhaustTemp():
    """获取出气口温度"""
    pass

def getCPUTemp():
    '''返回CPU的最高温度的那个core的温度'''
    getCPUTempProcessCommand = "sensors | awk '{print $3}'"
    getCPUTempProcess = subprocess.Popen(
        getCPUTempProcessCommand,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    getCPUTempProcess.wait(1)
    outs, errs = getCPUTempProcess.communicate(timeout=1)
    if getCPUTempProcess.poll() == 0:
        # 获取程序运行结束的结束码，通常0为正常返回
        getCPUTempProcess.kill()
        cpus_temp_list = [ float(x) for x in re.findall("\d{1,3}\.\d", outs)]
        # print(cpus_temp_list)
        return max(cpus_temp_list)
    else:
        getCPUTempProcess.kill()
        raise Exception("获取CPU温度失败")

def getGPUTemp():
    '''返回GPU的最高温度的那个core的温度'''
    getGPUTempProcessCommand = "nvidia-smi -q -d TEMPERATURE | grep 'GPU Current Temp'| awk '{print $5}'"
    getGPUTempProcess = subprocess.Popen(
        getGPUTempProcessCommand,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    getGPUTempProcess.wait(1)
    outs, errs = getGPUTempProcess.communicate(timeout=1)
    if getGPUTempProcess.poll() == 0:
        # 获取程序运行结束的结束码，通常0为正常返回
        getGPUTempProcess.kill()
        GPU_temp = re.findall("\d{1,3}", outs)
        GPU_temp_list = [int(x) for x in GPU_temp]
        return max(GPU_temp_list)
    else:
        getGPUTempProcess.kill()
        raise Exception("获取GPU温度失败")


def disableFansAutoSpeed():
    """关闭风扇自动转速。
    由于该设置非永久性更改ipmi配置，所以需要每次运行程序之前，都要运行一遍。
    """
    disableFansAutoSpeedCommand = "ipmitool raw 0x30 0x30 0x01 0x00"
    disableFansAutoSpeedProcess = subprocess.Popen(
        disableFansAutoSpeedCommand,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    disableFansAutoSpeedProcess.wait(1)
    outs, errs = disableFansAutoSpeedProcess.communicate(timeout=1)
    if disableFansAutoSpeedProcess.poll() == 0:
        # 获取程序运行结束的结束码，通常0为正常返回
        disableFansAutoSpeedProcess.kill()
    else:
        disableFansAutoSpeedProcess.kill()

def changeFansSpeed(speed):
    """根据温度调整风扇转速
    :param speed 风扇转速（百分制），传入十进制数字，如100表示风扇满转。
    """
    hexNumber = hex(speed)
    changeFansSpeedCommand = "ipmitool raw 0x30 0x30 0x02 0xff {FANS_SPEED}".format(FANS_SPEED=hexNumber)
    changeFansSpeedProcess = subprocess.Popen(
        changeFansSpeedCommand,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    changeFansSpeedProcess.wait(1)
    outs, errs = changeFansSpeedProcess.communicate(timeout=1)
    if changeFansSpeedProcess.poll() == 0:
        # 获取程序运行结束的结束码，通常0为正常返回
        changeFansSpeedProcess.kill()
    else:
        changeFansSpeedProcess.kill()

def record(cpuTemp, gpuTemp):
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open('record.log', 'w') as f:
        f.write("当前时间: {CURRENT_TIME}\nCPU温度: {CPU_TEMP}\nGPU温度: {GPU_TEMP}".format(CURRENT_TIME=localtime, CPU_TEMP=cpuTemp, GPU_TEMP=gpuTemp))
        f.close()

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # 【预先测试】 如果要快速测试本程序是否会调用硬件，需要取消本段注释
    # print("预先测试，花费30s。检查record.log文件中时间戳是否刷新，检查服务器风扇是否变化。", flush=True)
    # config = getConfig()
    # cpuTemp = getCPUTemp()
    # gpuTemp = getGPUTemp()
    # record(cpuTemp, gpuTemp)
    # print("邮箱测试邮件已发送", flush=True)
    # changeFansSpeed(int('100'))
    # time.sleep(10)
    # changeFansSpeed(int('50'))
    # time.sleep(10)
    # changeFansSpeed(int('30'))
    # time.sleep(10)
    # print("测试结束", flush=True)
    # print("温度及风扇监控程序开始运行", flush=True)
    disableFansAutoSpeed()

    # 【程序运行】
    while True:
        config = getConfig()
        cpuTemp = getCPUTemp()
        gpuTemp = getGPUTemp()
        record(cpuTemp, gpuTemp)
        if cpuTemp >= int(config['high']['cpu']) or gpuTemp >= int(config['high']['gpu']):
            changeFansSpeed(int(config['high']['fans_speed']))
        elif cpuTemp >= int(config['medium']['cpu']) or gpuTemp >= int(config['medium']['gpu']):
            changeFansSpeed(int(config['medium']['fans_speed']))
        elif cpuTemp >= int(config['low']['cpu']) or gpuTemp >= int(config['low']['gpu']):
            changeFansSpeed(int(config['low']['fans_speed']))
        else:
            # 对于low以下温度，采取low级别转速
            changeFansSpeed(int(config['low']['fans_speed']))

        timeSleepTime = int(config['detectFrequency']['time'])
        time.sleep(timeSleepTime)
