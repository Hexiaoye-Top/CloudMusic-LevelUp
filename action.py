# -*- encoding: utf-8 -*-
"""
@FILE    :   action.py
@DSEC    :   网易云音乐签到刷歌脚本
@AUTHOR  :   Secriy
@DATE    :   2020/08/25
@VERSION :   2.6
"""

import datetime
import os
import requests
import base64
import sys
import binascii
import argparse
import random
import hashlib
from Crypto.Cipher import AES
import json


# Get the arguments input.
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("phone", help="Your Phone Number.")
    parser.add_argument("password", help="The plaint text or MD5 value of the password.")
    parser.add_argument("-s", dest="sc_key", nargs=1, help="The SCKEY of the Server Chan.")
    parser.add_argument("-t", dest="tg_bot_key", nargs=2, help="The Token and Chat ID of your telegram bot.")
    parser.add_argument("-b", dest="bark_key", nargs=1, help="The key of your bark app.")
    parser.add_argument("-w", dest="wecom_key", nargs=3, help="Your Wecom ID, App-AgentID and App-Secrets.")
    parser.add_argument("-p", dest="push_plus_key", nargs=1, help="The token of your pushplus account.")
    args = parser.parse_args()

    return {
        "phone": args.phone,
        "password": args.password,
        "sc_key": args.sc_key,
        "tg_bot_key": args.tg_bot_key,
        "bark_key": args.bark_key,
        "wecom_key": args.wecom_key,
        "push_plus_key": args.push_plus_key,
    }


# Calculate the MD5 value of text
def calc_md5(text):
    md5_text = hashlib.md5(text.encode(encoding="utf-8")).hexdigest()
    return md5_text


# AES Encrypt
def aes_encrypt(text, sec_key):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(sec_key.encode("utf8"), 2, b"0102030405060708")
    ciphertext = encryptor.encrypt(text.encode("utf8"))
    ciphertext = str(base64.b64encode(ciphertext), encoding="utf-8")
    return ciphertext


# RSA Encrypt
def rsa_encrypt(text, pub_key, modulus):
    text = text[::-1]
    rs = int(text.encode("utf-8").hex(), 16) ** int(pub_key, 16) % int(modulus, 16)
    return format(rs, "x").zfill(256)


class Push:
    def __init__(self, text):
        self.text = text

    # Server Chan Turbo Push
    def server_chan_push(self, arg):
        url = "https://sctapi.ftqq.com/{0}.send".format(arg[0])
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        content = {"title": "网易云打卡", "desp": self.text}
        ret = requests.post(url, headers=headers, data=content)
        print("ServerChan: " + ret.text)

    # Telegram Bot Push
    def telegram_push(self, arg):
        url = "https://api.telegram.org/bot{0}/sendMessage".format(arg[0])
        data = {
            "chat_id": arg[1],
            "text": self.text,
        }
        ret = requests.post(url, data=data)
        print("Telegram: " + ret.text)

    # Bark Push
    def bark_push(self, arg):
        data = {"title": "网易云打卡", "body": self.text}
        headers = {"Content-Type": "application/json;charset=utf-8"}
        url = "https://api.day.app/{0}/?isArchive={1}".format(arg[0], arg[1])
        ret = requests.post(url, json=data, headers=headers)
        print("Bark: " + ret.text)

    # PushPlus Push
    def push_plus_push(self, arg):
        url = "http://www.pushplus.plus/send?token={0}&title={1}&content={2}&template={3}".format(
            arg[0], "网易云打卡", self.text, "html"
        )
        ret = requests.get(url)
        print("pushplus: " + ret.text)

    # Wecom Push
    def wecom_id_push(self, arg):
        body = {
            "touser": "@all",
            "msgtype": "text",
            "agentid": arg[1],
            "text": {"content": self.text},
            "safe": 0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800,
        }
        access_token = requests.get(
            "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(str(arg[0]), arg[2])
        ).json()["access_token"]
        res = requests.post(
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}".format(access_token),
            data=json.dumps(body),
        )
        ret = res.json()
        if ret["errcode"] != 0:
            print("微信推送配置错误")
        else:
            print("Wecom: " + ret)


