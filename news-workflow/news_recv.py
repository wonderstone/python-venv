import redis
from classifier import NewsClassifier
from processor import NewsProcessor
from common import read_yaml_config
from langchain_ollama import ChatOllama
from category import Category
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda
# 读取配置文件
config = read_yaml_config("/Users/mac/Desktop/python-venv/news-workflow/config.yaml")
system_prompt_classifier = config["prompts"]["system_prompt_classifier"]
user_prompt_classifier = config["prompts"]["user_prompt_classifier"]
system_prompt_processor = config["prompts"]["system_prompt_processor"]
user_prompt_processor = config["prompts"]["user_prompt_processor"]
# 连接到 Redis 服务器
r = redis.Redis(host='localhost', port=6379, db=0)

# ~ 1. For classifier
def get_structured_llm(model, category):
    if model == 'Qwen14':
        llm = ChatOllama(model="Qwen2.5:14b", temperature = 0.7,num_predict = 1024,)
    elif model == 'ds14':
        llm = ChatOllama( model="deepseek-r1:14b",temperature = 0.7,num_predict = 1024,)
    else:
        # 打印提示，返回默认Qwen14
        print("Invalid model. Only 'Qwen14' and 'ds14' are supported. Using 'Qwen14' as default.")
        llm = ChatOllama(model="Qwen2.5:14b", temperature = 0.7,num_predict = 1024,)
    return llm.with_structured_output(category, method="json_schema")


def get_classifier(system_prompt, user_prompt, model):
    structured_llm = get_structured_llm(model, Category)
    return NewsClassifier(system_prompt, user_prompt, structured_llm)

# ~ 2. For processor
def get_llm(model):
    if model == 'Qwen14':
        llm = ChatOllama(model="Qwen2.5:14b", temperature = 0.7,num_predict = 1024,)
    elif model == 'ds14':
        llm = ChatOllama( model="deepseek-r1:14b",temperature = 0.7,num_predict = 256,)
    else:
        # 打印提示，返回默认Qwen14
        print("Invalid model. Only 'Qwen14' and 'ds14' are supported. Using 'Qwen14' as default.")
        llm = ChatOllama(model="Qwen2.5:14b", temperature = 0.7,num_predict = 1024,)
    return llm

def get_processor(system_prompt, user_prompt, runnables):
    user_defined_runnables =  runnables | RunnableParallel({
        "JOutput": JsonOutputParser(),
        "Duration": RunnableLambda(lambda output: output.response_metadata['total_duration']/1e9)
    })
    return NewsProcessor(system_prompt, user_prompt, user_defined_runnables)


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
            if message['type'] == 'message':
                # 接收到的消息
                news = message['data'].decode('utf-8')
                print(f"Received news: {news}")

                # 获取类别
                category = classifier.get_category(news)
                print(f"Predicted category: {category.Category}")
                
                # 分支运行
                if category.Category == '公司新闻':
                    res = processor.process(news)
                    print(res)

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # 获取分类器
    classifier = get_classifier(system_prompt_classifier, user_prompt_classifier, 'Qwen14')

    # 获取处理器
    processor = get_processor(system_prompt_processor, user_prompt_processor, get_llm('ds14'))

    # 订阅频道
    subscribe_channel(classifier, processor)