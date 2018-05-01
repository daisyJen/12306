# -*- coding:utf-8 -*-
import urllib2, urllib
import ssl
import cookielib
from user import user, pwd
from json import loads
from codes import checkPicture
from station import station_names
from time import sleep
import re
import utils
import sys
reload(sys)
sys.setdefaultencoding('utf8')

c = cookielib.LWPCookieJar()#生成一个存储cookie的对象
cookie = urllib2.HTTPCookieProcessor(c)
opener = urllib2.build_opener(cookie)#把这个存储器绑定到opener对象当中
urllib2.install_opener(opener)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
}

#不进行证书验证
ssl._create_default_https_context = ssl._create_unverified_context

ticketType ={'成人票':'ADULT', '学生票':'STUDENT'}
seatType={'软卧':23, '商务座':25 , '特等座':25,   '硬卧':26,  '软座':27, '硬座':28, '无座':29, '一等座':30, '二等座':31}
def getStationCode(name):
    # stationArray[1]代表地名，如上海，stationArray[2]代表对应的编码，如SHH
    stationDict = {}
    stationArray = station_names.split('@')[1:]
    for station in stationArray: #bjb|北京北|VAP|beijingbei|bjb|0
        stations = station.split('|')
        stationDict[stations[1]] = stations[2]
    return stationDict[name]


def login():

# 1、获取验证码
    print '获取验证码..........'
    req = urllib2.Request('https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.22285932578004175')
    req.headers = headers
    imgCode = opener.open(req).read()
    with open('code.png', 'wb') as fn:
        fn.write(imgCode)

#2、验证校验码
    print '验证校验码..........'
    req = urllib2.Request('https://kyfw.12306.cn/passport/captcha/captcha-check')
    req.headers = headers
    #code = raw_input('请输入验证码：')
    code = checkPicture('code.png') #自动识别12306的验证码
    data = {
        'answer': code,
        'login_site': 'E',
        'rand': 'sjrand'
    }
    data = urllib.urlencode(data)
    html = opener.open(req, data).read()
    html = loads(html)
    print html['result_message']
    if html['result_code'] != "4":
        return
#3、登录
    print '登录..........'
    req = urllib2.Request('https://kyfw.12306.cn/passport/web/login')
    req.headers = headers
    data = {
        'username': user,
        'password': pwd,
        'appid': 'otn'
    }
    data = urllib.urlencode(data)
    html = opener.open(req, data).read()
    result = loads(html)
    if result['result_code'] != 0:
        print('登录失败，正在重新登录......')
        sleep(5)
        login()
    else:
        print result['result_message']
    req = urllib2.Request('https://kyfw.12306.cn/passport/web/auth/uamtk')
    req.headers = headers
    data = {
        'appid':'otn'
    }
    data = urllib.urlencode(data)
    html = opener.open(req, data).read()
    html = loads(html)
    print html['result_message']
    if html['result_code'] != 0:
        return

    req = urllib2.Request('https://kyfw.12306.cn/otn/uamauthclient')
    req.headers = headers
    data = {
        'tk':html['newapptk']
    }
    data = urllib.urlencode(data)
    html = opener.open(req, data).read()

    req = urllib2.Request('https://kyfw.12306.cn/otn/index/initMy12306')
    req.headers = headers
    html = opener.open(req).read()


#4、查询车票
def checkTicket(train_date, from_station, to_station, purpose_codes,train, seat):
    print '查询车票..........'
    req = urllib2.Request('https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=%s' %(train_date, getStationCode(from_station), getStationCode(to_station), purpose_codes))
    req.headers = headers
    html = opener.open(req).read()
    html = loads(html)
    if(html['status'] == 'false'):
        print '车票查询失败'
    for result in  html['data']['result']:
        info = result.split('|')
        # 3：车次，8:起始时间，9：到站时间，10:历时时间，
        if info[3] == train and (info[seat] == u'有' or int(info[seat]) > 0):
            buyTickets(train_date, from_station, to_station, purpose_codes,info[0],info[3],info[15],info[2],info[12] )
        else:
            continue


