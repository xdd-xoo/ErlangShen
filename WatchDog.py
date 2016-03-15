#-*- coding:utf-8 -*-
import urllib 
import re
import os 
import time    
app_root_url = r"http://apk.hiapk.com/apps/"
game_root_url = r"http://apk.hiapk.com/games/"
android_web_root = r"http://apk.hiapk.com"

def update_app_category(app_root_url):
    content = urllib.urlopen(app_root_url).readlines()
    regex = re.compile(r'class="category_item"><a href="/.*/(.*)"> <s')
    app_category = []
    for line in content:
        res = re.findall(regex,line)
        if res:
            app_category.append(app_root_url+res[0])

    return app_category
    		
def update_game_category(game_root_url):
    content = urllib.urlopen(game_root_url).readlines()
    regex = re.compile(r'class="category_item"><a href="/.*/(.*)"> <s')
    game_category = []
    for line in content:
        res = re.findall(regex,line)
        if res:
            game_category.append(game_root_url+res[0])
    return game_category

def collect_app_url():
    app_urls = []
    for url in update_app_category(app_root_url):
        app_down = []
        content = urllib.urlopen(url).readlines()
        for line in content:
            res = re.findall(r'<a href="(/appdown/.*)" rel="nofollow">$',line.strip())
            if res:
                app_down.append(res[0])
        #print app_down[0:5]
        app_urls.extend(app_down[0:5])
    return app_urls

def collect_game_url():
    game_urls = []
    for url in update_game_category(game_root_url):
        game_down = []
        content = urllib.urlopen(url).readlines()
        for line in content:
            res = re.findall(r'<a href="(/appdown/.*)" rel="nofollow">$',line.strip())
            if res:
                game_down.append(res[0])
        #print app_down[0:5]
        game_urls.extend(game_down[0:5])
    return game_urls

def init_local_downloads(category):
    foder = category.split("/")[-2]
    sub_folder = category.split("/")[-1]
    print "mkdir  %s\%s"%(foder,sub_folder)
    os.system("mkdir %s\%s"%(foder,sub_folder))



if __name__ == "__main__":
    app_urls = collect_app_url()
    game_urls = collect_game_url()

    local_game_storage = "C:\Dropbox\APKs\Games"
    if not os.path.isdir(local_game_storage):
        os.system("mkdir %s"%local_game_storage)
    local_app_storage = "C:\Dropbox\APKs\Apps"
    if not os.path.isdir(local_app_storage):
        os.system("mkdir %s"%local_app_storage)
    item = 1

    for app in game_urls:
        #print "Start to download the %d : %s.apk"%(item,app.split("/")[-1])
        try:
            print "Start to download the %d : %s"%(item,app.split("/")[-1])
            urllib.urlretrieve(android_web_root+app,local_game_storage+"\\"+app.split("/")[-1]+".apk")
            item +=1
        except :
            print "download %s failed"%app
    for app in app_urls:
        try:

            print "Start to download the %d : %s"%(item,app.split("/")[-1])
            urllib.urlretrieve(android_web_root+app,local_app_storage+"\\"+app.split("/")[-1]+".apk")
            item +=1
        except :
            print "download %s failed"%app