import datetime
import os
import time
from concurrent.futures.thread import ThreadPoolExecutor

import pymysql
import requests

conn = pymysql.connect("localhost", "root", "PandaPass!2", "laowai_panda_db_laowai_panda")
def get_unsynchronized_imgs():
    """
    获取未同步的图片
    """
    cursor = conn.cursor()
    try:
        sql = 'select id,image from connect_questionimage where update_time = 0'
        cursor.execute(sql)
        results = cursor.fetchall()
        images = []
        for result in results:
            temp = {}
            temp['id'] = result[0]
            temp['imgName'] = result[1]
            images.append(temp)

        return images
    except Exception as e:
        print("查询数据库异常", e)
        return None


def update_unsynchronized_imgs(id):
    cursor = conn.cursor()
    try:
        sql = f'update connect_questionimage set update_time = {int(time.time())} where id = {id}'
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("查询数据库异常", e)


def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    path = path.rstrip("/")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False

save_path = '/var/www/api/laowai_panda/media/'

def down_load_img(imgUrl, imgName,id):
    img_path = imgName.split('/')
    if len(img_path) > 1:
        save_dir = save_path + img_path[0] + '/'
        mkdir(save_dir)
    save_img_path = save_path + str(imgName)
    try:
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }
        res = requests.get(imgUrl, headers=header, timeout=120)
        if res.status_code != 200:
            print(imgUrl,'下载网络错误：',res.status_code)
            return False
        with open(save_img_path, 'wb') as f:
            f.write(res.content)
        print(imgUrl, '下载成功')
        update_unsynchronized_imgs(id)
        return save_img_path
    except Exception as e:
        print(imgUrl, "下载图片错误XXXX", e)
        try:
            os.remove(save_img_path)
        except Exception as e:
            pass
        return False


def do_down_load_remote_img(imgName,id):
    downloadImgUrlList = [
        'http://45.13.199.57/media/' + imgName,  # 德國
        'http://121.40.208.210/media/' + imgName,  # 杭州
    ]
    for imgUrl in downloadImgUrlList:
        down_load_img(imgUrl, imgName,id)

def main():
    images = get_unsynchronized_imgs()
    with ThreadPoolExecutor(max_workers=30) as thread:
        for image in images:
            # do_down_load_remote_img(imgName)
            thread.submit(do_down_load_remote_img, image['imgName'],image['id'])

if __name__ == '__main__':
    main()
    print('完成',datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))