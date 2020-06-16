# -*- coding: utf8 -*-
import json
import smtplib
import time
import logging
from datetime import datetime,timezone,timedelta
from email.mime.text import MIMEText
from email.header import Header
import requests

# hird-party SMTP service taking QQ mailbox as an example. 第三方 SMTP 服务,以QQ邮箱为例
# 常用SMTP服务器地址及端口
'''
    163.com：
        SMTP服务器地址:smtp.163.com（端口：25）
    126邮箱：
        SMTP服务器地址:smtp.126.com（端口：25）
    139邮箱：
        SMTP服务器地址：SMTP.139.com（端口：25）
    QQ邮箱：
        SMTP服务器地址：smtp.qq.com（端口：465）
    QQ企业邮箱 ：
        SMTP服务器地址：smtp.exmail.qq.com（SSL启用 端口：587/465）

    ...

    此代码以QQ邮箱为例，如需更多请自行百度后替换SMTP服务器和对应端口
'''
mail_host="smtp.mxhichina.com"             # SMTP server. SMTP服务器
mail_port=465                               # SMTP service port. SMTP服务端口

##-------------------------------- 签到配置START--------------------------------

mail_user="marisa@touhou-project.org"             # Username 用户名(账号A,填写发送邮件的账号)
mail_pass="PP123456pp"                  # SMTP service password. SMTP服务的口令(账号A的邮箱密码)
my_sender='marisa@touhou-project.org'             # 发件人邮箱账号(与账号A一致即可)
my_user='1306174256@qq.com'               # 收件人邮箱账号(账号B,填写需要收件的邮件的账号)

# 签到成功是否发送邮件提醒，默认设置不发送
# 可选值：
#   False 不发送
#   True 发送
success_send_mail_status = True;

# 签到失败是否发送邮件提醒，默认设置不发送
# 可选值：
#   False 不发送
#   True 发送
fail_send_mail_status = True;

'''
    填入账号密码，加密pwd获取方式如下
    1、访问本站接口https://music.cloudsvip.club/api.php?do=getSign&uin=账号&pwd=密码，可直接获取
    2、百度MD5加密网站进行密码加密后替换pwd
'''
uin = '17877201708'                         # 网易云账号
pwd = '27c2776c61f0dae6aea43eebd10a801e'    # 网易云密码

##-------------------------------- 签到配置END--------------------------------


##-------------------------------- 以下代码一般情况下无需改动--------------------

