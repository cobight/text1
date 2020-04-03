from tkinter import *
from tkinter import messagebox
import threading,ctypes,os,tkinter
from tkinter.ttk import *
import Coby.hrt
import Coby.sql3
import wave,pyaudio
import numpy as np
import warnings
import win32gui
from win32api import GetSystemMetrics
warnings.simplefilter("ignore", DeprecationWarning)#防止报警告
# pyinstaller -F -w -i cobight.ico Coby

class Application_ui(Frame):
    # 这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)

        #self.master.overrideredirect(True)
        self.master.title('Cobight')
        self.master.attributes('-alpha', 0.90)
        #self.master.attributes('-topmost',True)
        self.master.maxsize(1300,0)
        self.master.minsize(800,0)
        self.master.iconbitmap('cobight.ico')
        self.master.geometry('910x670+400+200')
        self.top = self.winfo_toplevel()
        self.top_Frame=Frame(self.top)
        self.top_Frame.place(relx=0,rely=0,relheight=1,relwidth=1)
        self.master.update()
        self.style_init()
        self.create_winclose()
        self.createWidgets()
        self.createFly()
    def create_winclose(self):
        self.frame_close=Label(self.top_Frame ,text='X')
        self.frame_close.place(relx=0.97,rely=0.01,relwidth=0.03)
    def style_init(self):
        self.style = Style()
        self.style.configure("B1.TFrame",background='#334353')
    def createWidgets(self):

        self.TabStrip1 = Notebook(self.top_Frame)
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
        global Flycanvas
        self.Fly=Frame(self.top_Frame)
        Flycanvas=Canvas(self.Fly,background='pink')
        Flycanvas.place(relx=0,rely=0,height=GetSystemMetrics(1),width=GetSystemMetrics(0))
        self.Fly.place(relx=0.005, rely=0.03, relwidth=1, relheight=0.85)
        Flycanvas.update()
        for x in range(258):
            Flycanvas.create_rectangle(7 * x+2, 0, 7 * x + 2, 0)
