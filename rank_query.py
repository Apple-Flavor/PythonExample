# -*- coding: utf-8 -*-
import json
import logging
import requests
import lxml.html

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

DOWNLOADS = 0
DOWNLOAD_URL = 1

def cn_number_to_latin(text):
    # "1235下载"
    # "1.2万下载"
    # "1.2亿下载"
    try:
        if isinstance(text, str):
            text = text.decode("utf-8")
        elif not isinstance(text, unicode):
            return 0

        if text[-2:] != u"下载":
            return 0

        text = text[:-2]
        if text[-1] == u"亿":
            return int(float(text[:-1]) * 100000000)
        elif text[-1] == u"万":
            return int(float(text[:-1]) * 10000)
        elif text[-1] == u"千":
            return int(float(text[:-1]) * 1000)
        elif text[-1] == u"百":
            return int(float(text[:-1]) * 100)
        else:
            return int(text)
    except Exception, e:
        print text
        return 0


class Baidu(object):

    @staticmethod
    def query(result):
        categories = {
        "社交通讯": 503, "影音播放": 506, "系统工具": 501, "拍摄美化": 508, "理财购物": 510,
        "生活实用": 504, "主题壁纸": 502, "资讯阅读": 505, "旅游出行": 509, "办公学习": 507,
        "休闲益智": 401, "动作射击": 403, "赛车竞速": 406, "棋牌桌游": 407,
        "经营养成": 408, "角色扮演": 402, "体育竞技": 405, "模拟辅助": 404  # "网络游戏": absent
        }
        for cat, cid in categories.items():
            Baidu._query(cat, cid, result)

    @staticmethod
    def _query(cate, cid, ret):
        list_request_url = r"http://shouji.baidu.com/game/list?cid=%d&page_num=%d"
        page = 0
        rank = 0  # rank starts from 1
        while True:
            page += 1  # start from page 1 not 0
            page_url = list_request_url % (cid, page)
            logger.debug("requesting page %d" % page)
            resp = requests.get(page_url)
            tree = lxml.html.fromstring(resp.content)
            matches = tree.xpath('.//div[@class = "app-meta"]')
            # matches = tree.xpath()
            if matches is None or len(matches) == 0:
                logger.info("No more apps available")
                logger.info("processed range (%d, %d)" % (1, rank))
                return
            for m in matches:
                rank += 1
                downloads = m.find('p/span[@class="down"]')
                downloads = cn_number_to_latin(downloads.text)
                apk = m.find(".//span[@data_url]")
                url = apk.get("data_url")
                package = apk.get("data_package")
                name = apk.get("data_name")
                # version = apk.get("data_versionname")
                # logger.debug("found a url:" + url)
                if package not in ret:
                    ret[package] = []
                ret[package] += [[downloads, name, u"Baidu", url], ]
                if rank == 10000: # debugging purpose
                    return


class Wandoujia(object):
    categories = ["topgame", "topapp"]

    @staticmethod
    def query(result):
        for c in Wandoujia.categories:
            Wandoujia._query(c, result)

    @staticmethod
    def _query(category, ret):
        request_url = r"http://apps.wandoujia.com/api/v1/apps?max=60&" \
                      r"start=%d&type=%s&opt_fields=apks.packageName,stat.total,alias"
        download_url = r"http://apps.wandoujia.com/apps/%s/download"
        page = 0
        rank = 0  # rank starts from 1
        while True:
            page += 1  # start from page 1 not 0
            page_url = request_url % (60 * (page - 1), category)
            resp = requests.get(page_url)
            if resp.status_code == 404:
                break
            apks = json.loads(resp.content)
            for a in apks:
                rank += 1
                package = a['apks'][0]['packageName']
                downloads = a['stat']['total']
                name = a['alias']
                if name is None:
                    name = "unknown"
                url = download_url % package
                if package not in ret:
                    ret[package] = []
                ret[package] += [[downloads, name, u"Wandoujia", url],]
                if rank >= 10000: # debugging purpose
                    return ret
        return ret


class Tencent(object):
    @staticmethod
    def query(r):
        categories = {
            "视频": 103, "音乐": 101, "购物": 122, "阅读": 102, "导航": 112,
            "社交": 106, "摄影": 104, "新闻": 110, "工具": 115, "美化": 119,
            "教育": 111, "生活": 107, "安全": 118, "旅游": 108, "儿童": 100,
            "理财": 114, "系统": 117, "健康": 109, "娱乐": 105, "办公": 113,
            "通讯": 116
        }
        for v in categories.itervalues():
            Tencent._query(v, r)

    @staticmethod
    def _query(cid, result):
        request_url = r"http://sj.qq.com/myapp/cate/appList.htm?orgame=1&categoryId=%d&pageSize=1000&pageContext=0"
        rank = 0  # rank starts from 1
        page_url = request_url % cid
        resp = requests.get(page_url)
        d = json.loads(resp.content)
        for item in d['obj']:
            rank += 1
            url = item['apkUrl']
            downloads = item['appDownCount']
            package = item['pkgName']
            name = item['appName']
            # logger.debug("found a url:" + url)
            if package not in result:
                result[package] = []
            result[package] += [[downloads, name, u"Tecent", url],]
            if rank == 10000: # debugging purpose
                return



def is_inculde(pkg_name,input_f):
    with open(input_f,"r") as f:
        f_contents = f.readlines()
    if str(pkg_name) in ''.join(f_contents):
        return True
    else:
        return False
def save_result(input_f):
    with open("./output.csv", "w+") as f:
        for k, v in r.iteritems():
            if is_inculde(k,input_f)==False:
                continue
            max = None
            downloads = 0
            for item in v:
                downloads += item[0]
                if max is None:
                    max = item
                elif max[0] < item[0]:
                    max = item
            try:
                for each in [k, ",", max[3].encode("utf-8"),",",str(downloads), ",", max[1].encode("utf-8"), ",", max[2].encode("utf-8"), "\n"]:
                    f.write(each)
            except Exception, e:
                print max[1], max[2], max[3]
                # max[1]
                print type(max[1]), type(max[2]), type(max[3])
                raise e

if __name__=="__main__":
    r = {}
    Tencent.query(r)
    Wandoujia.query(r)
    Baidu.query(r)
    save_result("input.csv")
