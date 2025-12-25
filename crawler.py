import requests
import json
from bs4 import BeautifulSoup
import time

class DoubanMovieCrawler:
    def __init__(self):
        self.movies = []
        # 请求头，模拟浏览器访问，避免被反爬
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.base_url = "https://movie.douban.com/top250"

    def get_movie_info(self, movie_url):
        """获取单部电影的详细信息"""
        try:
            response = requests.get(movie_url, headers=self.headers, timeout=10)
            response.raise_for_status()  # 抛出请求异常
            soup = BeautifulSoup(response.text, "html.parser")

            # 提取电影核心信息
            title = soup.find("span", property="v:itemreviewed").text if soup.find("span", property="v:itemreviewed") else "未知标题"
            score = float(soup.find("strong", class_="ll rating_num").text) if soup.find("strong", class_="ll rating_num") else 0.0
            year = soup.find("span", class_="year").text if soup.find("span", class_="year") else "未知年份"
            type_ele = soup.find_all("span", property="v:genre")
            movie_type = "/".join([t.text for t in type_ele]) if type_ele else "未知类型"
            region_ele = soup.find("div", id="info").text
            # 提取地区（简单处理，适配豆瓣格式）
            region = "未知地区"
            if "制片国家/地区:" in region_ele:
                region = region_ele.split("制片国家/地区:")[1].split("\n")[0].strip()
            # 提取演员
            actor_ele = soup.find_all("a", rel="v:starring")
            actors = [a.text for a in actor_ele] if actor_ele else ["未知演员"]

            movie_info = {
                "title": title,
                "score": score,
                "year": year,
                "type": movie_type,
                "region": region,
                "actors": actors
            }
            return movie_info
        except Exception as e:
            print(f"❌ 获取单部电影信息失败：{str(e)}")
            return None

    def crawl_movies(self, page_num):
        """爬取指定页数的电影数据"""
        self.movies = []  # 清空原有数据
        print(f"开始爬取豆瓣top250榜单，共{page_num}页...")
        for page in range(1, page_num + 1):
            try:
                # 计算偏移量，豆瓣top250每页25条
                offset = (page - 1) * 25
                url = f"{self.base_url}?start={offset}&filter="
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                # 提取每页的电影链接
                movie_items = soup.find_all("div", class_="item")
                for item in movie_items:
                    movie_link = item.find("a")["href"]
                    movie_info = self.get_movie_info(movie_link)
                    if movie_info:
                        self.movies.append(movie_info)
                        time.sleep(0.5)  # 延时，避免请求过快被封

                print(f"✅ 第{page}页爬取完成，获取{len(movie_items)}部电影")
                time.sleep(1)  # 每页爬取后延时
            except Exception as e:
                print(f"❌ 第{page}页爬取失败：{str(e)}")
                return False

        print(f"📊 爬取完成！共获取{len(self.movies)}部电影数据")
        return len(self.movies) > 0

    def save_data(self, filename="data.json"):
        """保存数据到JSON文件（统一为data.json，与分析器匹配）"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=2)
            print(f"💾 数据已保存至{filename}")
            return True
        except Exception as e:
            print(f"❌ 数据保存失败：{str(e)}")
            return False