#5、下单
def buyTickets(train_date, from_station, to_station, purpose_codes,secretStr, stationTrainCode, trainLocation, trainNo,leftTicketStr):
    print '下单..........'
    req = urllib2.Request('https://kyfw.12306.cn/otn/login/checkUser')
    req.headers = headers
    data = {
        '_json_att': ''
    }
    data = urllib.urlencode(data)
    html = opener.open(req, data).read()
    print '100001:checkUser: %s' %html

    req = urllib2.Request('https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest')
    req.headers = headers
    print train_date,purpose_codes,from_station,to_station,secretStr
    data = {
        'back_train_date':train_date,
        'purpose_codes':purpose_codes,
        'query_from_station_name':from_station,
        'query_to_station_name':to_station,
        'secretStr':urllib.unquote(secretStr),
        'tour_flag':'dc',
        'train_date':train_date,
        'undefined':''
    }
    data = urllib.urlencode(data)
    html = opener.open(req, data).read()
    print '100002:submitOrderRequest: %s' % html

    req = urllib2.Request('https://kyfw.12306.cn/otn/confirmPassenger/initDc')
    req.headers = headers
    data = {
        '_json_att':'',
    }
    data = urllib.urlencode(data)
    html = opener.open(req, data).read()
    globalRepeatSubmitToken = re.findall(r"globalRepeatSubmitToken = '(.*?)'",html)[0]
    key_check_isChange = re.findall(r"'key_check_isChange':'(.*?)'",html)[0]
    print '100003:globalRepeatSubmitToken: %s, key_check_isChange: %s' % (globalRepeatSubmitToken, key_check_isChange)


    req = urllib2.Request('https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs')
    req.headers = headers
    data = {
        '_json_att':'',
        'REPEAT_SUBMIT_TOKEN':globalRepeatSubmitToken
    }
    data = urllib.urlencode(data)
    html = opener.open(req, data).read()
    print '100004:getPassengerDTOs: %s' % html

    req = urllib2.Request('https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo')
    req.headers = headers
    data = {
        '_json_att': '',
        'bed_level_order_num':'000000000000000000000000000000',
        'cancel_flag':2,
        'oldPassengerStr':'任琴,1,511322199009152585,1_', #任琴,1,511322199009152585,1_冯代清,1,512924196402122166,1_
        'passengerTicketStr':'1,0,1,任琴,1,511322199009152585,,N',#3,0,1,任琴,1,511322199009152585,,N_3,0,1,冯代清,1,512924196402122166,,N
        'randCode':'',
        'REPEAT_SUBMIT_TOKEN':globalRepeatSubmitToken,
        'tour_flag':'dc',
        'whatsSelect':1

    }
    data = urllib.urlencode(data)
    html = opener.open(req, data).read()
    print '100005:checkOrderInfo: %s' %html

    req = urllib2.Request('https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount')
    req.headers = headers
    data = {
        '_json_att': '',
        'fromStationTelecode': getStationCode(from_station),
        'leftTicket': leftTicketStr,
        'purpose_codes': 00,#成人票
        'REPEAT_SUBMIT_TOKEN':globalRepeatSubmitToken,
        'seatType': 1,
        'stationTrainCode': stationTrainCode,
        'toStationTelecode':getStationCode(to_station),
        'train_date':utils.strToGMT(train_date),
        'train_location':trainLocation,
        'train_no':trainNo
    }
    print 100006, getStationCode(from_station),globalRepeatSubmitToken,stationTrainCode,getStationCode(to_station),utils.strToGMT(train_date),trainLocation,trainNo
    data = urllib.urlencode(data)
    html = opener.open(req, data).read()
    print '100006:getQueueCount: %s' % html


    req = urllib2.Request('https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue')
    req.headers = headers
    # print key_check_isChange,leftTicketStr,globalRepeatSubmitToken,trainLocation
    data = {
        '_json_att': '',
        'choose_seats':'',
        'dwAll':'N',
        'key_check_isChange':key_check_isChange,
        'leftTicketStr':leftTicketStr,
        'oldPassengerStr':'任琴,1,511322199009152585,1_',
        'passengerTicketStr':'3,0,1,任琴,1,511322199009152585,,N',
        'purpose_codes':'00',
        'randCode':'',
        'REPEAT_SUBMIT_TOKEN':globalRepeatSubmitToken,
        'roomType':'00',
        'seatDetailType':'000',
        'train_location':trainLocation,
        'whatsSelect':'1'
    }
    data = urllib.urlencode(data)
    html = opener.open(req, data).read()
    print '100007:confirmSingleForQueue: %s' %html


if __name__ == "__main__":
    train_date = raw_input('请输入出发日期，例2018-05-09:')
    from_station = raw_input('请输入出发地，例上海:')
    to_station = raw_input('请输入目的地，例北京:')
    purpose_codes = ticketType[raw_input('请输入车票类型，例成人票、学生票:')]
    train = raw_input('请输入车次，例G102:')
    seat = seatType[raw_input('请输入座位类型，例商务座、一等座、二等座、硬卧、硬座等:')]
    login()
    checkTicket(train_date, from_station, to_station, purpose_codes,train,seat)