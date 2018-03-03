import requests
from bs4 import BeautifulSoup
import json
import re
import itchat
from itchat.content import *
import config
from google import google


conf = config.config
users = {}
commnds =["h","help","帮助","google","g","谷歌","关闭","开启","返回","下一页","上一页",'acg']
helpStr="""回复命令使用相关功能：
[/h,/help,/帮助] 返回本说明
[/google,/g,/谷歌 + 文字] Google搜索
[/下一页,/上一页] 搜索翻页
[/返回] 退出当前功能(搜索)
[/acg] 来一张二次元
[/关闭] 关闭机器人
[/开启] 开启机器人
"""

def doCommnd(name):
    user = getUser(name)
    status = user['status']
    option = user['option']
    #print(name,user)
    if status=='开启':
        setUser(name,{'status':'','option':{}})
        itchat.send('已经开启机器人', toUserName=name)
    elif 'isClose' in option:
        return
    elif status=='关闭':
        setUser(name,{'status':'','option':{'isClose':True}})
        itchat.send('已经关闭机器人', toUserName=name)
    elif status=='h' or status=='help' or status=='帮助':
        setUser(name,{'status':'','option':{}})
        itchat.send(helpStr, toUserName=name)
    elif status=='google' or status=='g' or status=='谷歌':
        if 'msg' in option and option['msg']!='':
            keyword = option['msg']
            page = 1
            result = '第1页\r\n'
            setUser(name,{'status':status,'option':{'keyword':option['msg'],'page':1}})
            if keyword and keyword!='':
                search_results = google.searchByPage(keyword, page)
                for r in search_results:
                    result+=r.name+'\r\n'+r.link+'\r\n'
                itchat.send(result[:-2], toUserName=name)
        else:
            itchat.send('搜索功能，回复文字搜索', toUserName=name)
    elif status=='上一页':
        page = 1
        if 'keyword' in option and 'page' in option:
            if option['page']>1:
                page=option['page']
                page-=1
                result = '第'+str(page)+'页\r\n'
                search_results = google.searchByPage(option['keyword'], page)
                for r in search_results:
                    result+=r.name+'\r\n'+r.link+'\r\n'
                itchat.send(result[:-2], toUserName=name)
                setUser(name,{'status':'google','option':{'keyword':option['keyword'],'page':page}})
            else:
                itchat.send('已经是第'+str(page)+'页了', toUserName=name)
        else:
            itchat.send('当前不是搜索模式', toUserName=name)
    elif status=='下一页':
        if 'keyword' in option and 'page' in option:
            page=option['page']
            page+=1
            result = '第'+str(page)+'页\r\n'
            search_results = google.searchByPage(option['keyword'], page)
            for r in search_results:
                result+=r.name+'\r\n'+r.link+'\r\n'
            itchat.send(result[:-2], toUserName=name)
            setUser(name,{'status':'google','option':{'keyword':option['keyword'],'page':page}})
        else:
            itchat.send('当前不是搜索模式', toUserName=name)
    elif status=='acg':
        users[name]['status']=''
        getAcgImg(name)
    elif status=='返回':
        setUser(name,{'status':'','option':{}})
        itchat.send('已返回聊天模式', toUserName=name)
    elif status=='':
        itchat.send(chat(name,option['msg']), toUserName=name)
        users[name]['option']['msg']=''

def setUser(name,value):
    users[name] = value

def getUser(name):
    return users[name]

def chat(name,msg):
    r = requests.post(conf['api'], data={'key': conf['apiKey'],'info':msg,'userid':name})
    return r.json()['text']

def getAcgImg(name):
    r = requests.get('http://www.theanimegallery.com/gallery/image:random')
    html = BeautifulSoup(r.text,"html.parser")
    url = 'http://www.theanimegallery.com'+html.find(class_='image').img.attrs['src']
    filename = str.split(url,'/')[7:8][0]
    r = requests.get(url,stream=True)
    r.raise_for_status()
    tempImg = open('temp/'+filename,'wb')
    for block in r.iter_content(1024):
        tempImg.write(block)
    tempImg.close()
    itchat.send_image('temp/'+filename,toUserName=name)
def replyPic(name):
    getAcgImg(name)

@itchat.msg_register([TEXT,PICTURE])
def onMsgReceive(obj):
    name = obj.FromUserName
    remarkName = obj.User.RemarkName#备注
    nick = obj.User.NickName#昵称
    msg = obj.Text#内容 
    #忽略名单
    for t in conf["ignore"]:
        if t==remarkName:
            return False
    #check users list
    for t in users:
        if t==name:
            break
    else:
        users[name]={'status':'','option':{}}
        print('新用户',name)
    #接收到图片
    if obj.MsgType==3:
        if 'isClose' in users[name]['option'] and users[name]['option']['isClose']==True:
            return
        else:
            replyPic(name)
        return
    isCommnd = re.match('/.*',msg)
    if re.match('/(.+) ',msg):
        commnd = re.match('/(.+) ',msg)
    else:
        commnd = re.match('/(.+)',msg)
    query = re.match('/.+ (.+)',msg)

    if isCommnd and commnd:
        if commnd.group(1) in commnds:
            #itchat.send('命令存在', toUserName=name)
            status = commnd.group(1)
            if query:
                #itchat.send('参数存在', toUserName=name)
                setUser(name,{'status':commnd.group(1),'option':{'msg':query.group(1)}})
            else:
                setUser(name,{'status':commnd.group(1),'option':users[name]['option']})
        else:
            itchat.send('命令无效', toUserName=name)
            itchat.send(helpStr, toUserName=name)
            return
    elif isCommnd and commnd==None:
        itchat.send('命令无效', toUserName=name)
        itchat.send(helpStr, toUserName=name)
        return
    else:
        users[name]['option']['msg']=msg
        #setUser(name,{'status':users[name]['status'],'option':{'msg':msg}})

    doCommnd(name)
    return

@itchat.msg_register(RECORDING)
def onVioceReceive(obj):
    obj.download('vioce/'+obj.fileName)

itchat.auto_login(hotReload=conf["hotReload"],enableCmdQR=conf["cmdQR"])
itchat.run(conf["verbose"])