class Encrypt:
    def __init__(self):
        self.modulus = (
            "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629"
            "ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d"
            "813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7 "
        )
        self.nonce = "0CoJUm6Qyw8W8jud"
        self.pubKey = "010001"

    def encrypt(self, text):
        # Random String Generator
        sec_key = str(binascii.hexlify(os.urandom(16))[:16], encoding="utf-8")
        enc_text = aes_encrypt(aes_encrypt(text, self.nonce), sec_key)
        enc_sec_key = rsa_encrypt(sec_key, self.pubKey, self.modulus)
        return {"params": enc_text, "encSecKey": enc_sec_key}


class CloudMusic:
    def __init__(self, phone, country_code, password):
        self.session = requests.Session()
        self.enc = Encrypt()
        self.phone = phone
        self.csrf = ""
        self.nickname = ""
        self.uid = ""
        self.login_data = self.enc.encrypt(
            json.dumps({"phone": phone, "countrycode": country_code, "password": password, "rememberLogin": "true"})
        )
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.89 "
            "Safari/537.36",
            "Referer": "http://music.163.com/",
            "Accept-Encoding": "gzip, deflate",
        }

    def login(self):
        login_url = "https://music.163.com/weapi/login/cellphone"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.89 Safari/537.36",
            "Referer": "http://music.163.com/",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": "os=pc; osver=Microsoft-Windows-10-Professional-build-10586-64bit; appver=2.0.3.131777; "
            "channel=netease; __remember_me=true;",
        }
        res = self.session.post(url=login_url, data=self.login_data, headers=headers)
        ret = json.loads(res.text)
        if ret["code"] == 200:
            self.csrf = requests.utils.dict_from_cookiejar(res.cookies)["__csrf"]
            self.nickname = ret["profile"]["nickname"]
            self.uid = ret["account"]["id"]
            level = self.get_level()
            text = '"{nickname}" 登录成功，当前等级：{level}\n\n距离升级还需听{count}首歌\n\n距离升级还需登录{days}天'.format(
                nickname=self.nickname,
                level=level["level"],
                count=level["nextPlayCount"] - level["nowPlayCount"],
                days=level["nextLoginCount"] - level["nowLoginCount"],
            )
        else:
            text = "账号 {0} 登录失败: ".format(self.phone) + str(ret["code"])
        return text

    # Get the level of account.
    def get_level(self):
        url = "https://music.163.com/weapi/user/level?csrf_token=" + self.csrf
        res = self.session.post(url=url, data=self.login_data, headers=self.headers)
        ret = json.loads(res.text)
        return ret["data"]

    def sign(self, tp=0):
        sign_url = "https://music.163.com/weapi/point/dailyTask?{csrf}".format(csrf=self.csrf)
        res = self.session.post(url=sign_url, data=self.enc.encrypt('{{"type":{0}}}'.format(tp)), headers=self.headers)
        ret = json.loads(res.text)
        sign_type = "安卓端" if tp == 0 else "PC/Web端"
        if ret["code"] == 200:
            text = "{0}签到成功，经验+{1}".format(sign_type, str(ret["point"]))
        elif ret["code"] == -2:
            text = "{0}今天已经签到过了".format(sign_type)
        else:
            text = "签到失败 " + str(ret["code"]) + "：" + ret["message"]
        return text

    def get_recommend_playlists(self):
        recommend_url = "https://music.163.com/weapi/v1/discovery/recommend/resource"
        res = self.session.post(
            url=recommend_url, data=self.enc.encrypt('{"csrf_token":"' + self.csrf + '"}'), headers=self.headers
        )
        ret = json.loads(res.text)
        playlists = []
        if ret["code"] == 200:
            playlists.extend([(d["id"]) for d in ret["recommend"]])
        else:
            print("获取推荐歌曲失败 " + str(ret["code"]) + "：" + ret["message"])
        return playlists

    def get_subscribe_playlists(self):
        private_url = "https://music.163.com/weapi/user/playlist?csrf_token=" + self.csrf
        res = self.session.post(
            url=private_url,
            data=self.enc.encrypt(json.dumps({"uid": self.uid, "limit": 1001, "offset": 0, "csrf_token": self.csrf})),
            headers=self.headers,
        )
        ret = json.loads(res.text)
        subscribed_lists = []
        if ret["code"] == 200:
            for li in ret["playlist"]:
                if li["subscribed"]:
                    subscribed_lists.append(li["id"])
        else:
            print("个人订阅歌单获取失败 " + str(ret["code"]) + "：" + ret["message"])
        return subscribed_lists

    def get_musics(self):
        detail_url = "https://music.163.com/weapi/v6/playlist/detail?csrf_token=" + self.csrf
        musics = []
        for m in self.get_recommend_playlists():
            res = self.session.post(
                url=detail_url,
                data=self.enc.encrypt(json.dumps({"id": m, "n": 1000, "csrf_token": self.csrf})),
                headers=self.headers,
            )
            ret = json.loads(res.text)
            musics.extend([i["id"] for i in ret["playlist"]["trackIds"]])
        amount = 320 - len(musics)
        if amount <= 0:
            musics = random.sample(musics, 320)
            amount = 200
        for m in self.get_subscribe_playlists():
            res = self.session.post(
                url=detail_url,
                data=self.enc.encrypt(json.dumps({"id": m, "n": 1000, "csrf_token": self.csrf})),
                headers=self.headers,
            )
            ret = json.loads(res.text)
            random.seed(datetime.datetime.now())  # Random
            track_ids = [i["id"] for i in ret["playlist"]["trackIds"]]
            if len(track_ids) > amount:
                musics.extend(random.sample(track_ids, amount))
            else:
                musics.extend(track_ids)
        return musics

    def task(self):
        feedback_url = "http://music.163.com/weapi/feedback/weblog"
        post_data = json.dumps(
            {
                "logs": json.dumps(
                    list(
                        map(
                            lambda x: {
                                "action": "play",
                                "json": {
                                    "download": 0,
                                    "end": "playend",
                                    "id": x,
                                    "sourceId": "",
                                    "time": 240,
                                    "type": "song",
                                    "wifi": 0,
                                },
                            },
                            self.get_musics(),
                        )
                    )
                )
            }
        )
        res = self.session.post(url=feedback_url, data=self.enc.encrypt(post_data))
        ret = json.loads(res.text)
        if ret["code"] == 200:
            text = "刷听歌量成功"
        else:
            text = "刷听歌量失败 " + str(ret["code"]) + "：" + ret["message"]
        return text


