#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@FILE    :   action.py
@DSEC    :   网易云音乐签到刷歌脚本
@AUTHOR  :   Secriy
@DATE    :   2020/08/25
@VERSION :   2.2
"""

import os
import requests
import base64
import json
import binascii
import argparse
import random
from Crypto.Cipher import AES


# Get the arguments input.
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("phone", help="your Phone Number")
    parser.add_argument("password", help="MD5 value of the password")
    parser.add_argument("-s", dest="SCKEY", nargs="*", help="SCKEY of the Server Chan")
    parser.add_argument("-l", dest="PLAYLIST", nargs="*", help="your playlist")
    args = parser.parse_args()

    return {"phone": args.phone, "password": args.password, "sckey": args.SCKEY, "playlist": args.PLAYLIST}


# Random String Generator
def create_secret_key(size):
    return str(binascii.hexlify(os.urandom(size))[:16], encoding="utf-8")


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


# Server Chan Turbo
def server_chan_turbo(sendkey, text):
    url = "https://sctapi.ftqq.com/%s.send" % sendkey
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    content = {"title": "网易云打卡脚本", "desp": text}
    ret = requests.post(url, headers=headers, data=content)
    print(ret.text)


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
        sec_key = create_secret_key(16)
        enc_text = aes_encrypt(aes_encrypt(text, self.nonce), sec_key)
        enc_sec_key = rsa_encrypt(sec_key, self.pubKey, self.modulus)
        return {"params": enc_text, "encSecKey": enc_sec_key}


class CloudMusic:
    def __init__(self, phone, password):
        self.session = requests.Session()
        self.enc = Encrypt()
        self.csrf = ""
        self.nickname = ""
        self.login_data = self.enc.encrypt(
            json.dumps({"phone": phone, "countrycode": "86", "password": password, "rememberLogin": "true"})
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
            retext = '"{nickname}" 登录成功，当前等级：{level}\n\n'.format(
                nickname=self.nickname, level=self.get_level()["level"]
            ) + "距离升级还需听{before_count}首歌".format(
                before_count=self.get_level()["nextPlayCount"] - self.get_level()["nowPlayCount"]
            )
            return retext
        else:
            return "登录失败 " + str(ret["code"]) + "：" + ret["message"]

    # Get the level of account.
    def get_level(self):
        url = "https://music.163.com/weapi/user/level?csrf_token=" + self.csrf
        res = self.session.post(url=url, data=self.login_data, headers=self.headers)
        ret = json.loads(res.text)
        return ret["data"]

    # def refresh(self):
    #     url = "https://music.163.com/weapi/login/token/refresh?csrf_token=" + self.csrf
    #     res = self.session.post(url=url,
    #                             data=self.loginData,
    #                             headers=self.headers)
    #     ret = json.loads(res.text)
    #     print(ret)
    #     return ret["code"]

    def sign(self):
        sign_url = "https://music.163.com/weapi/point/dailyTask"
        res = self.session.post(url=sign_url, data=self.enc.encrypt('{"type":0}'), headers=self.headers)
        ret = json.loads(res.text)
        if ret["code"] == 200:
            return "签到成功，经验+" + str(ret["point"])
        elif ret["code"] == -2:
            return "今天已经签到过了"
        else:
            return "签到失败 " + str(ret["code"]) + "：" + ret["message"]

    def task(self, custom):
        url = "https://music.163.com/weapi/v6/playlist/detail?csrf_token=" + self.csrf
        recommend_url = "https://music.163.com/weapi/v1/discovery/recommend/resource"
        music_lists = []
        if not custom:
            res = self.session.post(
                url=recommend_url, data=self.enc.encrypt('{"csrf_token":"' + self.csrf + '"}'), headers=self.headers
            )
            ret = json.loads(res.text)
            if ret["code"] != 200:
                print("获取推荐歌曲失败 " + str(ret["code"]) + "：" + ret["message"])
            else:
                lists = ret["recommend"]
                music_lists = [(d["id"]) for d in lists]
        else:
            music_lists = custom
        music_id = []
        for m in music_lists:
            res = self.session.post(
                url=url,
                data=self.enc.encrypt(json.dumps({"id": m, "n": 1000, "csrf_token": self.csrf})),
                headers=self.headers,
            )
            ret = json.loads(res.text)
            for i in ret["playlist"]["trackIds"]:
                music_id.append(i["id"])
        # print("歌单大小：{musicCount}首\n".format(musicCount=len(music_id)))
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
                            random.sample(music_id, 420 if len(music_id) > 420 else len(music_id)),
                        )
                    )
                )
            }
        )
        res = self.session.post(url="http://music.163.com/weapi/feedback/weblog", data=self.enc.encrypt(post_data))
        ret = json.loads(res.text)
        if ret["code"] == 200:
            return "刷听歌量成功"
        else:
            return "刷听歌量失败 " + str(ret["code"]) + "：" + ret["message"]


if __name__ == "__main__":
    # Get Args
    info = get_args()
    # Start
    app = CloudMusic(info["phone"], info["password"])
    print(30 * "=")
    # Login
    res_login = app.login()
    # Sign In
    res_sign = app.sign()
    # Music Task
    res_task = app.task(info["playlist"])
    # Print Response
    res_print = res_login + "\n\n" + res_sign + "\n\n" + res_task
    print(res_print)
    print(30 * "=")
    # noinspection PyBroadException
    try:
        if info["sckey"]:
            # 调用Server酱
            server_chan_turbo(info["sckey"][0], res_print)
    except Exception:
        print("Server酱调用失败：" + str(Exception))
    print(30 * "=")