class Application(Application_ui):
    # 这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)

        self.headpic=None
        self.index_diss=-1
        self.event_obj=threading.Event()
        self.srchkey=True
        self.movekey=False
        self.top_Frame.bind("<ButtonPress-1>",self.move_bdown)
        self.top_Frame.bind("<Motion>",self.move_Motion)
        self.top_Frame.bind("<ButtonRelease-1>",self.move_bup)
        self.inp.bind("<Return>",self.Loginn)
        self.songlv.bind("<Double-Button-1>", self._song_onclick)
        self.srchinp.bind("<Return>",self._search)
        self.frame_close.bind("<Button-1>",lambda event:self.winfo_toplevel().destroy())
        self.hrt=None
        self.cookie=None
        self.s_hrt=None
        self.xy=0
        #self.freetk()
        t=threading.Thread(target=self.readsql3)
        t.setDaemon(True)
        t.start()
        self.update()
        zmh(Flycanvas.winfo_id())
        self.qrshow()
    def move_bdown(self,e):
        self.x=e.x
        self.y=e.y
        self.movekey=True
        self.xy=0
        print(1)
    def move_Motion(self,e):
        if self.movekey and self.xy%2==0:
            print(e.x,e.y)
            deltax = e.x - self.x
            deltay = e.y - self.y
            x = self.master.winfo_x() + deltax
            y = self.master.winfo_y() + deltay
            self.master.geometry("+%s+%s" % (x, y))
        self.xy+=1
    def move_bup(self,e):
        self.x=None
        self.y=None
        self.movekey=False
        print(2)
    def _search(self,e):
        self._srchwinlist=[]
        self._srchLabellist=[]
        self._srchwinnum=0
        print("输入的是"+self.inpsrch.get())
        self.s_hrt=Coby.hrt.heartSrch(self.inpsrch.get())
        self.srchcv.delete(ALL)
        t=threading.Thread(target=self.srchcv_insert)
        t.setDaemon(True)
        self.srchkey=False
        t.start()
    def srchcv_insert(self):
        retnb=self.s_hrt.getpage()
        ind=self._srchwinnum
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
            rightLabel=Label(fra, width=5, font=('隶书', 15),
                  text=str(int(self.s_hrt.songlist[i]['interval']/60))+":"+str(self.s_hrt.songlist[i]['interval']%60))
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
        self._srchwinnum+=len(retnb)
        self.srchkey = True
    def srchcv_onclick(self,e):
        for i,item in enumerate(self._srchLabellist):
            if e.widget in item:
                retn = self.s_hrt.getsongmsg(i)
                print(retn)
                if len(retn) > 3 and retn[9] != "":
                    self.update()
                    path=sys.path[0]+'/music/' + retn[4] + '.wav'
                    for root, dirs, files in os.walk( sys.path[0]+"/music"):  # path 为根目录

                        if retn[4] + ".wav" in files:  # 能直接播放
                            print('have')
                            self.event_obj.set()
                            self.update()
                            self.event_obj = threading.Event()
                            self.event_obj.clear()
                            t1 = threading.Thread(target=Media, args=(self.event_obj, path))
                            t1.setDaemon(True)
                            t1.start()
                        else:
                            try:
                                Coby.hrt.m4a_to_mp3(retn[9], retn[4], retn[4])  # 耗时操作，（下载+m4a转mp3+文件改名）
                                self.event_obj.set()
                                self.update()
                                self.event_obj = threading.Event()
                                self.event_obj.clear()
                                t1 = threading.Thread(target=Media, args=(self.event_obj, path))
                                t1.setDaemon(True)
                                t1.start()
                            except:
                                messagebox.askquestion(title='？？？网速呢？？？', message='兄弟，插网线了么？连wifi了么？')

                elif len(retn) > 3 and retn[9] == "":
                    messagebox.askquestion(title='？？？资源呢？？？', message='有资源，但没法播放，试试扫码登陆吧~')
                else:
                    messagebox.askquestion(title='？？？没资源？？？', message='这个真没资源，估计下架了')

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
            t=threading.Thread(target=qrshow,args=(self.Fly.winfo_id(),self.TabStrip1__Tab2.winfo_id(),self.winfo_toplevel().winfo_id()))
            t.setDaemon(True)
            t.start()
        except Exception as e:
            print(e)
    def readsql3(self):
        sq = Coby.sql3.sq3()
        x=sq.showTABLE()
        sq.close()
        if len(x) ==0:
            print("database have not msg")
        else:
            msg = list(x[len(x)-1])[1]
            num = list(x[len(x)-1])[0]
            self.hrt=Coby.hrt.heartPack(num)
            jsn=Coby.hrt.Mjson()
            jsn.loads(msg)
            self.hrt.disslists=jsn.reads("diss")
            self.hrt.songlist=jsn.reads("song")
            self.freashdis()
            #self._show_in_dislv()
    def Loginn(self,e):
        #print(self.inpuin.get())
        self.hrt=Coby.hrt.heartPack(self.inpuin.get())
        self.jpLoginn()
    def jpLoginn(self):
        msg = self.hrt.get_uin_to_disslist()
        if msg:
            print(self.hrt.nick)
            self.welcome['text'] = '你好：' + self.hrt.nick
            self.hrt.get_disis_to_songlist()
            print(self.hrt.uin)
            sq = Coby.sql3.sq3()
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

        self.headpic=Coby.hrt.getpic1("http://q1.qlogo.cn/g?b=qq&nk="+self.hrt.uin+"&s=100")
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
                self.pic_dissimg.append(Coby.hrt.getpic2(item['diss_cover']))
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
        for i,item in enumerate(self.songlv.get_children()):
            if item==self.songlv.focus():
                if self.event_obj.isSet()==False:
                    self._music_play (self.index_diss, i)
                    break
    def _music_play(self,d,s):
        retn=self.hrt.getsongmsg(d,s)
        print(retn)
        if len(retn)>3 and retn[9] !="":
            self.update()
            path=sys.path[0]+'/music/' + retn[4] + '.wav'
            for root, dirs, files in os.walk(sys.path[0]+"/music"):  # path 为根目录
                if retn[4]+".wav" in files:#能直接播放
                    self.event_obj.set()
                    self.update()
                    self.event_obj=threading.Event()
                    self.event_obj.clear()
                    t1 = threading.Thread(target=Media, args=(self.event_obj, path))
                    t1.setDaemon(True)
                    t1.start()
                else:
                    Coby.hrt.m4a_to_mp3(retn[9],retn[4],retn[4])#耗时操作，（下载+m4a转mp3+文件改名）
                    self.event_obj.set()
                    self.update()
                    self.event_obj = threading.Event()
                    self.event_obj.clear()
                    t1 = threading.Thread(target=Media, args=(self.event_obj, path))
                    t1.setDaemon(True)
                    t1.start()

        elif len(retn)>3 and retn[9]=="":
            messagebox.askquestion(title='？？？资源呢？？？', message='有资源，但没法播放，试试扫码登陆吧~')
        else:
            messagebox.askquestion(title='？？？没资源？？？', message='这个真没资源，估计下架了')

