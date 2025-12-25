from crawler import DoubanMovieCrawler
from analyzer import MovieAnalyzer
import time

def main():
    print("="*50)
    print("       豆瓣Top250电影爬虫与可视化分析工具")
    print("="*50)

    # 步骤1：爬取电影数据
    crawler = DoubanMovieCrawler()
    while True:
        choice = input("是否开始爬取豆瓣Top250电影数据？(y/n)：").strip().lower()
        if choice == "y":
            page_num = input("请输入爬取页数（每页25部，范围1-10）：")
            if page_num.isdigit():
                page_num = int(page_num)
                # 新增页数范围校验
                if 1 <= page_num <= 10:
                    if crawler.crawl_movies(page_num):
                        crawler.save_data()
                    break
                else:
                    print("请输入1-10之间的数字！")
            else:
                print("请输入有效的数字（1-10）！")
        elif choice == "n":
            print("跳过爬取，直接加载已有数据...")
            time.sleep(1)
            break
        else:
            print("输入无效，请输入 y 或 n！")

    # 步骤2：电影数据可视化分析
    analyzer = MovieAnalyzer()
    if not analyzer.data:
        print("无有效数据可分析，程序结束")
        return

    # 功能菜单交互
    while True:
        print("\n--- 数据分析功能菜单 ---")
        print("1. 电影类型数量分布")
        print("2. 各地区电影平均分")
        print("3. 各年份电影数量趋势")
        print("4. 演员出镜频次Top15")
        print("5. 退出程序")
        func_choice = input("请选择功能（输入1-5）：").strip()

        if func_choice == "1":
            analyzer.stat_type_count()
        elif func_choice == "2":
            analyzer.stat_region_score()
        elif func_choice == "3":
            analyzer.stat_year_trend()
        elif func_choice == "4":
            analyzer.stat_actor_frequency()
        elif func_choice == "5":
            print("程序已正常退出，再见！")
            break
        else:
            print("功能编号无效，请重新选择（1-5）！")

if __name__ == "__main__":
    main()