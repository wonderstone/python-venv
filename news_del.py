# use apscheduler to delete n days before news from database

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

from ngroup import *

def delete_news(ndays):
    db = NGroupDatabase("news_groups.json")
    # use minutes for testing
    current_time_minus_ndays = datetime_to_str(datetime.now() - timedelta(minutes=ndays))
    db.remove_news_before(current_time_minus_ndays)
    print(f"Deleted all news before {current_time_minus_ndays}")


def add_news():
    db = NGroupDatabase("news_groups.json")

    # 获取当前时间1分钟之前的时间标签
    current_time_minus15 = datetime_to_str(datetime.now() - timedelta(minutes=15))

        # 添加新闻
    news1 = NGroup(
        stocks=['特斯拉', '比亚迪'],
        summary="some news",
        news_time=current_time_minus15,  # 直接传递字符串
        tag="flash20250303110556631800"
    )
    db.add_news(news1)


if __name__ == "__main__":




    # 使用 apscheduler 定时删除数据库中的新闻
    scheduler = BackgroundScheduler()
    # 每30秒添加一条新闻
    scheduler.add_job(add_news, 'interval', seconds=30)
    # 每1分钟删除一次数据库中10分钟之前的新闻
    scheduler.add_job(delete_news, 'interval', minutes=1, args=[10])
    scheduler.start()

    # 运行调度器
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped!")