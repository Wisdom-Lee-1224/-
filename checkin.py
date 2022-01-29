from base64 import b64encode
from datetime import datetime
from json import loads
from os import getenv
from traceback import format_exc
from typing import Optional

from Crypto.Cipher import AES
from requests import post


class STUHealth():
    import random
import time
import traceback
from contextlib import contextmanager

import cv2
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


@contextmanager
def selenium(driver):
    try:
        yield
    except Exception as e:
        traceback.print_exc()
        driver.quit()


class SliderCaptcha():

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.driver = webdriver.Chrome(chrome_options=options)

        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        with selenium(self.driver):
            login_url = 'http://dun.163.com/trial/jigsaw'
            self.driver.maximize_window()
            self.driver.get(url=login_url)
            # 点击按钮，触发滑块
            self.driver.find_element_by_xpath(
                '//div[@class="yidun_slider"]'
            ).click()

            # 获取背景图并保存
            background = self.wait.until(
                lambda x: x.find_element_by_xpath('//img[@class="yidun_bg-img"]')
            ).get_attribute('src')
            with open('background.png', 'wb') as f:
                resp = requests.get(background)
                f.write(resp.content)

            # 获取滑块图并保存
            slider = self.wait.until(
                lambda x: x.find_element_by_xpath('//img[@class="yidun_jigsaw"]')
            ).get_attribute('src')
            with open('slider.png', 'wb') as f:
                resp = requests.get(slider)
                f.write(resp.content)

            distance = self.findfic(target='background.png', template='slider.png')
            print(distance)
            # 初始滑块距离边缘 4 px
            trajectory = self.get_tracks(distance + 4)
            print(trajectory)

            # 等待按钮可以点击
            slider_element = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'yidun_jigsaw'))
            )

            # 添加行动链
            ActionChains(self.driver).click_and_hold(slider_element).perform()
            for track in trajectory['plus']:
                ActionChains(self.driver).move_by_offset(
                    xoffset=track,
                    yoffset=round(random.uniform(1.0, 3.0), 1)
                ).perform()
            time.sleep(0.5)

            for back_tracks in trajectory['reduce']:
                ActionChains(self.driver).move_by_offset(
                    xoffset=back_tracks,
                    yoffset=round(random.uniform(1.0, 3.0), 1)
                ).perform()
            #
            for i in [-4, 4]:
                ActionChains(self.driver).move_by_offset(
                    xoffset=i,
                    yoffset=0
                ).perform()

            time.sleep(0.1)
            ActionChains(self.driver).release().perform()
            time.sleep(2)

    def close(self):
        self.driver.quit()

    def findfic(self, target='background.png', template='slider.png'):
        """
        :param target: 滑块背景图
        :param template: 滑块图片路径
        :return: 模板匹配距离
        """
        target_rgb = cv2.imread(target)
        target_gray = cv2.cvtColor(target_rgb, cv2.COLOR_BGR2GRAY)
        template_rgb = cv2.imread(template, 0)
        # 使用相关性系数匹配， 结果越接近1 表示越匹配
        # https://www.cnblogs.com/ssyfj/p/9271883.html
        res = cv2.matchTemplate(target_gray, template_rgb, cv2.TM_CCOEFF_NORMED)
        # opencv 的函数 minMaxLoc：在给定的矩阵中寻找最大和最小值，并给出它们的位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # 因为滑块只需要 x 坐标的距离，放回坐标元组的 [0] 即可
        if abs(1 - min_val) <= abs(1 - max_val):
            distance = min_loc[0]
        else:
            distance = max_loc[0]
        return distance

    def get_tracks(self, distance):
        """
        :param distance: 缺口距离
        :return: 轨迹
        """
        # 分割加减速路径的阀值
        value = round(random.uniform(0.55, 0.75), 2)
        # 划过缺口 20 px
        distance += 20
        # 初始速度，初始计算周期， 累计滑动总距
        v, t, sum = 0, 0.3, 0
        # 轨迹记录
        plus = []
        # 将滑动记录分段，一段加速度，一段减速度
        mid = distance * value
        while sum < distance:
            if sum < mid:
                # 指定范围随机产生一个加速度
                a = round(random.uniform(2.5, 3.5), 1)
            else:
                # 指定范围随机产生一个减速的加速度
                a = -round(random.uniform(2.0, 3.0), 1)
            s = v * t + 0.5 * a * (t ** 2)
            v = v + a * t
            sum += s
            plus.append(round(s))

        # end_s = sum - distance
        # plus.append(round(-end_s))

        # 手动制造回滑的轨迹累积20px
        # reduce = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -1]
        reduce = [-6, -4, -6, -4]
        return {'plus': plus, 'reduce': reduce}


def run():
    spider = SliderCaptcha()
    spider.login()
    spider.close()


