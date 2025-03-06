from abc import ABC, abstractmethod
from typing import Any


class Processor(ABC):
    def __init__(self, system_prompt, user_prompt, runnables):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.runnables = runnables

    @abstractmethod
    def process(self, news) -> Any:
        pass


class NewsProcessor(Processor):
    def __init__(self, system_prompt, user_prompt, runnables):
        super().__init__(system_prompt, user_prompt, runnables)

    def process(self, news):
        final_prompt = self.system_prompt + self.user_prompt.format(news)
        return self.runnables.invoke(final_prompt)



if __name__ == "__main__":

    news ="""
Model Q的定位与市场策略
Model Q是特斯拉首款面向中低端市场的车型，预计2025年上半年正式上市。其海外售价将低于3万美元，而在中国市场，补贴后价格有望下探至14万元人民币左右。这一价格策略直接对标比亚迪海豚、大众ID.3等热门车型，旨在吸引预算有限的年轻消费者。
特斯拉的这一举措不仅是为了应对国产品牌的竞争，更是为了扩大市场份额。通过推出入门级车型，特斯拉希望进一步拉近与中低端消费群体的距离，同时巩固其在全球电动车市场的领先地位。
技术亮点：比亚迪电池的潜在合作
Model Q的技术亮点之一是其动力系统。据悉，Model Q将提供两种电池版本：低配版搭载磷酸铁锂电池，高配版则可能采用三元锂电池。磷酸铁锂电池以其成本低、安全性高的特点，成为入门级电动车的理想选择。
更有消息称，特斯拉可能与比亚迪合作，采用其电池技术。比亚迪作为全球领先的电池制造商，其磷酸铁锂电池在性能和成本上具有显著优势。如果合作成真，Model Q的制造成本将进一步降低，售价也可能更具竞争力。
"""

    from common import read_yaml_config
    # 读取配置文件
    config = read_yaml_config("/Users/mac/Desktop/python-venv/news-workflow/config.yaml")
    system_prompt = config["prompts"]["system_prompt_processor"]
    user_prompt = config["prompts"]["user_prompt_processor"]

    from langchain_ollama import ChatOllama
    llm_Jade = ChatOllama(model="Jade-ArliAI-Qwen2.5:latest", temperature = 0.7, num_predict = 256,) # 32B model 35s
    llm_Qwen14 = ChatOllama(model="Qwen2.5:14b", temperature = 0.7,num_predict = 1024,) # 14B model 5s
    llm_ds14  = ChatOllama( model="deepseek-r1:14b",temperature = 0.7,num_predict = 256,) # 14B model 12s

    # print(llm_Qwen14.invoke(news))
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.runnables import RunnableParallel, RunnableLambda

    # 获取llm返回的response_metadata中的total_duration字段信息
    # https://github.com/ollama/ollama/blob/main/docs/api.md
    def get_duration(output):
        return output.response_metadata['total_duration']/1e9

    lc = llm_Qwen14 | RunnableParallel({
        "JOutput": JsonOutputParser(),
        "Duration": RunnableLambda(get_duration)
    })

    # lc = llm_Qwen14|JsonOutputParser()

    npsor = NewsProcessor(system_prompt, user_prompt, lc)
    res = npsor.process(news)
    print(res)
    # Output: 收市综评