def main_handler(event, context):

    # 网易云移动端和PC端签到(不含打卡功能)

    # 建议此函数设置为一天执行一次即可,签到只有每天第一次签到会成功,后面再次执行则会失败(若开启邮件提醒，则会触发邮件提醒功能)
    
    base_url =      "https://music.cloudsvip.club"
    login_url =     base_url + "/api.php?do=login"      # 登录URL
    daka_url =      base_url + "/api.php?do=daka"       # 打卡URL
    sign_url =      base_url + "/api.php?do=sign"       # 移动端签到URL
    signpc_url =    base_url + "/api.php?do=signpc"     # PC端签到URL

    # daka_url =      base_url + "/api.php?do=daka"     # 打卡URL，请阅读102行代码注释
    
    data= {'uin': uin,'pwd': pwd}

    nickName = ''
    userId = ''
    mobileResult = ''
    mobileCode = ''
    PCResult = ''
    PCCode = ''
    QDresult = ''
    result = ''
    sign_status = False
    signpc_status = False

    req = requests.post(login_url, data = data ) 
    cookies = req.cookies

    # 登录判断
    # reqJsonObj = json.loads(req.text)
    # if reqJsonObj['code'] == 200:
    #     nickName = reqJsonObj['profile']['nickname']
        
    # else:
    #     return str(reqJsonObj['msg']) + ': ' + str(reqJsonObj['code'])

    # 登录判断
    reqJsonObj = json.loads(req.text)
    
    if reqJsonObj['code'] == 200:
        nickName = reqJsonObj['profile']['nickname']
        userId = reqJsonObj['profile']['userId']
    elif reqJsonObj['code'] == 400:
        return '登录异常，请检查账号密码格式是否正确！' + '，返回码: ' + str(reqJsonObj['code'])
    else :
        return str(reqJsonObj['message']) + '，返回码: ' + str(reqJsonObj['code'])
    
    mobile = uin.replace(uin[3:11], '********')

    uid = str(userId).replace(str(userId)[3:9], '*******')

    dt0 = datetime.utcnow().replace(tzinfo=timezone.utc)

    dt8 = dt0.astimezone(timezone(timedelta(hours=8))) # 转换时区到东八区

    dt = datetime.strftime(dt8,'%Y-%m-%d %H:%M:%S')

    ##-------------------------------- 签到功能START-------------------------------- 
    # 移动端签到
    sign = requests.post(sign_url, cookies = cookies)
    signJsonObj = json.loads(sign.text)
    if signJsonObj['code'] == 200:
        mobileResult = '云贝 +' +  str(signJsonObj['point'])
        mobileCode = str(signJsonObj['code'])
        sign_status = True
    else:
        mobileResult = str(signJsonObj['msg'])
        mobileCode = str(signJsonObj['code'])

    # PC端签到
    signpc = requests.post(signpc_url, cookies = cookies)
    signPcJsonObj = json.loads(signpc.text)
    if signPcJsonObj['code'] == 200:
        PCResult = '云贝 +' +  str(signPcJsonObj['point'])
        PCCode = str(signJsonObj['code'])
        signpc_status = True
    else:
        PCResult = str(signPcJsonObj['msg'])
        PCCode = str(signJsonObj['code'])
    ##-------------------------------- 签到功能END-------------------------------- 


    ##-------------------------------- 打卡功能START-------------------------------- 
    daka = requests.post(daka_url, cookies = cookies)
    dakaJsonObj = json.loads(daka.text)
    if dakaJsonObj['code'] == 200:
        QDresult = '听歌量+ ' + str(dakaJsonObj['count']) 
    else:
        result += '打卡失败: 未知错误'
    ##-------------------------------- 打卡功能END-------------------------------- 


    if sign_status and signpc_status:
        status = '成功'
    else:
        status = '失败'

    # 邮件发送模板
    content = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>网易云音乐签到</title></head><body><div style="width: 550px;height: auto;border-radius: 5px;margin:0 auto;box-shadow: 0px 0px 20px #888888;position: relative;padding-bottom: 5px;"><div style="background-image: url(https://s1.ax1x.com/2020/06/15/NCSYLQ.md.jpg);width:550px;height: 300px;background-size: cover;background-repeat: no-repeat;border-radius: 5px 5px 0px 0px;"></div><div style="width: 230px;height: 40px;background-color: rgb(255, 114, 114);margin-top: -20px;margin-left: 20px;box-shadow: 3px 3px 3px rgba(0, 0, 0, 0.3);color: rgb(255, 255, 255);text-align: center;line-height: 40px;">Dear:'+ nickName +'</div><div style="background-color:white;line-height:180%;padding:0 15px 12px;width:520px;margin:30px auto;color:#555555;font-family:\'Century Gothic\',\'Trebuchet MS\',\'Hiragino Sans GB\',微软雅黑,\'Microsoft Yahei\',Tahoma,Helvetica,Arial,\SimSun\',sans-serif;font-size:12px;margin-bottom: 0px;"><h2 style="font-size:14px;font-weight:normal;padding:13px 0 10px 8px;">您的云函数定时任务<span style="text-decoration:none;color: #ff7272;">网易云音乐签到</span>执行'+ status +'了呐~</h2><div style="padding:0 12px 0 12px;margin-top: 10px"><style type="text/css">.comment>img{margin:0px 6px 5px 6px;width:25px}</style><p>用户信息：</p><p style="background-color: #f5f5f5;border: 0px solid #DDD;border-radius: 6px;padding: 6px 15px;margin:18px 0">ID：<span style="text-decoration:none;color: #ff7272;">' + uid + '</span><br/>账号：<span style="text-decoration:none;color: #ff7272;">'+ mobile +'</span><br/>登录时间：<span style="text-decoration:none;color: #ff7272;">'+ dt +'</span><br/></p><p>任务明细：</p><table cellpadding="6"width="100%"class="comment"style="text-align:center;background-color: #f5f5f5;border: 0px solid #DDD;border-radius: 6px;padding: 6px 15px;margin:18px 0"><tr><td>任务</td><td>状态</td><td>执行结果</td></tr><tr><td>移动端签到</td><td>'+ mobileCode +'</td><td>'+ mobileResult +'</td></tr><tr><td>桌面端签到</td><td>'+ PCCode +'</td><td>'+ PCResult +'</td></tr><tr><td>云音乐打卡</td><td>'+ QDresult +'</td><td>'+ result +'</td></tr></table></p></div></div><div style="color:#8c8c8c;;font-family: \'Century Gothic\',\'Trebuchet MS\',\'Hiragino Sans GB\',微软雅黑,\'Microsoft Yahei\',Tahoma,Helvetica,Arial,\'SimSun\',sans-serif;font-size: 10px;width: 100%;text-align: center;word-wrap:break-word;margin-top: -30px;"><p style="padding:20px;">萤火虫消失之后，那光的轨迹仍久久地印在我的脑际。那微弱浅淡的光点，仿佛迷失方向的魂灵，在漆黑厚重的夜幕中彷徨。——《挪威的森林》村上春树</p></div><a style="text-decoration:none; color:#FFF;width: 40%;text-align: center;background-color:#ff7272;height: 42px;line-height: 42px;box-shadow: 1px 1px 1px rgba(0, 0, 0, 0.30);margin: -10px auto;display: block;border-radius: 32px;"href="https://music.cloudsvip.club"target="_blank">前往网易云音乐打卡网站</a><div style="color:#8c8c8c;;font-family: \'Century Gothic\',\'Trebuchet MS\',\'Hiragino Sans GB\',微软雅黑,\'Microsoft Yahei\',Tahoma,Helvetica,Arial,\'SimSun\',sans-serif;font-size: 10px;width: 100%;text-align: center;margin-top: 30px;"><p>本邮件为系统自动发送，请勿直接回复~</p></div></div></body></html>'
    # 判断双端签到是否成功
    if sign_status and signpc_status:
        # 判断签到成功是否发送邮件
        if success_send_mail_status:
            # 发送邮件成功提醒
            if sendEmail(my_sender, my_user, '网易云音乐签到' + status + '提醒', content):
                return "SEND EMAIL SUCCESS"
            else:
                return "SEND EMAIL FAIL"
        else:
            return "CHECK IN SUCCESS"
    else:
        # 判断签到失败是否发送邮件
        if fail_send_mail_status:
            # 发送邮件失败提醒
            if sendEmail(my_sender, my_user, '网易云音乐签到' + status + '提醒', content):
                return "SEND EMAIL SUCCESS"
            else:
                return "SEND EMAIL FAIL"
        else:
            return "CHECK IN FAIL"

def sendEmail(fromAddr,toAddr,subject,content):
    sender = fromAddr
    receivers = [toAddr]  # Receiving emails, can be set as your QQ mailbox or other mailbox. 接收邮件，可设置为您的QQ邮箱或者其他邮箱

    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = Header(fromAddr, 'utf-8')
    message['To'] =  Header(toAddr, 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, mail_port)
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("SEND EMAIL SUCCESS")
        return True
    except smtplib.SMTPException as e:
        print(e)
        print("ERROR: SEND EMAIL FAIL")
        return False
