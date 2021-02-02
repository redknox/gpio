#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# create date 2021/2/1

"""
步进电机驱动
"""

__author__ = 'Haifeng Kong'

# import RPi.GPIO as GPIO
from collections.abc import Iterable


class SMD(object):
    """
    步进电机控制类，可以控制步进电机的转动角度、转动速度、转动方向。可以指定步进电机转动到某一个角度
    尽可能实现精密控制：既，无论转动多少圈，相同的角度，指向的相位角相同。也就是消除累积误差。
    Attributes:
        angle: int 当前方位角，[0-359] 表示电机轴相对于初始化时转动的方位角
        phase: int 当前脉冲方位角 [0-4095] 以脉冲值记录的电机轴对于初始化时转动的方位角
        speed: int 未特别指定转速时的默认转速，电机转动速度 [0-9] 0档大约每分钟1转，9档
                    大约每分钟14转
        step:  int 当前相位
    """

    SMD_PULSE = [[1, 0, 0, 1],
                 [1, 0, 0, 0],
                 [1, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 1, 0],
                 [0, 0, 1, 0],
                 [0, 0, 1, 1],
                 [0, 0, 0, 1]]

    # 每次脉冲的时间间隔，也就是持续的毫秒数, 28BYJ-48电机标称最大空载牵出频率为900pps，最大空载
    # 牵入频率为500pps，所以在频繁启停场景，建议用8档确保启动正常，启动后再切换9档长时间运行。
    SMD_SPEED = [0.01, 0.009, 0.008, 0.007, 0.006, 0.005, 0.004, 0.003, 0.002, 0.001]

    SMD_PIN = []  # 步进电机引脚

    angle = 0  # 电机当前角度  [0-359]
    phase = 0  # 电机当前脉冲相位 [0-4085]
    speed = 9  # 默认转速9，最快 [0-9]
    step = 0  # 当前相位，[0-7]

    def __init__(self, mode='GPIO.BCM', int1=19, int2=22, int3=23, int4=24):
        '''
        初始化，配置步进电机使用的树莓派引脚。引脚的编号要根据引脚定义模式确定，具体请查询手册
        :param mode: 引脚定义模式，只能是GPIO.BOARD或者GPIO.BCM的一种。
        :param int1|list: 4相位步进电机int1使用的引脚,也可以直接指定一个4位的列表
        :param int2: 4相位步进电机int2使用的引脚
        :param int3: 4相位步进电机int3使用的引脚
        :param int4: 4相位步进电机int4使用的引脚
        '''

        # GPIO.setwarnings(False)   # 关闭警告

        # if mode == GPIO.BCM or mode == GPIO.BOARD:    # 设置引脚编号模式
        #     GPIO.setmode(mode)
        # else:
        #     raise TypeError('GPIO引脚模式输入错误！只能是GPIO.BCM或者GPIO.BOARD!')

        if isinstance(int1, Iterable):
            if len(int1) == 4:
                self.SMD_PIN = int1
            else:
                raise ValueError('4相位电机需要4个引脚值！')
        else:
            self.SMD_PIN = [int1, int2, int3, int4]
        # 检验针脚定义是否合法
        for pin in self.SMD_PIN:
            if not isinstance(pin, int):
                raise TypeError("引脚编号必须为正整数！")

        # if mode == GPIO.BCM:
        #     for jmp in self.SMD_PIN:
        #         if jmp < 2 or jmp > 27:
        #             raise ValueError(f'引脚值{jmp}在GPIO.BCM模式下不合法！')
        # else:
        #     for jmp in self.SMD_PIN:
        #         if jmp not in [3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31, 32, 33, 35, 36,
        #                        37, 38, 40]:
        #             raise ValueError(f'引脚值{jmp}在GPIO.BORAD模式下不合法！')

        self.phase = 0
        self.angle = 0
        self.step = 0

        # 初始化引脚，设置为输出模式，为步进电机加载第一个脉冲  ?(此部分内容是否可以放到以后再做?)

        # GPIO.setup(self.SMD_PIN, GPIO.OUT)
        #
        # for i in range(0, 4):
        #     if self.SMD_PULSE[self.step][i] == 1:
        #         GPIO.output(self.SMD_PIN[i], True)
        #     else:
        #         GPIO.output(self.SMD_PIN[i], False)

    def __del__(self):
        """
        析构函数，释放步进电机占用的引脚
        :return:
        """
        # GPIO.cleanup(self.SMD_PIN)
        pass

    def __turn(self, pules, direction, speed=-1):
        """
        用指定的速度、方向、转动指定的角度。
        :param pules: int >0 电机转动的脉冲数，每4096脉冲转动一周。
        :param direction: int [-1,1] 转动的方向，-1逆时针转动，1正时针转动。
        :param speed: int [0-9] 从慢到快分为10档。9档大约每分钟10转，9档大约每分钟1转。
        """
        if speed == -1:  # 如果没有指定速度，则用对象的速度
            speed = self.speed
        if speed > 9:
            speed = 9
        for i in range(0, pules):
            self.step = self.step + direction
            if self.step == 8:
                self.step = 0
            if self.step == -1:
                self.step = 7
            # for j in range(0, 4):
            #     if self.SMD_PULSE[self.step][j] == 1:
            #         GPIO.output(self.SMD_PIN[j], True)
            #     else:
            #         GPIO.output(self.SMD_PIN[j], False)
            # time.sleep(self.SMD_SPEED(speed))

    def rotate(self, angle, direction=1, speed=-1):
        """
        朝指定的方向、使用指定的速度，转动指定的角度。为了避免积累误差，用转动后的方位角与当前
        方位角之间的角度差来计算实际转动的脉冲数，而不是直接计算输入转动角度对应的脉冲数。可能
        转动同样的角度实际的脉冲数不同。
        :param angle: int 转动的角度。可以为负值，角度值的正负，与direction参数构成亦或关系
                        既：角度值为正，方向值为正，则顺时针转动；角度值为负，方向值为负，则
                        顺指针转动；其他情况为逆时针转动。
        :param direction:int [-1,1] 指定转动方向，需要与angle参数功能确定实际转动方向。
        :param speed:int [0-9] 指定转动速度。
        :return:
        """
        # 验证传入的角度是否合法
        if not isinstance(angle, int):
            try:
                temp = int(angle)
            except TypeError:
                print(f'转动角 {angle} 不合法！')
            else:
                angle = temp

        # 验证传入的方向
        if direction != -1:
            direction = 1

        # 验证传入的速度
        if speed < 0:
            speed = self.speed

        if speed > 9:
            speed = 9

        if angle < 0:  # 如果angle<0 则按照指定方向的反向旋转
            angle *= -1
            direction *= -1

        rounds = angle // 360  # 计算转动的圈数，用于后面的补偿
        countAngle = angle % 360  # 计算与转动初始的方位角差

        dstAngle = self.angle + countAngle * direction  # 转动的目标方位角
        # 将目标方位角设置到0-360度之间
        if dstAngle > 360:
            dstAngle -= 360
        elif dstAngle < 0:
            dstAngle += 360
        # 根据目标方位角换算出脉冲方位角
        dstPhase = self.__angle2phase(dstAngle)

        # 根据转动方向，用目标脉冲方位角和当前脉冲方位角计算需要转动的脉冲数
        if direction == 1:
            turnPhase = dstPhase - self.phase
        else:
            turnPhase = self.phase - dstPhase

        # 将脉冲数变为正值
        if turnPhase < 0:
            turnPhase += 4096

        # 如果旋转超过1圈时补偿脉冲数
        turnPhase += 4096 * rounds

        # 保存新的方位角和脉冲方位角
        self.angle = dstAngle
        self.phase = dstPhase

        print(f'转动脉冲：{turnPhase}\t转动方向{direction}\t转动速度：{speed}')
        print(f'当前角度{self.angle},\t 当前脉冲角度{self.phase}')

        # 调用转动函数进行转动
        # self.__turn(turnPhase, direction, speed)

    def turnTo(self, angle, direction=0, speed=-1):
        """
        转动到指定方向,方向是相对于电机初始化或归零时主轴的位置。如果未指定转动方向，则以最小转动角
        转动到指定位置
        :param angle: int [0-359] 指定转动的目标方向，
        :param direction: int [-1,0,1] 转动的方向，-1位逆时针、1位正时针、0为以最小角度转动,自动
                            选择顺时针或者逆时针方向。
        :param speed: int [0-9] 转动速度
        """
        # 验证角度
        if not isinstance(angle, int):
            try:
                temp = int(angle)
            except ValueError:
                print(f'目标角度{angle}不是合法的值！')
            else:
                angle = temp
        # 验证方向
        if direction != -1 and direction != 0:
            direction = 1
        # 验证速度
        if speed < 0:
            speed = self.speed
        if speed > 9:
            speed = 9
        # 本函数只关心最终指向位置，并不关心旋转的实际数值，最大转动角度不会超过一圈
        if angle > 360 or angle < -360:
            angle = angle % 360
        if angle < 0:
            angle += 360

        turnAngle = angle - self.angle
        if direction == 0:  # 没有指定转动方向，则以转动角度最短的方向转动到指定角度
            if turnAngle > 0:
                if turnAngle <= 180:
                    direction = 1
                else:
                    turnAngle = 360 - turnAngle
                    direction = -1
            else:
                direction = -1
                turnAngle *= -1
                if turnAngle > 180:
                    turnAngle = 360 - turnAngle
                    direction = 1
        else:   # 指定转动方向时，则以指定的方向转动到指定位置
            if turnAngle < 0:
                if direction == -1:
                    turnAngle *= -1
                else:
                    turnAngle = 360 + turnAngle
            else:
                if direction == -1:
                    turnAngle = 360 - turnAngle

        print(f'转动角度{turnAngle},转动方向{direction}')
        self.rotate(turnAngle, direction, speed)

    def zero(self):
        """
        归零 将当前属性内保存的方向值和脉冲角度值清零
        :return:
        """

    def pureAngle(self, angle):
        if angle < 0:
            angle *= -1
        if angle > 360:
            angle = angle % 360

    def __angle2phase(self, angle):
        return int(4096 * (angle / 360) + 0.5)

    # main()函数是入口函数。
    # 如果没有建立单元测试，那么在main()函数里
    # 写对模块的测试。


def main():
    # TODO(konghaifeng@cmcm.com): 写测试。
    smd = SMD('GPIO.BCM', 1, 2, 3, 4)
    print(smd.SMD_PIN)
    smd = SMD('GPIO.BCM', [5, 6, 7, 8])
    print(smd.SMD_PIN)
    for i in range(0, 9):
        smd.rotate(25)
    print('=========================')
    smd.turnTo(333, 1)
    print('=========================')
    smd.turnTo(355, 1)
    print('=========================')
    smd.turnTo(350, 1)
    print('=========================')
    smd.turnTo(359, 1)


if __name__ == '__main__':
    main()
