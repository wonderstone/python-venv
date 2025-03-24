import subprocess
from langchain_core.messages import SystemMessage, HumanMessage

# ~ Refactor Section:
#% 00A. Func to get the llm based on ollama
def get_llm(model, temperature, num_predict):
    try:
        llm = ChatOllama(model=model, temperature=temperature, num_predict=num_predict)
        return llm
    except Exception as e:
        print(f"Error: {e}")
        return None
    
#% 00B. Func to get the runnable's response
def get_runnable_response(runnable, **kwargs):
    """
    A flexible function to invoke a runnable with different types of inputs.
    Supports both system/user messages and direct prompts.
    
    Args:
        runnable: The runnable object to invoke.
        **kwargs: Arbitrary keyword arguments, such as:
            - system_prompt: The system message content.
            - user_prompt: The user message content.
            - prompt: A direct prompt string.
    
    Returns:
        The response from the runnable invocation.
    """
    try:
        # Check if system_prompt and user_prompt are provided
        if "system_prompt" in kwargs and "user_prompt" in kwargs:
            system_message = SystemMessage(content=kwargs["system_prompt"])
            user_message = HumanMessage(content=kwargs["user_prompt"])
            return runnable.invoke([system_message, user_message])
        
        # Check if a direct prompt is provided
        elif "prompt" in kwargs:
            return runnable.invoke(kwargs["prompt"])
        
        else:
            raise ValueError("Invalid arguments: Provide either 'system_prompt' and 'user_prompt', or 'prompt'.")
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
# ~ Func 1
# Define a func to get models supported by the API
def get_models():
    result = subprocess.run(["ollama", "ls"], capture_output=True, text=True, check=True)
    models_output = result.stdout

    # 解析输出，提取 NAME 列数据
    lines = models_output.split('\n')
    names = []
    for line in lines[1:]:  # 跳过标题行
        if line.strip():  # 跳过空行
            name = line.split()[0]  # 提取 NAME 列
            names.append(name)
    return names


# ~ Func 2
from langchain_ollama import ChatOllama

def run_model(model, temperature, num_predict, prompt):
    llm = ChatOllama(model=model, temperature=temperature, num_predict=num_predict)
    return llm.invoke(prompt).model_dump()


# ~ Func 3
# Define a func to do the Category job
from category_new import CategoryFactory
# refactored version:
# func to get custom llm for category
def get_category_runnable(model, temperature, num_predict, category_list):
    llm = ChatOllama(model=model, temperature=temperature, num_predict=num_predict)
    return llm.with_structured_output(CategoryFactory(category_list).create_category_model(), method="json_schema")

# ~ Func 4
# Define a func to do the Processor job
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda
from processor import NewsProcessor

def get_routine_runnable(model, temperature, num_predict):
    llm = ChatOllama(model=model, temperature=temperature, num_predict=num_predict)
    user_defined_runnables =  llm | RunnableParallel({
        "Output": JsonOutputParser(),
        "Duration": RunnableLambda(lambda output: output.response_metadata['total_duration']/1e9)
    })
    return user_defined_runnables


if __name__ == "__main__":
    # 获取支持的模型列表
    MODEL_NAMES = get_models()
    print("Supported models:", MODEL_NAMES)

    # 示例：运行模型
    model = "Qwen2.5:14b"
    temperature = 0.7
    num_predict = 1024
    prompt = "我很高兴认识你。"
    print(run_model(model, temperature, num_predict, prompt))

    # -1. 示例：运行分类器
    model = "Qwen2.5:14b"
    temperature = 0.7
    num_predict = 1024
    category_list = ["收市综评", "公司新闻",  "国际新闻", "其他"]
    ctstr =  category_list.__str__()
    news = "今日收市综评：A股市场震荡走高，沪指涨0.5%，创业板指涨1.2%。"

    from common import read_yaml_config
    # 读取配置文件
    config = read_yaml_config("/Users/mac/Desktop/python-venv/news-workflow/config.yaml")
    # * 提示词 system , user 分类
    system_prompt = config["prompts"]["system_prompt_classifier_new"]
    user_prompt = config["prompts"]["user_prompt_classifier_new"]
    # * 提示词 prompt 拼接后 分类
    prompt = system_prompt + user_prompt.format(news, category= ctstr)

    # 获得结构化llm
    structured_llm = get_category_runnable(model, temperature, num_predict, category_list)
    # 两种调用支持
    print(get_runnable_response(system_prompt=system_prompt, user_prompt=user_prompt.format(news, category= ctstr), runnable=structured_llm))
    print(get_runnable_response(prompt=prompt, runnable=structured_llm))


    # -2. 示例：运行常规处理器
    model = "Qwen2.5:14b"
    temperature = 0.7
    num_predict = 1024
    news ="""
Model Q的定位与市场策略
Model Q是特斯拉首款面向中低端市场的车型，预计2025年上半年正式上市。其海外售价将低于3万美元，而在中国市场，补贴后价格有望下探至14万元人民币左右。这一价格策略直接对标比亚迪海豚、大众ID.3等热门车型，旨在吸引预算有限的年轻消费者。
特斯拉的这一举措不仅是为了应对国产品牌的竞争，更是为了扩大市场份额。通过推出入门级车型，特斯拉希望进一步拉近与中低端消费群体的距离，同时巩固其在全球电动车市场的领先地位。
技术亮点：比亚迪电池的潜在合作
Model Q的技术亮点之一是其动力系统。据悉，Model Q将提供两种电池版本：低配版搭载磷酸铁锂电池，高配版则可能采用三元锂电池。磷酸铁锂电池以其成本低、安全性高的特点，成为入门级电动车的理想选择。
更有消息称，特斯拉可能与比亚迪合作，采用其电池技术。比亚迪作为全球领先的电池制造商，其磷酸铁锂电池在性能和成本上具有显著优势。如果合作成真，Model Q的制造成本将进一步降低，售价也可能更具竞争力。
"""
    system_prompt = config["prompts"]["system_prompt_processor"]
    user_prompt = config["prompts"]["user_prompt_processor"]
    prompt = system_prompt + user_prompt.format(news)

    # 获得常规runnable
    user_defined_runnables = get_routine_runnable(model, temperature, num_predict)
    # 调用
    print(get_runnable_response(system_prompt=system_prompt, user_prompt=user_prompt.format(news), runnable=user_defined_runnables))
    print(get_runnable_response(prompt=prompt, runnable=user_defined_runnables))


    # -3. 示例：运行模糊匹配
    model = "Qwen2.5:14b"
    temperature = 0.7
    num_predict = 1024
    abbreviation = "浦发银行"
    system_prompt_checker = config["prompts"]["system_prompt_checker"]
    user_prompt_checker = config["prompts"]["user_prompt_checker"]
    prompt = system_prompt_checker + user_prompt_checker.format(abbreviation)


    print(get_runnable_response(system_prompt=system_prompt_checker, user_prompt=user_prompt_checker.format(abbreviation), runnable=user_defined_runnables))
    print(get_runnable_response(prompt=prompt, runnable=user_defined_runnables))