def run_task(info, phone, password):
    # Start
    country_code = "86"
    if "+" in phone:
        country_code = str(phone).split("+")[0]
        phone = str(phone).split("+")[1]
    app = CloudMusic(phone, country_code, password)
    # Login
    res_login = app.login()
    print(res_login, end="\n\n")
    if "400" in res_login:
        print(res_login)
        print(30 * "=")
        return
    # Sign In
    res_sign = app.sign()
    print(res_sign, end="\n\n")
    # Mobile Sign In
    res_m_sign = app.sign(1)
    print(res_m_sign, end="\n\n")
    # Music Task
    res_task = "刷听歌量失败"
    for i in range(1):
        res_task = app.task()
        print(res_task)
    print(30 * "=")
    try:
        # Push
        push = Push(res_login + "\n\n" + res_sign + "\n\n" + res_m_sign + "\n\n" + res_task)
        # ServerChan
        if info["sc_key"]:
            push.server_chan_push(info["sc_key"])
        # Bark
        if info["bark_key"]:
            push.bark_push(info["bark_key"])
        # Telegram
        if info["tg_bot_key"]:
            push.telegram_push(info["tg_bot_key"])
        # pushplus
        if info["push_plus_key"]:
            push.push_plus_push(info["push_plus_key"])
        # 企业微信
        if info["wecom_key"]:
            push.wecom_id_push(info["wecom_key"])
    except Exception as err:
        print(err)
    print(30 * "=")


def task_pool(infos):
    phone_list = infos["phone"].split(",")
    passwd_list = infos["password"].split(",")
    # Run tasks
    for k, v in enumerate(phone_list):
        print(30 * "=")
        if not passwd_list[k]:
            break
        if len(passwd_list[k]) == 32:
            run_task(infos, phone_list[k], passwd_list[k])
        else:
            run_task(infos, phone_list[k], calc_md5(passwd_list[k]))


if __name__ == "__main__":
    # Get arguments
    task_pool(get_args())
