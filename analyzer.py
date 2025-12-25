import json
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
import platform
import re

# 配置中文字体
def set_chinese_font():
    system = platform.system()
    if system == "Windows":
        plt.rcParams["font.family"] = ["SimHei", "Microsoft YaHei"]
    elif system == "macOS":
        plt.rcParams["font.family"] = ["PingFang SC", "Songti SC"]
    else:
        plt.rcParams["font.family"] = ["WenQuanYi Micro Hei", "SimHei"]
    plt.rcParams["axes.unicode_minus"] = False

set_chinese_font()


class MovieAnalyzer:
    def __init__(self, data_file="data.json"):
        self.data = self.load_data(data_file)
        if self.data:
            self.df = pd.DataFrame(self.data)
            print(f"成功加载 {len(self.data)} 条电影数据")
        else:
            print("数据加载失败")
            self.df = None  # 显式初始化避免属性不存在

    def load_data(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"错误：未找到 {filename} 文件")
            return None
        except json.JSONDecodeError:
            print(f"错误：{filename} 格式损坏")
            return None

    def stat_type_count(self):
        """统计类型分布 + 保存图片"""
        if not self.data:
            return
        # 拆分多类型并统计
        all_types = []
        for movie in self.data:
            # 处理可能的空类型或异常格式
            if movie.get("type"):
                all_types.extend(movie["type"].split("/"))
        type_counter = Counter(all_types)
        plt.figure(figsize=(12, 6))
        x = list(type_counter.keys())
        y = list(type_counter.values())
        plt.bar(x, y, color="#1f77b4", alpha=0.8)
        plt.title("豆瓣Top250电影类型分布", fontsize=16, fontweight="bold", pad=20)
        plt.xlabel("电影类型", fontsize=14, labelpad=15)
        plt.ylabel("电影数量", fontsize=14, labelpad=15)
        plt.xticks(rotation=45, ha="right", fontsize=12)
        plt.yticks(fontsize=12)
        for i, v in enumerate(y):
            plt.text(i, v + 0.1, str(v), ha="center", fontsize=10)
        plt.tight_layout()
        
        # 保存图片
        save_path = "movie_type_distribution.png"
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"类型分布图表已保存为：{save_path}")
        
        plt.show()

    def stat_region_score(self):
        """统计地区评分 + 保存图片"""
        if not self.data or self.df is None:
            return
        # 处理可能的多地区数据（取第一个地区）
        self.df["region_clean"] = self.df["region"].apply(
            lambda x: x.split("/")[0] if x else "未知"
        )
        region_score = self.df.groupby("region_clean")["score"].mean().sort_values(ascending=False)
        plt.figure(figsize=(10, 8))
        region_score.plot(kind="barh", color="#ff7f0e", alpha=0.8)
        plt.title("各地区豆瓣Top250电影平均分", fontsize=16, fontweight="bold", pad=20)
        plt.xlabel("平均分", fontsize=14, labelpad=15)
        plt.ylabel("地区", fontsize=14, labelpad=15)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        for i, v in enumerate(region_score):
            plt.text(v + 0.02, i, f"{v:.2f}", va="center", fontsize=10)
        plt.xlim(8.0, 9.5)
        plt.tight_layout()
        
        # 保存图片
        save_path = "movie_region_score.png"
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"地区评分图表已保存为：{save_path}")
        
        plt.show()

    def stat_year_trend(self):
        """统计年份趋势 + 保存图片"""
        if not self.data or self.df is None:
            return
        # 优化年份提取逻辑（从字符串中提取4位数字年份）
        def extract_year(x):
            if not x:
                return None
            match = re.search(r'\b\d{4}\b', str(x))
            return match.group() if match else None
        
        self.df["year_clean"] = self.df["year"].apply(extract_year)
        self.df = self.df.dropna(subset=["year_clean"])
        # 转换为整数类型便于排序
        self.df["year_clean"] = self.df["year_clean"].astype(int)
        year_counter = self.df["year_clean"].value_counts().sort_index()
        plt.figure(figsize=(14, 6))
        plt.plot(year_counter.index, year_counter.values, marker="o", color="#2ca02c", linewidth=2)
        plt.title("豆瓣Top250电影年份数量趋势", fontsize=16, fontweight="bold", pad=20)
        plt.xlabel("年份", fontsize=14, labelpad=15)
        plt.ylabel("电影数量", fontsize=14, labelpad=15)
        plt.xticks(rotation=45, ha="right", fontsize=12)
        plt.yticks(fontsize=12)
        for i, (year, count) in enumerate(zip(year_counter.index, year_counter.values)):
            plt.text(year, count + 0.1, str(count), ha="center", fontsize=9)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        # 保存图片
        save_path = "movie_year_trend.png"
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"年份趋势图表已保存为：{save_path}")
        
        plt.show()

    def stat_actor_frequency(self):
        """统计演员出镜频次（Top15）+ 保存图片"""
        if not self.data:
            return
        
        # 提取所有演员，处理可能的字符串格式
        all_actors = []
        for movie in self.data:
            actors = movie.get("actors", [])
            # 处理可能的字符串类型演员列表（如"张国荣/梁朝伟"）
            if isinstance(actors, str):
                all_actors.extend(actors.split("/"))
            elif isinstance(actors, list):
                all_actors.extend(actors)
        
        # 统计演员出镜次数，筛选Top15（排除"未知演员"）
        actor_counter = Counter(all_actors)
        for name in ["未知演员", "未知"]:
            if name in actor_counter:
                del actor_counter[name]
        top15_actors = actor_counter.most_common(15)
        actor_names = [item[0] for item in top15_actors]
        actor_counts = [item[1] for item in top15_actors]
        
        # 绘制横向条形图
        plt.figure(figsize=(10, 8))
        plt.barh(actor_names, actor_counts, color="#d62728", alpha=0.8)
        plt.title("豆瓣Top250电影演员出镜频次Top15", fontsize=16, fontweight="bold", pad=20)
        plt.xlabel("出镜次数（电影部数）", fontsize=14, labelpad=15)
        plt.ylabel("演员姓名", fontsize=14, labelpad=15)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        
        # 添加数值标签
        for i, v in enumerate(actor_counts):
            plt.text(v + 0.05, i, str(v), va="center", fontsize=10)
        
        plt.tight_layout()
        
        # 保存图片
        save_path = "movie_actor_frequency.png"
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"演员出镜频次图表已保存为：{save_path}")
        
        plt.show()