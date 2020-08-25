#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@FILE    :   action.py
@DSEC    :   网易云音乐签到刷歌脚本
@AUTHOR  :   Secriy
@DATE    :   2020/08/25
@VERSION :   1.0
'''

import os
import sys
import requests
import base64
import json
import hashlib
import binascii
import codecs
from Crypto.Cipher import AES


class Encrypt:
    def __init__(self):
        self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.nonce = '0CoJUm6Qyw8W8jud'
        self.pubKey = '010001'

    # Random String Generator
    def createSecretKey(self, size):
        return str(binascii.hexlify(os.urandom(size))[:16], encoding='utf-8')

    # AES Encrypt
    def aesEncrypt(self, text, secKey):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(secKey.encode('utf8'), 2, b'0102030405060708')
        ciphertext = encryptor.encrypt(text.encode('utf8'))
        ciphertext = str(base64.b64encode(ciphertext), encoding='utf-8')
        return ciphertext

    # RSA Encrypt
    def rsaEncrypt(self, text, pubKey, modulus):
        text = text[::-1]
        rs = int(text.encode('utf-8').hex(), 16)**int(pubKey, 16) % int(
            modulus, 16)
        return format(rs, 'x').zfill(256)

    # md5 Compute
    def md5(self, str):
        hl = hashlib.md5()
        hl.update(str.encode(encoding='utf-8'))
        return hl.hexdigest()

    def encrypt(self, text):
        secKey = self.createSecretKey(16)
        encText = self.aesEncrypt(self.aesEncrypt(text, self.nonce), secKey)
        encSecKey = self.rsaEncrypt(secKey, self.pubKey, self.modulus)
        return {'params': encText, 'encSecKey': encSecKey}


class CloudMusic:
    def __init__(self):
        self.loginUrl = "https://music.163.com/weapi/login/cellphone"
        self.signUrl = "https://music.163.com/weapi/point/dailyTask"
        self.taskUrl = "https://music.163.com/weapi/v1/discovery/recommend/resource"
        self.session = requests.Session()
        self.enc = Encrypt()
        self.headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
            "Referer": "http://music.163.com/",
            "Accept-Encoding": "gzip, deflate",
        }

    def login(self, phone, password):
        loginData = self.enc.encrypt(
            json.dumps({
                'phone': phone,
                'countrycode': '86',
                'password': self.enc.md5(password),
                'rememberLogin': 'true'
            }))
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
            "Referer":
            "http://music.163.com/",
            "Accept-Encoding":
            "gzip, deflate",
            "Cookie":
            "os=pc; osver=Microsoft-Windows-10-Professional-build-10586-64bit; appver=2.0.3.131777; channel=netease; __remember_me=true;"
        }
        res = self.session.post(url=self.loginUrl,
                                data=loginData,
                                headers=headers)
        self.cookie = res.cookies
        ret = json.loads(res.text)
        if ret['code'] == 200:
            print("登录成功")
        else:
            print("登录失败" + str(ret['code']) + "：" + ret['message'])

    def sign(self):
        res = self.session.post(url=self.signUrl,
                                data=self.enc.encrypt('{"type":0}'),
                                headers=self.headers)
        ret = json.loads(res.text)
        if ret['code'] == 200:
            print("签到成功，经验+" + str(ret['point']))
        elif ret['code'] == -2:
            print("重复签到")
        else:
            print("签到失败" + str(ret['code']) + "：" + ret['message'])

    def task(self):
        csrf = requests.utils.dict_from_cookiejar(self.cookie)['__csrf']
        url = "https://music.163.com/weapi/v6/playlist/detail?csrf_token=" + csrf
        res = self.session.post(url=self.taskUrl,
                                data=self.enc.encrypt('{"csrf_token":"' +
                                                      csrf + '"}'),
                                headers=self.headers)
        ret = json.loads(res.text)
        if ret['code'] != 200:
            print("获取推荐歌曲失败")
        else:
            lists = ret['recommend']
        musicId = []
        for m in lists:
            print(m['id'])
            res = self.session.post(url=url,
                                    data=self.enc.encrypt(
                                        json.dumps({
                                            'id': m['id'],
                                            'n': 1000,
                                            'csrf_token': csrf
                                        })),
                                    headers=self.headers)
            ret = json.loads(res.text)
            for i in ret['playlist']['trackIds']:
                musicId.append(i['id'])
        postData = json.dumps({
            'logs':
            json.dumps(
                list(
                    map(
                        lambda x: {
                            'action': 'play',
                            'json': {
                                'download': 0,
                                'end': 'playend',
                                'id': x,
                                'sourceId': '',
                                'time': 240,
                                'type': 'song',
                                'wifi': 0
                            }
                        }, musicId)))
        })
        res = self.session.post(
            url="http://music.163.com/weapi/feedback/weblog",
            data=self.enc.encrypt(postData))
        ret = json.loads(res.text)
        if ret['code'] == 200:
            print("刷单成功！共" + str(len(musicId)) + "首")
            exit()
        else:
            print("发生错误：" + str(ret['code']) + ret['message'])
            exit(ret['code'])


if __name__ == "__main__":
    # 自定义歌单
    # customMusicList = ""
    app = CloudMusic()
    # pylint: disable=unbalanced-tuple-unpacking
    phone, passowrd = sys.argv[1:3]
    # Login
    app.login(phone, passowrd)
    # Sign In
    app.sign()
    # Music Task
    app.task()
