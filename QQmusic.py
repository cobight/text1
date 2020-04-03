from tkinter import *
from tkinter import messagebox
import threading
import pygame
import ctypes
import os
import tkinter
from tkinter.ttk import *
import urllib.request
import urllib.parse
import re
import json
import sys
from PIL import Image,ImageTk
from io import BytesIO
import sqlite3
# pyinstaller -F -w -i cobight.ico Coby
class sq3:#D:\Python\sqlite3_space\demo1.db3
    def __init__(self):
        print(sys.path)
        url=sys.path[1]+"/data/tx.db"
        print(url)
        self.url = url
        self.db = sqlite3.connect(url)
        self.cur=self.db.cursor()
        try:
            if self.haveTB_x("mypack"):
                print("mypack")
            else:
                self.createTB()
        except Exception as e:
            print(e)
    def close(self):
        self.cur.close()
        self.db.close()
    def createTB(self):
        sql='create table mypack(QQnumber TEXT,pack TEXT)'
        self.cur.execute(sql)
    def showTBs(self):
        self.cur.execute('select name from sqlite_master where type=\'table\' order by name')
        x=(self.cur.fetchall())
        #print(x)
        return x
    def haveTB_x(self,table=""):
        x = self.showTBs()
        for item in x:
            i = list(item)
            if table in i[0]:
                return True
        return False
    def insPACK(self,QQnumber="",diss=[],song=[]):
        dic=dict()
        dic['diss']=diss
        dic['song']=song
        data=(json.dumps(dic))
        retnb=self.selec(QQnumber)
        if len(retnb)==0:
            sql='insert into myPACK values( ?,? )'
            self.cur.execute(sql,(QQnumber,data))
            self.db.commit()
        else:
            self.dele(QQnumber)
            sql = 'insert into myPACK values( ?,? )'
            self.cur.execute(sql, (QQnumber, data))
            self.db.commit()
        return data
    def showTABLE(self):
        self.cur.execute('SELECT * FROM mypack')
        x=(self.cur.fetchall())
        return x
    def selec(self,Qnub=""):
        self.cur.execute('SELECT * FROM mypack where QQnumber='+Qnub)
        x = (self.cur.fetchall())
        return x
    def dele(self,Qnub=""):
        sql = 'delete from mypack where QQnumber = '+Qnub
        self.cur.execute(sql)
        self.db.commit()
class Mjson:
    def loads(self,input=""):
        self.mjson=json.loads(input)
    def loadd(self,dic={ }):
        self.mjson=dic
    def _re_in(self,item=""):
        msg = re.findall("\[(.*?)\]", item)
        if len(msg) ==1:
            return msg[0]
        else:
            return msg
    def reads(self,select=""):
        dic=self.mjson
        if  select != "":
            lis=select.split('.')
            for i in lis:
                if type(dic) == dict:#循环中，如果不是字典，会崩的
                    if "][" in i:
                        x = list(dic[i[0:i.find("[")]])
                        lis=self._re_in(i)
                        for q in lis:
                            x=x[int(q)]
                        dic=x
                    elif "[" in i and "]" in i:
                        x = list(dic[i[0:i.find("[")]])
                        dic=x[int(self._re_in(i))]
                    else:
                        dic=dic[i]
                else:
                    return None
        return dic
