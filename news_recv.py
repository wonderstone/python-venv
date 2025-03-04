import redis
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import JsonOutputParser

from pydantic import BaseModel, Field
from typing import Literal

from common import *
from langchain_core.messages import AIMessage

from ngroup import *

# 实例化 NGroupDatabase
db = NGroupDatabase("news_groups.json")

# 读取配置文件
config = read_yaml_config("config.yaml")
system_prompt = config["prompts"]["system_prompt"]
user_prompt = config["prompts"]["user_prompt"]
ds_prompt = config["prompts"]["ds_prompt"]
system_prompt1 = config["prompts"]["system_prompt1"]
analysis_template = config["prompts"]["analysis_template"]

# 连接到 Redis 服务器
r = redis.Redis(host='localhost', port=6379, db=0)

# ~1. 实例化 ChatOllama
llm = ChatOllama(model="llama3.2:latest", temperature = 0.0, num_predict = 256,)
llm_Qwen14 = ChatOllama(model="Qwen2.5:14b", temperature = 0.0,num_predict = 1024,)
llm_ds14  = ChatOllama( model="deepseek-r1:14b",temperature = 0.0,num_predict = 256,)

lc = llm_Qwen14|JsonOutputParser()


# ~2. Pydantic限定输出的数据结构
class Category(BaseModel):
    """Category that news should be sorted into."""
    # Category should be in one of the following: 'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'
    Category: Literal["收市综评", "公司新闻", "其他"] = Field(None, description="Category that news should be sorted into.")

structured_llm = llm.with_structured_output(Category)

# ~3. prompt part
def prompt_analysis_lc(system_prompt, user_prompt, news):
    final_prompt =system_prompt + user_prompt.format(news) 
    return final_prompt

# ~4. tmp ds part
def get_str_from_output(output):
    tmp= output.content
    tmp = tmp.split('</think>')[1]
    return ds_prompt.format(tmp)

from langchain_core.runnables import RunnableLambda

tmpchain = llm_ds14|RunnableLambda(get_str_from_output) | structured_llm



# & 01 func to get category
def get_category(system_prompt, user_prompt, news, chain):
    final_prompt = prompt_analysis_lc(system_prompt, user_prompt, news)
    return chain.invoke(final_prompt)

# & 02 check the category
def check_category(output):
    # check the output type
    # if output is Category, return its content
    if isinstance(output, Category):
        return output.Category
    elif isinstance(output, AIMessage): # if it is llm output, return the content
        return output.content

# & 03 force the category
def force_category(category):
    # todo : 如果出现llm输出非设定项目的救济方案，可引入label_similarity_bert中的函数
    return category

# & 04 branch runnable
def branch_runnable(category, news):
    if category == "公司新闻":
        final_prompt = prompt_analysis_lc(system_prompt1, analysis_template, news)
        # print(final_prompt)
        return lc.invoke(final_prompt)



# 订阅频道
def subscribe_channel(category_chain):
    pubsub = r.pubsub()
    pubsub.subscribe('news_channel')  # 订阅 'test_channel' 频道

    print("Subscribed to 'news_channel'")

    # 监听并处理接收到的消息
    for message in pubsub.listen():
        try: # 防止出现异常导致程序退出
            # print 分割线
            print("=" * 20)
            # 忽略 subscribe 和 unsubscribe 消息
            if message['type'] == 'message':
                news_data = json.loads(message['data'])
                id = news_data['news_id']
                news = news_data['news']
                time_stamp = datetime_to_str(datetime.now())
                print(f"Received news: {news}")
                output = get_category(system_prompt, user_prompt, news, category_chain)
                print(f"分类判断: {check_category(output)}")
                res = branch_runnable(check_category(output), news)
                # ! 恶心  记得下次继续调整

                if res is not None:
                    stocks=convert_str_to_list(res['涉及公司'])
                    # 如果stocks只有一个元素，就不进行新闻更新处理
                    if len(stocks) > 1:
                        news1 = NGroup(
                            stocks=stocks,
                            summary=res['简要分析'],
                            news_time=time_stamp,  # 直接传递字符串
                            tag = id
                        )
                        db.add_news(news1)
                else:
                    print(f"No Action")
        except Exception as e:
            print(f"Error: {e}")
if __name__ == "__main__":
    # 支持基于ds14的tmpchain和基于llm的llm_Qwen14
    # subscribe_channel(tmpchain)
    subscribe_channel(llm_Qwen14)