if __name__ == '__main__':
    run()
    def __init__(self, username, password) -> None:
        self.api = 'https://stuhealth.jnu.edu.cn/api/'
        self.headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'Content-Type': 'application/json',
            'Origin': 'https://stuhealth.jnu.edu.cn',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://stuhealth.jnu.edu.cn/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.login(username, password)

    def query(self, api, data) -> str:
        response = post(self.api+api, headers=self.headers, json=data)
        result = loads(response.text)
        success = result['meta']['success']
        msg = result['meta']['msg']
        self.result = result
        if not success:
            raise Exception(msg)
        print(msg)
        return msg

    @staticmethod
    def encrypt(password) -> str:
        # Init
        CRYPTOJSKEY = 'xAt9Ye&SouxCJziN'.encode('utf-8')
        BS = AES.block_size
        def _pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        # Hash
        cipher = AES.new(CRYPTOJSKEY, AES.MODE_CBC, CRYPTOJSKEY)
        enrypted = cipher.encrypt(_pad(password).encode('utf-8'))
        enrypted = b64encode(enrypted).decode('utf-8')
        enrypted = enrypted.replace('/', '_').replace('+', '-').replace('=', '*', 1)
        return enrypted

    @staticmethod
    def filter_tables(mainTable, secondTable) -> tuple:
        # Init
        REMOVE_LIST = ['personType', 'id', 'createTime', 'del', 'mainId']
        MAIN_ADD_LIST = ['way2Start']
        MAIN_TO_SECOND = {
            'inChina': 'other1',
            'countryArea': 'other2',
            'personC4': 'other3',
            'personC1': 'other4',
            'personC1id': 'other5',
            'personC2': 'other6',
            'personC2id': 'other7',
            'personC3': 'other8',
            'personC3id': 'other9',
        }
        # Filter Main Table
        new_mainTable = {k: v for k, v in mainTable.items() if v if k not in REMOVE_LIST}
        for i in MAIN_ADD_LIST:
            if i not in new_mainTable:
                new_mainTable[i] = ""
        new_mainTable['declareTime'] = datetime.now().strftime("%Y-%m-%d")
        # Filter Second Table
        if secondTable is not None:
            new_secondTable = {k: v for k, v in secondTable.items() if v if k not in REMOVE_LIST}
        elif mainTable['currentArea'] == "1":
            new_secondTable = {v: mainTable[k] for k, v in MAIN_TO_SECOND.items() if mainTable[k]}
        else:
            new_secondTable = secondTable
        return new_mainTable, new_secondTable

    def login(self, username, password) -> None:
        if len(password) != 24:
            password = self.encrypt(password)
        api = 'user/login'
        data = {"username": username, "password": password}
        self.login_msg = self.query(api, data)
        self.idtype = self.result['data']['idtype']
        self.jnuid = self.result['data']['jnuid']
        self.jnuId = self.result['data']['jnuId']
        self.need_write = (self.result['meta']['code'] == 200)

    def stuinfo(self) -> tuple:
        api = 'user/stuinfo'
        data = {"jnuid": self.jnuid, "idType": self.idtype}
        self.query(api, data)
        mainTable = self.result['data']['mainTable']
        secondTable = self.result['data']['secondTable']
        return mainTable, secondTable

    def stucheckin(self) -> int:
        api = 'user/stucheckin'
        data = {"jnuid": self.jnuid}
        self.query(api, data)
        checkinInfo = self.result['data']['checkinInfo']
        last_id = 0
        for info in checkinInfo:
            if info['flag'] == True:
                last_id = info['id']
                break
        return last_id

    def review(self, id) -> tuple:
        api = 'user/review'
        data = {"jnuid": self.jnuid, "id": id}
        self.query(api, data)
        mainTable = self.result['data']['mainTable']
        secondTable = self.result['data']['secondTable']
        return mainTable, secondTable

    def write(self, mainTable, secondTable) -> str:
        api = 'write/main'
        data = {"jnuid": self.jnuid, "mainTable": mainTable}
        if secondTable is not None:
            data['secondTable'] = secondTable
        msg = self.query(api, data)
        return msg


def sc_send(text, desp='') -> None:
    postdata = {'text': text, 'desp': desp}
    post('https://sctapi.ftqq.com/'+SCKEY+'.send', data=postdata)


def tg_send(desp='') -> None:
    tg_api = 'https://api.telegram.org/bot'+BOTTOKEN+'/sendMessage'
    tg_data = {'chat_id': TGCHATID, 'text': desp}
    post(tg_api, data=tg_data)


def checkin(username, password) -> Optional[str]:
    try:
        stu = STUHealth(username, password)
        if not stu.need_write:
            return
        last_id = stu.stucheckin()
        last_tables = stu.review(last_id)
        tables = stu.filter_tables(*last_tables)
        msg = stu.write(*tables)
        return "打卡{}：{}".format(username, msg)
    except Exception as e:
        print('发生异常{}，详情如下：{}'.format(e, format_exc()))
        return "打卡错误{}：{}".format(username, e)


if __name__ == "__main__":
    # accounts settings
    usernames = getenv('USERNAME', '').split()
    passwords = getenv('PASSWORD', '').split()
    SCKEY = getenv('SCKEY')
    TGCHATID = getenv('TGCHATID')
    BOTTOKEN = getenv('BOTTOKEN')
    # run
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    push_msg = []
    for account in zip(usernames, passwords):
        print("开始打卡...")
        msg = checkin(*account)
        if msg is not None:
            push_msg.append(msg)
    if SCKEY and push_msg:
        print('发送微信推送...')
        sc_send('\n\n'.join(push_msg))
    if BOTTOKEN and push_msg:
        print('发送 Telegram 推送...')
        tg_send('\n\n'.join(push_msg))
