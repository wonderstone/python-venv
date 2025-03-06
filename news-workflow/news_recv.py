import redis
from classifier import NewsClassifier
from processor import NewsProcessor
from common import read_yaml_config
from langchain_ollama import ChatOllama
from category import Category

# 读取配置文件
config = read_yaml_config("/Users/mac/Desktop/python-venv/news-workflow/config.yaml")
system_prompt = config["prompts"]["system_prompt_classifier"]
user_prompt = config["prompts"]["user_prompt_classifier"]


def get_structured_llm(model, category):
    if model == 'Qwen14':
        llm = ChatOllama(model="Qwen2.5:14b", temperature = 0.7,num_predict = 1024,)
    elif model == 'ds14':
        llm = ChatOllama( model="deepseek-r1:14b",temperature = 0.7,num_predict = 256,)
    else:
        # 打印提示，返回默认Qwen14
        print("Invalid model. Only 'Qwen14' and 'ds14' are supported. Using 'Qwen14' as default.")
        llm = ChatOllama(model="Qwen2.5:14b", temperature = 0.7,num_predict = 1024,)
    return llm.with_structured_output(category, method="json_schema")


def get_classifier(system_prompt, user_prompt, model):
    structured_llm = get_structured_llm(model, Category)
    return NewsClassifier(system_prompt, user_prompt, structured_llm)






# category = classifier.get_category(news)

# 连接到 Redis 服务器
r = redis.Redis(host='localhost', port=6379, db=0)


# 订阅频道
def subscribe_channel(classifier: NewsClassifier , processor: NewsProcessor, channel = 'news_channel', ):
    pubsub = r.pubsub()
    pubsub.subscribe(channel)  # 订阅 'news_channel' 频道

    print("Subscribed to channel:", channel)

    # 监听并处理接收到的消息
    for message in pubsub.listen():
        try: # 防止出现异常导致程序退出
            # print 分割线
            print("=" * 20)

            # 接收到的消息
            news = message['data'].decode('utf-8')
            print(f"Received news: {news}")

            # 获取类别
            category = classifier.get_category(news)
    
            print(f"Predicted category: {category}")

            # 强制类别
            category = force_category(category)
            print(f"Forced category: {category}")

            # 分支运行
            branch_runnable(category, news)

        except Exception as e:
            print(f"Error: {e}")