class heartPack:
    def __init__(self,uin=""):
        if uin is None:
            self.uin = ''
        else:
            self.uin = uin
        self.disslists=[]
        self.songlist=[]
        self.nick=""
        self.cookie=None
    def send(self,curl):
        #主要是getcdinfo需要referer，headers还真不能省略
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-language': 'zh-cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': ' https://y.qq.com/portal/profile.html'
            #'Cookie' : self.cookie
        }
        req = urllib.request.Request(url=curl, headers=headers)
        resp = urllib.request.urlopen(req)
        return resp.read().decode('utf-8')
    def sendck(self,curl):
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-language': 'zh-cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': ' https://y.qq.com/portal/profile.html',
            'Cookie' : self.cookie
        }
        req = urllib.request.Request(url=curl, headers=headers)
        resp = urllib.request.urlopen(req)
        return resp.read().decode('utf-8')
    def get_uin_to_disslist(self):
        url="https://c.y.qq.com/rsc/fcgi-bin/fcg_user_created_diss?hostuin="+self.uin+"&sin=0&size=40&r=1583114650987&g_tk=1850906659&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0"
        x=self.send(url)
        jsn = Mjson()
        if "\"diss_cover\":\"?n=1\"" in x:#QQ号存在
            x=x.replace(":\"?n=1\"",":\"https://y.gtimg.cn/mediastyle/global/img/cover_like.png?n=1\"")
            jsn.loads(x)
            if jsn.reads("code") == 0:
                self.disslists = jsn.reads("data.disslist")
                del self.disslists[0]
                self.nick = jsn.reads("data.hostname")
                return True
            return False
        return False
    def get_disis_to_songlist(self):
        self.songlist = []
        if  len(self.disslists) != 0:
            for item in self.disslists:
                jsn = Mjson()
                jsn.loads(self.send(
                    "https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?type=1&json=1&utf8=1&onlysong=0&new_format=1&disstid=" + str(
                        item[
                            'tid']) + "&g_tk=764277635&loginUin="+self.uin+"&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&song_begin=0"))
                lis = (jsn.reads("cdlist[0].songlist"))
                self.songlist.append(lis)
            return True
        return False
                # print(len(lis))
                # print(item['diss_name'],item['tid'],item['song_cnt'],item['listen_num'])
    def getSong_url(self, songmid):
        print(self.cookie)
        if self.cookie == None:
            sendURL = "http://u.y.qq.com/cgi-bin/musicu.fcg?g_tk=1115100142&format=json&data=%7B%22comm%22%3A%7B%22ct%22%3A23%2C%22cv%22%3A0%7D%2C%22url%5Fmid%22%3A%7B%22module%22%3A%22vkey.GetVkeyServer%22%2C%22method%22%3A%22CgiGetVkey%22%2C%22param%22%3A%7B%22guid%22%3A%22649357301%22%2C%22songmid%22%3A%5B%22" + songmid + "%22%5D%2C%22songtype%22%3A%5B0%5D%2C%22uin%22%3A%220%22%2C%22loginflag%22%3A1%2C%22platform%22%3A%2223%22%7D%7D%7D&_=1527829250224"
            mj = Mjson()
            mj.loads(self.send(sendURL))
            msg = mj.reads("url_mid.data.midurlinfo[0].purl")
            return msg
        else:#扫码登陆有cookie
            sendurl="https://u.y.qq.com/cgi-bin/musicu.fcg?data={%22url_mid%22:{%22module%22:%22vkey.GetVkeyServer%22,%22method%22:%22CgiGetVkey%22,%22param%22:{%22guid%22:%226936663186%22,%22songmid%22:[%22" +songmid+ "%22],%22songtype%22:[0],%22uin%22:%22"+self.uin+"%22,%22platform%22:%2223%22}}}"
            mj = Mjson()
            mj.loads(self.sendck(sendurl))
            msg = mj.reads("url_mid.data.midurlinfo[0].purl")
            return msg
    def _issongcanplay(self,acs):
        print(acs)
        lis = list(bin(acs)[2:])
        lis.pop()
        lis.reverse()
        print(lis)
        if len(lis) > 3:
            if (lis[0] == '1') or (lis[1] == '1') or (lis[2] == '1'):
                return True
            else:
                return False
        return False
    def getsongmsg(self,dindex,sindex):
        if len(self.disslists) >0 and len(self.songlist)>0:
            ls = self.songlist[dindex][sindex]
            jsn = Mjson()
            jsn.loadd(ls)
            switch = self._issongcanplay(jsn.reads("action.switch"))
            isonly = jsn.reads("isonly")
            vip1 = jsn.reads("pay.pay_play")
            vip2 = jsn.reads("pay.pay_month")
            msg = [
                1 if isonly != 0 else 0,  # 是否独家
                1 if vip1 > 0 and vip2 > 0 else 0,  # 是否vip
                1 if switch else 0  # 是否有资源
            ]
            if msg[2]==1:
                msg.append(jsn.reads("name"))
                msg.append(jsn.reads("mid"))
                msg.append(jsn.reads("interval"))
                msg.append(jsn.reads("singer"))#list
                msg.append(jsn.reads("album.name"))
                msg.append(jsn.reads("album.mid"))
                msg.append(self.getSong_url(jsn.reads("mid")))
                msg.append(jsn.reads("mv"))
            return msg
        else: return None
