# todo: 可能后续会有调整
import json
from typing import List
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta

# 将 datetime 对象转换为字符串
def datetime_to_str(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

# 将字符串转换为 datetime 对象
def str_to_datetime(time_str):
    return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")


class NGroup(BaseModel):
    stocks: List[str] = Field(..., description="A list of stocks related to the news.")
    summary: str = Field(..., description="A brief summary of the news related to the stocks.")
    news_time: str = Field(..., description="The time when the news was published, as a string.")
    tag: Optional[str] = None


class NGroupDatabase:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.load_data()

    def load_data(self):
        """加载已有的数据文件，如果没有则初始化为空列表"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.data = [NGroup(**item) for item in json.load(file)]
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = []

    def save_data(self):
        """将数据保存回文件"""
        with open(self.file_path, 'w', encoding='utf-8') as file:
            # 使用 pydantic 的 .json() 方法来正确地序列化数据
            json.dump([item.model_dump() for item in self.data], file, ensure_ascii=False, indent=4)

    def add_news(self, news_group: NGroup):
        """增加新闻"""
        self.data.append(news_group)
        self.save_data()

    def remove_news(self, news_time: str):
        """通过新闻时间删除新闻"""
        self.data = [news for news in self.data if news.news_time != news_time]
        self.save_data()

    def remove_news_before(self, news_time: str):
        """删除指定时间之前的所有新闻"""
        del_time = str_to_datetime(news_time)
        self.data = [news for news in self.data if str_to_datetime(news.news_time) >= del_time]
        self.save_data()

    def get_all_news(self) -> List[NGroup]:
        """获取所有新闻"""
        return self.data

    def get_news_by_time(self, news_time: str) -> Optional[NGroup]:
        """通过时间获取单条新闻"""
        for news in self.data:
            if news.news_time == news_time:
                return news
        return None

    def get_newslist_by_time_range(self, start_time: str, end_time: str) -> List[NGroup]:
        """通过时间范围获取新闻列表"""
        start_datetime = str_to_datetime(start_time)
        end_datetime = str_to_datetime(end_time)
        return [news for news in self.data if start_datetime <= str_to_datetime(news.news_time) <= end_datetime]

if __name__ == "__main__":
    # 使用示例：
    db = NGroupDatabase("news_groups.json")

    # 获取当前时间字符串 使用 datetime_to_str() 函数
    current_time = datetime_to_str(datetime.now())

    # 获取当前时间1分钟之前的时间标签
    current_time_minus1 = datetime_to_str(datetime.now() - timedelta(minutes=1))

    # 打印当前时间



    print(f"Current time: {current_time}")
    print(f"Current time minus 1 minute: {current_time_minus1}")


    # delete all news before current time_minus1
    db.remove_news_before(current_time_minus1)

    # 添加新闻
    news1 = NGroup(
        stocks=['特斯拉', '比亚迪'],
        summary="some news",
        news_time=current_time,  # 直接传递字符串
        tag="flash20250303110556631800"
    )
    db.add_news(news1)

    # 删除新闻
    # db.remove_news("2025-02-11T15:30:00")

    # 获取所有新闻
    print(db.get_all_news())

    # 获取特定时间的新闻
    print(db.get_newslist_by_time_range(current_time_minus1, current_time))

