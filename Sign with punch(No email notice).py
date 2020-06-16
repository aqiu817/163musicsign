import json
import requests
def main_handler(event, context):
    base_url = "https://music.cloudsvip.club"
    login_url =     base_url + "/api.php?do=login"      # 登录URL
    daka_url =      base_url + "/api.php?do=daka"       # 打卡URL
    sign_url =      base_url + "/api.php?do=sign"       # 移动端签到URL
    signpc_url =    base_url + "/api.php?do=signpc"     # PC端签到URL


    # 浏览器访问后复制结果替换{}的内容
    #或者自行使用md5加密工具替换pwd中内容
    # https://music.cloudsvip.club/api.php?do=getSign&uin=账号&pwd=密码
    data= {'uin': '账号','pwd': 'e10adc3949ba59abbe56e057f20f883e'}
    req = requests.post(login_url, data = data ) 


    cookies = req.cookies 
    # 登录判断
    reqJsonObj = json.loads(req.text)
    
    if reqJsonObj['code'] == 200:
        nickName = reqJsonObj['profile']['nickname']
    elif reqJsonObj['code'] == 400:
        return '登录异常，请检查账号密码格式是否正确！' + '，返回码: ' + str(reqJsonObj['code'])
    else :
        return str(reqJsonObj['message']) + '，返回码: ' + str(reqJsonObj['code'])
    result = ''
    # 移动端签到
    sign = requests.post(sign_url, cookies = cookies)
    signJsonObj = json.loads(sign.text)
    if signJsonObj['code'] == 200:
        result += '移动端签到成功: ' + '经验+' +  str(signJsonObj['point'])
    else:
        result += '移动端签到失败: ' + str(signJsonObj['msg'])
    result += '    '
    # PC端签到
    signpc = requests.post(signpc_url, cookies = cookies)
    signPcJsonObj = json.loads(signpc.text)
    if signPcJsonObj['code'] == 200:
        result += 'PC端签到成功: ' + '经验+' +  str(signPcJsonObj['point'])
    else:
        result += 'PC端签到失败: ' + str(signPcJsonObj['msg'])
    result += '         '
    # 打卡
    daka = requests.post(daka_url, cookies = cookies)
    dakaJsonObj = json.loads(daka.text)
    if dakaJsonObj['code'] == 200:
        result += '打卡成功: ' + str(dakaJsonObj['count']) + '首'
    else:
        result += '打卡失败: 未知错误'
        
    return result