class heartSrch:
    def __init__(self,inp=""):
        self.songlist=[]
        self.cookie=None
        self.index=1
        self.url="https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.song&searchid=64089506324002852&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=#page#&n=15&w=#quote#&g_tk=1402852833&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0".replace("#quote#",urllib.parse.quote(inp))
    def send(self,curl):
        req = urllib.request.Request(url=curl)
        resp = urllib.request.urlopen(req)
        return resp.read().decode('utf-8')
    def sendck(self,curl):
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-language': 'zh-cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': ' https://y.qq.com/portal/profile.html',
            'Cookie' : self.cookie
        }
        req = urllib.request.Request(url=curl, headers=headers)
        resp = urllib.request.urlopen(req)
        return resp.read().decode('utf-8')
    def getpage(self):
        retn=self.send(self.url.replace("#page#",str(self.index)))
        jsn=Mjson()
        jsn.loads(retn)
        try:
            retn=jsn.reads("data.song.list")
            self.songlist.extend(retn)
            self.index+=1
            return retn
        except Exception as e:
            return None
    def getSong_url(self, songmid):
        print(self.cookie)
        if self.cookie == None:
            sendURL = "http://u.y.qq.com/cgi-bin/musicu.fcg?g_tk=1115100142&format=json&data=%7B%22comm%22%3A%7B%22ct%22%3A23%2C%22cv%22%3A0%7D%2C%22url%5Fmid%22%3A%7B%22module%22%3A%22vkey.GetVkeyServer%22%2C%22method%22%3A%22CgiGetVkey%22%2C%22param%22%3A%7B%22guid%22%3A%22649357301%22%2C%22songmid%22%3A%5B%22" + songmid + "%22%5D%2C%22songtype%22%3A%5B0%5D%2C%22uin%22%3A%220%22%2C%22loginflag%22%3A1%2C%22platform%22%3A%2223%22%7D%7D%7D&_=1527829250224"
            mj = Mjson()
            mj.loads(self.send(sendURL))
            msg = mj.reads("url_mid.data.midurlinfo[0].purl")
            return msg
        else:#扫码登陆有cookie
            sendurl="https://u.y.qq.com/cgi-bin/musicu.fcg?data={%22url_mid%22:{%22module%22:%22vkey.GetVkeyServer%22,%22method%22:%22CgiGetVkey%22,%22param%22:{%22guid%22:%226936663186%22,%22songmid%22:[%22" +songmid+ "%22],%22songtype%22:[0],%22uin%22:%22"+self.uin+"%22,%22platform%22:%2223%22}}}"
            mj = Mjson()
            mj.loads(self.sendck(sendurl))
            msg = mj.reads("url_mid.data.midurlinfo[0].purl")
            return msg
    def _issongcanplay(self,acs):
        lis = list(bin(acs)[2:])
        lis.pop()
        lis.reverse()
        if len(lis) > 3:
            if (lis[0] == '1') or (lis[1] == '1') or (lis[2] == '1'):
                return True
            else:
                return False
        return False
    def getsongmsg(self,index):
            ls = self.songlist[index]
            jsn = Mjson()
            jsn.loadd(ls)
            switch = self._issongcanplay(jsn.reads("action.switch"))
            isonly = jsn.reads("isonly")
            vip1 = jsn.reads("pay.pay_play")
            vip2 = jsn.reads("pay.pay_month")
            msg = [
                1 if isonly != 0 else 0,  # 是否独家
                1 if vip1 > 0 and vip2 > 0 else 0,  # 是否vip
                1 if switch else 0  # 是否有资源
            ]
            if msg[2]==1:
                msg.append(jsn.reads("name"))
                msg.append(jsn.reads("mid"))
                msg.append(jsn.reads("interval"))
                msg.append(jsn.reads("singer"))#list
                msg.append(jsn.reads("album.name"))
                msg.append(jsn.reads("album.mid"))
                msg.append(self.getSong_url(jsn.reads("mid")))
                msg.append(jsn.reads("mv"))
            return msg
