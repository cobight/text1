import json,sys
import sqlite3
class sq3:#D:\Python\sqlite3_space\demo1.db3
    def __init__(self):
        url=sys.path[0]+"\\data\\tx.db"
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
        sql = 'insert into myPACK values( ?,? )'
        if len(retnb)!=0:
            self.dele(QQnumber)
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

if __name__ =='__main__':
    sq=sq3()
    print(sq.selec('1415470614'))