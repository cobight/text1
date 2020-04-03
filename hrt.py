import urllib.request, urllib.parse, re, json, os, sys, time
from PIL import Image,ImageTk
from io import BytesIO
'''songlist获取后，
    isonly判断是否    独家
    mv的vid判断有无   MV
    pay里的pay_play  >0表示要vip         
    action里的switch 经处理   三个音频版本表示能否播
'''
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
        #print(acs)
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
    path=sys.path[0]
    print(url)
    req = urllib.request.urlopen(url)
    with open(path+"/music/"+mid+".m4a", 'wb') as f:
        f.write(req.read())
    osmsg=path+"/ffmpeg/bin/ffmpeg -i "+path+"/music/"+mid+".m4a "+path+"/music/"+mid+".wav"
    os.system(osmsg)
    os.rename(path+"/music/"+mid+".wav",path+"/music/"+name+".wav")
def getmsguin(text):
    uin=re.search("uin=o(.*?); ",text)
    return uin.groups()[0]
if __name__ =='__main__':
    srch=(heartSrch("我继续"))
    retn=srch.getpage()
    print((retn))

