def Media(ev,url):
    try:
        CHUNK = 1024  # 我把它理解为缓冲流
        wf = wave.open(url, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),  # 设置声道数
                        rate=wf.getframerate(),  # 设置流的频率
                        output=True)
        data = wf.readframes(CHUNK)  # 音频数据初始化
        while ev.isSet()==False and  data != '':  # 直到音频放完
            stream.write(data)  # 播放缓冲流的音频
            data = wf.readframes(CHUNK)  # 更新data
            numpydata = np.fromstring(data, dtype=np.int16)#把data由字符串以十六进制的方式转变为数组
            transforamed=np.real(np.fft.fft(numpydata))#傅里叶变换获取实数部分
            count=32#设置间隔区
            for ix in Flycanvas.find_all():
                Flycanvas.delete(ix)
            fuc = 0
            y = Flycanvas.winfo_height()-40
            for n in range(0, transforamed.size, count):  # 从频域中的2048个数据中每隔count个数据中选取一条
                hight = abs(int(transforamed[n] / 10000))  # 对这么多数据取整和绝对值
                Flycanvas.create_rectangle(GetSystemMetrics(0)/64 * fuc+2, y, GetSystemMetrics(0)/64 * fuc + GetSystemMetrics(0)/64+2, y -  4 * hight)
                fuc+=1
            Flycanvas.update()
        stream.stop_stream()
        stream.close()
        p.terminate()
    except Exception as e:
        pass
def qrshow(hwnd1,hwnd2,hwnd3):
    try:
        print("QRshow:",hwnd1,hwnd2,hwnd3)
        hidetittle(hwnd3)
        hideFrame(hwnd1)
        dll = ctypes.WinDLL("./QRshow.dll")
        '''测试交互
        #dll.e_shadow(hwnd1)
        retn=dll.canvas_back(1)
        print("text",type(retn),retn)
        retn=ctypes.string_at(retn)
        print(type(retn),retn)
        print(bytes.decode(retn))'''
        x = ctypes.string_at(dll.e_openwindow(hwnd2))
        keycook = x.decode('utf-8')
        uin=Coby.hrt.getmsguin(keycook)

        ap.hrt=Coby.hrt.heartPack(uin)
        ap.hrt.cookie = keycook
        ap.jpLoginn()
    except Exception as e:
        print(e)
def hidetittle(hwnd=0):#隐藏标题栏但不会隐藏任务栏,代替self.master.overrideredirect(True)
    global user32,fhwnd
    fhwnd=user32.GetParent(hwnd)
    print("tk",fhwnd)
    user32.SetWindowLongA(fhwnd,-16,369229824)
def hideFrame(hwnd=0):
    global user32
    cs=user32.GetWindowLongA(hwnd,-20)
    cs=(cs|32)|524288
    user32.SetWindowLongA(hwnd,-20,cs)#鼠标穿透
    cs2=(240+240*256+240*256*256)#RGB
    user32.SetLayeredWindowAttributes(hwnd,cs2,255,3)#(窗口句柄,透明色,透明度,fuc代码)
    #print("shadowcanvas",hwnd)
def zmh(ckjb):
    global user32,Flycanvas
    zmjb = win32gui.FindWindow("Progman", "Program Manager")
    lpdwsult = 0
    user32.SendMessageTimeoutA(zmjb, 1324, 0, 0, 0, 1000, lpdwsult)
    retn=[]
    win32gui.EnumWindows(cha,retn)#枚举窗口+干活
    ret=user32.SetParent(ckjb, zmjb)
    Flycanvas.update()
def cha(hwnd,lparam):
    global user32,lock,deskhwnd
    if lock!=None and lock:
        name=win32gui.GetClassName(hwnd)
        if name=='WorkerW':
            rere=None
            rere=win32gui.FindWindowEx(hwnd,0,u'SHELLDLL_DefView',None)
            if rere!=0:
                lock=None
    elif lock==None:
        deskhwnd=hwnd
        user32.ShowWindowAsync(deskhwnd, False)
        lock=False
    elif lock==False:
        pass
def CallBack(hwnd, hwnds):
    hwnds[win32gui.GetClassName(hwnd)] = hwnd
    return True

if __name__ == "__main__":
    try:
        if os.path.isdir("music") ==False:
            os.mkdir("music")
        if os.path.isdir("data")==False:
            os.mkdir("data")
        user32=ctypes.windll.LoadLibrary('user32.dll')
        fhwnd=None
        Flycanvas=None
        lock = True
        deskhwnd = None
        top = Tk()
        ap=Application(top)
        ap.mainloop()
    except Exception as e:
        print(e)
        pass

