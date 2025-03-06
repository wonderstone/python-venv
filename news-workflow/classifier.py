# Design the classifier class to classify the news articles

# In the classifier.py file, create a Classifier class with the following methods:
# __init__(self, system_prompt, user_prompt, llm)
# get_category(self, news)
# check_category(self, output)
# force_category(self, category)


# The Classifier class should have the following attributes:
# system_prompt: A string representing the system prompt
# user_prompt: A string representing the user prompt
# llm: A language model instance

# The get_category method should take a news article as input and return the predicted category based on the news content. It should use the system_prompt, user_prompt, and llm to generate the final prompt for the language model and invoke it to get the output.

# The check_category method should take the output from the language model and return the predicted category. If the output is an instance of Category, it should return the category content. If the output is an instance of AIMessage, it should return the content. 

# The force_category method should take a category as input and return the forced category. This method can be used to handle cases where the language model output is not one of the predefined categories.

from abc import ABC, abstractmethod
from typing import Any


class Classifier(ABC):
    def __init__(self, system_prompt, user_prompt, runnables):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.runnables = runnables

    @abstractmethod
    def get_category(self, news) -> Any:
        pass


class NewsClassifier(Classifier):
    def __init__(self, system_prompt, user_prompt, runnables):
        super().__init__(system_prompt, user_prompt, runnables)


    def get_category(self, news):
        final_prompt = self.system_prompt + self.user_prompt.format(news)

        return self.runnables.invoke(final_prompt)


if __name__ == "__main__":

    news = "今日收市综评：A股市场震荡走高，沪指涨0.5%，创业板指涨1.2%。"

    from common import read_yaml_config
    # 读取配置文件
    config = read_yaml_config("/Users/mac/Desktop/python-venv/news-workflow/config.yaml")
    system_prompt = config["prompts"]["system_prompt_classifier"]
    user_prompt = config["prompts"]["user_prompt_classifier"]
    
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2:latest", temperature = 0.7, num_predict = 256,)
    llm_Qwen14 = ChatOllama(model="Qwen2.5:14b", temperature = 0.7,num_predict = 1024,)
    llm_ds14  = ChatOllama( model="deepseek-r1:14b",temperature = 0.7,num_predict = 256,)

    from category import Category
    structured_llm = llm_ds14.with_structured_output(Category, method="json_schema")

    classifier = NewsClassifier(system_prompt, user_prompt, structured_llm)
    category = classifier.get_category(news)
    print(category)
    # Output: 收市综评