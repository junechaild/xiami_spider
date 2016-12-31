import requests
import lxml.html as lx
import pandas as pd
import math
#from multiprocessing.dummy import Pool
from selenium import webdriver
from gevent.pool import Pool
import gevent
import time
import re
class XiamiSpder():
    def __init__(self,url):#定义需要爬取的数据和相关变量
        self.url=url
        self.headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                               '(KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
        self.cookies={'gid':'148230424430779',
         '_xiamitoken':'110e8bd93f93cf9022beaced77cbea99',
         '_unsign_token':'12e630ef05e0498f4ed75edfd235cfaa',
         'CNZZDATA921634':'cnzz_eid%3D1925397266-1482300850-%26ntime%3D1482300850',
         'CNZZDATA2629111':'cnzz_eid%3D191862154-1482301573-%26ntime%3D1482301573',
         'cna':'9BjhEJqDQkUCAdOiGi3dEudT',
         'l':'AmJiyzVIGfmcQs111spmH98oMuLA6GbN',
	     'isg':'Ari414mpFEFBsnjFzY7kAH_IiWbyWRyruRH6jvItWPOmDVL3lDI-Ovtvs7JH',
	     'login_method':'mobilelogin',
         'member_auth':'',
        'user':''
        }
        #self.proxy={'http':'113.244.150.57'}
        self.song_name=[]
        self.song_url=[]
        self.song_singer=[]
        self.song_comment_num=[]
        self.song_play_num=[]
        self.album_name=[]
        self.album_url=[]
        self.album_language=[]
        self.album_date=[]
        self.album_score=[]
        self.album_genre=[]
        self.driver = webdriver.PhantomJS(executable_path="C:\\Users\\trian\Downloads\phantomjs-1.9.7-windows\phantomjs.exe")

    def albumcrawl(self,album_url,retry=6):#专辑爬虫
        album_re=requests.get(album_url,cookies=self.cookies,headers=self.headers)
        if(album_re.status_code==200):
            print("爬取专辑页面："+album_url)
            album_tree=lx.fromstring(album_re.text)
            album_score = self.is_empty(album_tree.xpath("//p[@class='clearfix']/em/text()"))
            album_language = self.is_empty(album_tree.xpath("//div[@id='album_info']/table/tr[2]/td[2]/text()"))
            album_company = self.is_empty(album_tree.xpath("//div[@id='album_info']/table/tr[3]/td/a/text()"))
            album_date = self.is_empty(album_tree.xpath("//div[@id='album_info']/table/tr[4]/td[2]/text()"))
            album_genre = self.is_empty(album_tree.xpath("//div[@id='album_info']/table/tr[6]/td/a/text()"))
            return{'album_score':album_score,
               'album_language':album_language,
               'album_company':album_company,
               'album_date':album_date,
               'album_genre':album_genre
               }
        else:
            time.sleep(5)
            print("爬取"+album_url+"失败")


    def is_empty(self,item):#判断字段是否为空的函数
        if len(item)==0:
            return "无"
        else:
            return item[0]

    def songcrawl(self,song_url):#歌曲爬虫
        #time.sleep(4)
        song_re=requests.get(song_url,cookies=self.cookies,headers=self.headers)
        self.driver.get(song_url)
        time.sleep(0.8)
        if(song_re.status_code==200):
            print("爬取歌曲页面："+song_url)
            song_tree=lx.fromstring(song_re.text)
            song_name=self.is_empty(song_tree.xpath("//div[@id='wrapper']/div[@id='title']/h1/text()"))
            song_singer=self.is_empty(song_tree.xpath("//table[@id='albums_info']/tr[2]/td[2]/div/a/text()"))
            song_comment_num=self.is_empty(song_tree.xpath("//ul[@class='clearfix']/li[3]/a/text()"))
            album_name=self.is_empty(song_tree.xpath("//div[@class='album_relation']/div[@class='cover']/a/@title"))
            album_url =self.is_empty(song_tree.xpath("//div[@class='album_relation']/div[@class='cover']/a/@href"))
            if(album_url!='无'):
                if (album_url.find("www.xiami.com")):
                    album_url = "https://www.xiami.com" + album_url
                album=self.albumcrawl(album_url)
                song_play_num = self.driver.find_element_by_id("play_count_num").text
            else:
                album={'album_score':'无',
               'album_language':'中文',
               'album_company':'无',
               'album_date':'无',
               'album_genre':'无'
               }
                song_name=song_tree.xpath("//div[@class='demo-player']/h2/text()")[0]
                song_singer=song_tree.xpath("//div[@class='demo-player']/h2/span/text()")[0]
                song_play_num='无'
                album_name="demo"
                song_comment_num=song_tree.xpath("//div[@class='all_page']/span/text()")[0]
                song_comment_num=re.findall(r"\d+",song_comment_num)[1]

            print("歌曲名："+song_name)
            print("歌曲地址："+song_re.url)
            print("歌手名：" + song_singer)
            print("专辑名：" + album_name)
            print("评论数：" + song_comment_num)
            print("试听数："+song_play_num)
            print("专辑地址：",album_url)
            print("专辑评分:"+album["album_score"])
            print("语言:"+album['album_language'])
            print("发行时间:"+album['album_date'])
            print("发行公司:"+album['album_company'])
            print("风格流派:"+album['album_genre'])
            self.song_name.append(song_name)
            self.song_comment_num.append(song_comment_num)
            self.song_singer.append(song_singer)
            self.song_url.append(song_url)
            self.album_name.append(album_name)
            self.album_score.append(album["album_score"])
            self.album_date.append(album['album_date'])
            self.album_language.append(album['album_language'])
            self.album_genre.append(album['album_genre'])
            self.album_url.append(album_url)
            self.song_play_num.append(song_play_num)

            print(len(self.song_name))

        else:
            time.sleep(5)
            print("爬取" + song_url + "失败")

    def musiccrawl(self,url):#收藏列表爬虫
        music_re=requests.get(url,cookies=self.cookies,headers=self.headers)
        if(music_re.status_code==200):
            print("爬取页面："+url)
            music_tree=lx.fromstring(music_re.text)
            song_url = music_tree.xpath("//div/table[@class='track_list']/tbody/tr/td[@class='song_name']/a[1]/@href")  # 选取属性用@
            for urls in song_url:
                if (urls.find("www.xiami.com")):
                    url = "https://www.xiami.com" + urls
            #music_pool=Pool(4)
            #music_pool.map(self.songcrawl,song_url)
            music_spider=[]
            for urls in song_url:
                music_spider.append(gevent.spawn(self.songcrawl,urls))
            gevent.joinall(music_spider)
            #music_pool.close()
            #music_pool.join()
        else:
            time.sleep(15)
            #self.musiccrawl(url)
            print("爬取"+url+"失败")

    def xiamicrawl(self):#起始爬虫
        music_re = requests.get(self.url, cookies=self.cookies, headers=self.headers)
        print(music_re.status_code)
        music_tree = lx.fromstring(music_re.text)
        song_sum = str(music_tree.xpath("//div[@class='c695_l_content']/div[@class='all_page']/span/text()")[0])
        print(song_sum)
        start = song_sum.find('共')
        end = song_sum.find('条')
        song_sum = int(song_sum[start + 1:end])
        print('总共'+str(song_sum)+"首歌曲")
        page_sum = math.ceil(song_sum / 25)  # 向上取整
        print('共计'+str(page_sum)+'页')
        song_urls = []
        for i in range(1, page_sum + 1):
            u = 'http://www.xiami.com/space/lib-song/u/44316745/page/' + str(i)
            song_urls.append(u)


        #xiami_pool=Pool(4)
        #xiami_pool.map(self.musiccrawl,song_urls)
        xiami_spider=[]
        for url in song_urls:
            xiami_spider.append(gevent.spawn(self.musiccrawl,url))
        gevent.joinall(xiami_spider)
        #xiami_pool.close()
        #xiami_pool.join()
        self.save_data()

    def save_data(self):#保持数据函数
        music=pd.DataFrame()
        music['song_name']=self.song_name
        music['song_singer']=self.song_singer
        music['song_url']=self.song_url
        music['song_comment_num']=self.song_comment_num
        music['song_play_num']=self.song_play_num
        music['album_name']=self.album_name
        music['album_url']=self.album_url
        music['album_score']=self.album_score
        music['album_language']=self.album_language
        music['album_date']=self.album_date
        music['album_language']=self.album_language
        music['album_genre']=self.album_genre
        music.to_csv("xiami_music.csv", headers=True, index_label="ID", encoding='utf-8')


start_url='http://www.xiami.com/space/lib-song/u/44316745'
requests.adapters.DEFAULT_RETRIES = 5
#s = requests.session()
#s.keep_active= False
spider=XiamiSpder(start_url)
spider.xiamicrawl()