def getpic1(url):
    req = urllib.request.urlopen(url)
    byioobj=BytesIO()
    byioobj.write(req.read())
    img=Image.open(byioobj)
    img = ImageTk.PhotoImage(img)
    return img
def getpic2(url):
    req = urllib.request.urlopen(url)
    byioobj=BytesIO()
    byioobj.write(req.read())
    img=Image.open(byioobj)
    img=img.resize((50,50))
    img = ImageTk.PhotoImage(img)
    return img
def m4a_to_mp3(url,name,mid):
    path=sys.path[1]
    req = urllib.request.urlopen(url)
    with open(path+"/music/"+mid+".m4a", 'wb') as f:
        f.write(req.read())
    osmsg=path+"/ffmpeg/bin/ffmpeg -i "+path+"/music/"+mid+".m4a "+path+"/music/"+mid+".wav"
    os.system(osmsg)
    os.rename(path+"/music/"+mid+".wav",path+"/music/"+name+".wav")
def getmsguin(text):
    uin=re.search("uin=o(.*?); ",text)
    return uin.groups()[0]
class Application_ui(Frame):
    # 这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Cobight')
        self.master.attributes('-alpha', 0.95)
        self.master.maxsize(900,0)
        self.master.minsize(800,0)
        self.master.iconbitmap('cobight.ico')
        self.master.geometry('800x670+400+200')
        self.top = self.winfo_toplevel()
        self.master.update()
        self.style_init()

        self.createWidgets()
        self.createFly()

    def style_init(self):
        self.style = Style()
        self.style.configure("Bold.TButton", font=('华文行楷', 20))
        self.style.configure("B1.TFrame",background='#334353')
    def createWidgets(self):

        self.TabStrip1 = Notebook(self.top)
        print(self.TabStrip1.winfo_id())
        self.TabStrip1.place(relx=0.04, rely=0.03, relwidth=0.92, relheight=0.85)

        self.TB1()
        self.TB2()
    def TB1(self):
        self.TabStrip1__Tab1 = Frame(self.TabStrip1,style='B1.TFrame')
        self.cv = Canvas(self.TabStrip1__Tab1, height=100, width=100, background='pink')
        self.cv.place(relx=0.02, rely=0.06)
        self.inpuin = StringVar()
        self.inp = Entry(self.TabStrip1__Tab1, width=15, font=('华文行楷', 20), textvariable=self.inpuin)
        self.inp.place(relx=0.2, rely=0.08)
        self.welcome = Label(self.TabStrip1__Tab1, width=15, font=('华文行楷', 18))
        self.welcome.place(relx=0.2, rely=0.16)
        self.dislv = Canvas(self.TabStrip1__Tab1, height=350, width=200, background="pink")
        self.dislv.place(relx=0.02, rely=0.3)
        self.songlv = Treeview(self.TabStrip1__Tab1, height=16, show="headings", columns=['0', '1', '2'])
        self.songlv.column('0', width=210)
        self.songlv.column('1', width=150, anchor='center')
        self.songlv.column('2', width=80, anchor='center')
        self.songlv.heading('0', text='歌名')
        self.songlv.heading('1', text='歌手')
        self.songlv.heading('2', text='时长')
        self.songlv.place(relx=0.35, rely=0.3)
        self.TabStrip1.add(self.TabStrip1__Tab1, text='我的音乐')
    def TB2(self):
        self.TabStrip1__Tab2 = Frame(self.TabStrip1)

        self.inpsrch=StringVar()
        self.srchinp=Entry(self.TabStrip1__Tab2,width=20, font=('华文行楷', 20), textvariable=self.inpsrch)
        self.srchinp.place(relx=0.3, rely=0.09)

        self.srchcv=Canvas(self.TabStrip1__Tab2,height=1000,width=650,background='pink')
        self.srchcv.place(relx=0.07,rely=0.3)

        self.TabStrip1.add(self.TabStrip1__Tab2, text='寻找音乐')
    def createFly(self):
        self.Fly=Frame(self.top,style='B1.TFrame')
        self.Fly.place(relx=0, rely=0.03, relwidth=1, relheight=0.85)
class Application(Application_ui):
    # 这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        self.media=None
        self.headpic=None
        self.index_diss=-1
        self.mediakey=True
        self.srchkey=True
        self.inp.bind("<Return>",self.Loginn)
        self.songlv.bind("<Double-Button-1>", self._song_onclick)
        self.srchinp.bind("<Return>",self._search)

        self.hrt=None
        self.cookie=None
        self.s_hrt=None
        t=threading.Thread(target=self.readsql3)
        t.setDaemon(True)
        t.start()
        self.qrshow()
    def _search(self,e):
        self._srchwinlist=[]
        self._srchLabellist=[]
        self._srchwinnum=0
        print("输入的是"+self.inpsrch.get())
        self.s_hrt=heartSrch(self.inpsrch.get())
        self.srchcv.delete(ALL)
        t=threading.Thread(target=self.srchcv_insert)
        t.setDaemon(True)
        self.srchkey=False
        t.start()
    def srchcv_insert(self):
        retnb=self.s_hrt.getpage()
        ind=self._srchwinnum
        self.update()
        for i in range(ind,ind+len(retnb)):
            frame = Frame(self.srchcv,width=40)

            leftLabel = Label(frame,width=20,font=('隶书', 16), text=self.s_hrt.songlist[i]['name'])
            leftLabel.bind("<MouseWheel>",self.srchcv_mousewheel)
            leftLabel.bind("<Double-Button-1>",self.srchcv_onclick)
            leftLabel.pack(side=tkinter.LEFT)
            sgrmsg=""
            for item in self.s_hrt.songlist[i]['singer']:
                sgrmsg+=item['name']+"/"
            fra=Frame(frame,width=20)
            midLabel=Label(fra,width=15,font=('隶书', 15),text=sgrmsg[0:len(sgrmsg)-1])
            midLabel.bind("<MouseWheel>",self.srchcv_mousewheel)
            midLabel.bind("<Double-Button-1>",self.srchcv_onclick)
            midLabel.pack(side=tkinter.LEFT)
            rightLabel = Label(fra, width=5, font=('隶书', 15), text=str(int(self.s_hrt.songlist[i]['interval']/60))+":"+str(self.s_hrt.songlist[i]['interval']%60))
            rightLabel.bind("<MouseWheel>",self.srchcv_mousewheel)
            rightLabel.bind("<Double-Button-1>",self.srchcv_onclick)
            rightLabel.pack(side=tkinter.RIGHT)
            fra.pack(side=tkinter.RIGHT)
            self._srchwinlist.append(frame)
            self._srchLabellist.append([leftLabel,midLabel,rightLabel])
            if len(self._srchwinlist)==1:
                self.srchcv.create_window((300, 15), window=frame)
            else:
                self.srchcv.create_window((300,self._srchwinlist[i-1].winfo_y()+36 ), window=frame)
                self.update()
        self._srchwinnum+=len(retnb)
        self.srchkey = True
    def srchcv_onclick(self,e):
        for i,item in enumerate(self._srchLabellist):
            if e.widget in item:
                retn = self.s_hrt.getsongmsg(i)
                #print(retn)
                if len(retn) > 3 and retn[9] != "":
                    self.update()
                    for root, dirs, files in os.walk(sys.path[1] + "/music"):  # path 为根目录

                        if retn[3] + ".mp3" in files:  # 能直接播放
                            pygame.mixer.music.load(sys.path[1] + '/music/' + retn[3] + '.mp3')
                            pygame.mixer.music.play()
                            self.mediakey = True
                        else:
                            try:
                                m4a_to_mp3(retn[9], retn[3], retn[4])  # 耗时操作，（下载+m4a转mp3+文件改名）
                                pygame.mixer.music.load(sys.path[1] + '/music/' + retn[3] + '.mp3')
                                pygame.mixer.music.play()
                            except:
                                messagebox.askquestion(title='？？？网速呢？？？', message='兄弟，插网线了么？连wifi了么？')
                                pass
                            self.mediakey = True
                elif len(retn) > 3 and retn[9] == "":
                    messagebox.askquestion(title='？？？资源呢？？？', message='有资源，但没法播放，试试扫码登陆吧~')
                    self.mediakey = True
                else:
                    messagebox.askquestion(title='？？？没资源？？？', message='这个真没资源，估计下架了')
                    self.mediakey = True
    def srchcv_mousewheel(self,e):
        if self._srchwinlist[0].winfo_y() >0 and e.delta > 0:
            print("拒绝顶部下拉")
        elif self._srchwinlist[len(self._srchwinlist) - 1].winfo_y()+20 <350 and e.delta < 0:
            if self.srchkey:
                self.srchkey=False
                t=threading.Thread(target=self.srchcv_insert)
                t.setDaemon(True)
                t.start()
                #self.srchcv_insert()
            #print("拒绝底部上拉")
        else:
            xx=self.srchcv.find_all()
            for x in xx:
                self.srchcv.move(x,0,5 if e.delta>0 else -5)
    def qrshow(self):
        try:
            t=threading.Thread(target=qrshow,args=((self.TabStrip1__Tab2_hwnd,)))
            t.setDaemon(True)
            t.start()
        except Exception as e:
            print(e)
    def readsql3(self):
        sq = sq3()
        x=sq.showTABLE()
        sq.close()
        if len(x) ==0:
            print("database have not msg")
        else:
            msg = list(x[len(x)-1])[1]
            num = list(x[len(x)-1])[0]
            self.hrt=heartPack(num)
            jsn=Mjson()
            jsn.loads(msg)
            self.hrt.disslists=jsn.reads("diss")
            self.hrt.songlist=jsn.reads("song")
            self.freashdis()
            #self._show_in_dislv()
    def Loginn(self,e):
        #print(self.inpuin.get())
        self.hrt=heartPack(self.inpuin.get())
        self.jpLoginn()
    def jpLoginn(self):
        msg = self.hrt.get_uin_to_disslist()
        if msg:
            print(self.hrt.nick)
            self.welcome['text'] = '你好：' + self.hrt.nick
            self.hrt.get_disis_to_songlist()
            print(self.hrt.uin)
            sq = sq3()
            sq.insPACK(self.hrt.uin, self.hrt.disslists, self.hrt.songlist)
            sq.close()
            self.freashdis()
    def freashdis(self):
        s = threading.Thread(target=self._showheadpic)
        s.setDaemon(True)
        s.start()
        dis = threading.Thread(target=self._show_in_dislv)
        dis.setDaemon(True)
        dis.start()
    def _showheadpic(self):
        self.headpic=getpic1("http://q1.qlogo.cn/g?b=qq&nk="+self.hrt.uin+"&s=100")
        self.cv.delete(ALL)
        self.cv.create_image(1,1, anchor='nw',image=self.headpic)
        #self.headpic=None#会销毁图片的，但是image控件应该还没有销毁
    def _show_in_dislv(self):
        try:
            self.dislv.delete(ALL)
            x = self.songlv.get_children()
            for item in x:
                self.songlv.delete(item)
            self.pic_dissimg=[]
            self.picwinlist=[]
            for i,item in enumerate(self.hrt.disslists):
                #print(item)
                self.pic_dissimg.append(getpic2(item['diss_cover']))
                self.picwinlist.append(Label(self.dislv,image=self.pic_dissimg[i]))
                self.picwinlist[i]['text']="  "+item['diss_name']#强行美观，嘻嘻
                self.picwinlist[i]['compound']="left"
                self.picwinlist[i]['width']=20
                self.picwinlist[i].bind("<Double-Button-1>",self._show_in_songlv)
                self.picwinlist[i].bind("<MouseWheel>",self._dislv_mousewheel)
                if i ==0:
                    self.dislv.create_window((100,25+2),window=self.picwinlist[i])
                else:
                    self.dislv.create_window((100, 25+2+self.picwinlist[i-1].winfo_y()+50), window=self.picwinlist[i])
                self.update()
        except Exception as e:
            print(e)
            #print(self.picwinlist[i].winfo_y())
    def _dislv_mousewheel(self,e):
        self.update()
        #print(e,e.delta)
        xx = self.dislv.find_all()
        if len(xx) >7:
            if self.picwinlist[0].winfo_y()==0 and e.delta>0:
                print("拒绝顶部下拉")
            elif self.picwinlist[len(self.picwinlist)-1].winfo_y()==300 and e.delta<0:
                print("拒绝底部上拉")
            else:
                for x in xx:
                    self.dislv.move(x, 0, 10 if e.delta > 0 else -10)

        #print(self.picwinlist[0].winfo_y(),self.picwinlist[len(self.picwinlist)-1].winfo_y())
    def _show_in_songlv(self,e):
        self.update()
        for i,item in enumerate(self.picwinlist):
            if item == e.widget:
                self._songlv_clean()
                self.index_diss=i
                for si in self.hrt.songlist[i]:
                    msgsgr=""
                    for sgr in si['singer']:
                        msgsgr+=sgr['name']+"/"

                    self.songlv.insert("","end",
                                       values=[(si['name']),msgsgr[:len(msgsgr)-1],str(int(si['interval']/60))+":"+str(si['interval']%60)])


        #print(e.widget)
    def _songlv_clean(self):
        x=self.songlv.get_children()
        for i in x:
            self.songlv.delete(i)
    def _song_onclick(self,e):
        print(e)
        for i,item in enumerate(self.songlv.get_children()):
            if item==self.songlv.focus():
                if self.mediakey:
                    #t=threading.Thread(target=self._music_play,args=(self.index_diss,i))
                    #t.setDaemon(True)
                    self.mediakey=False
                    #t.start()
                    self.music_play(self.index_diss,i)
                    break
    def music_play(self,d,s):
        retn=self.hrt.getsongmsg(d,s)
        print(retn)
        if len(retn)>3 and retn[9] !="":
            self.update()
            path=sys.path[1]+'\\music\\'+retn[3]+'.wav'
            print(path)
            for root, dirs, files in os.walk(sys.path[1]+"\\music"):  # path 为根目录

                if retn[3]+".wav" in files:#能直接播放
                    playmedia(path)
                    self.mediakey = True
                else:
                    m4a_to_mp3(retn[9],retn[3],retn[4])#耗时操作，（下载+m4a转mp3+文件改名）
                    playmedia(path)
                    self.mediakey = True



        elif len(retn)>3 and retn[9]=="":
            messagebox.askquestion(title='？？？资源呢？？？', message='有资源，但没法播放，试试扫码登陆吧~')
            self.mediakey=True
        else:
            messagebox.askquestion(title='？？？没资源？？？', message='这个真没资源，估计下架了')
            self.mediakey = True
def qrshow(hwnd1,hwnd2):
    try:
        dll = ctypes.WinDLL("./QRshow.dll")
        dll.e_shadow(hwnd1)
        x = ctypes.string_at(dll.e_openwindow(hwnd2))
        keycook = x.decode('utf-8')
        uin=heartPack.getmsguin(keycook)

        ap.hrt=heartPack.heartPack(uin)
        ap.hrt.cookie = keycook
        ap.jpLoginn()
        #print(keycook)
    except Exception as e:
        print(e)
def playmedia(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
if __name__ == "__main__":
    try:
        pygame.mixer.init()
        top = Tk()
        ap=Application(top)
        ap.mainloop()
    except Exception as e:
        print(e)
        pass
#cd F:\python_space\bs_project\Coby

#pyinstaller -F -i cobight.ico -w QQmusic.py -p hrt.py -p sql3.py --hidden-import Coby.hrt --hidden-import Coby.sql3