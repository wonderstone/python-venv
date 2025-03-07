import re


# 目标字典，key为上市公司缩写，value为上市代码
# 给出示例，未来可以外部引用或者从数据库中读取

dict_interested = {
    "蜜雪集团": "02097.HK",
    "*ST目标": "600000.SH",
    "ABC": "600000.SH",
    "ST公司": "600000.HK",
    "公司名称": "600000.SH"
}



def extract_abbreviation_and_code(input_str):
    # 正则表达式：匹配公司缩写和上市代码
    # 这部分可以匹配公司缩写和附带的上市代码，包含括号和方括号

    pattern_with_abbr = r'([A-Za-z0-9*]*[\u4e00-\u9fa5]+|[A-Za-z0-9*]+)(?:\[(\d{3,6}[\.A-Za-z]*)\]|\((\d{3,6}[\.A-Za-z]*)\)|(\d{3,6}[\.A-Za-z]*))?'
    # 先尝试匹配包含公司缩写和上市代码的情况
    match_with_abbr = re.match(pattern_with_abbr, input_str)
    if match_with_abbr:
        abbreviation = match_with_abbr.group(1)  # 公司缩写
        stock_code = match_with_abbr.group(2) or match_with_abbr.group(3) or match_with_abbr.group(4)  # 上市代码
        return abbreviation, stock_code

    # 如果都没有匹配到，返回None
    return None, None

# ~ 1. 精确匹配公司缩写, input: abbreviation, code, output: bool
def match_precise(abbreviation, code):
    # 从字典中查找公司缩写对应的上市代码
    if abbreviation in dict_interested:
        # 如果找到了对应的上市代码
        return True
        # 更精确的匹配逻辑
        # if code == dict_interested[abbreviation]:
        #     return True
    return False

# ~ 2. 模糊匹配：大模型判断是否为A股上市公司, input: abbreviation, system_prompt, user_prompt, runnables.
def match_fuzzy_llm(abbreviation, system_prompt, user_prompt, runnables):
    final_prompt = system_prompt + user_prompt.format(abbreviation)
    # 这里调用大模型判断是否为A股上市公司
    return runnables.invoke(final_prompt)

# ~ 3. 模糊匹配：相似度匹配，使用chroma





if __name__ == "__main__":
    # 测试用例
    test_cases = [
            "蜜雪集团"               # 只有公司名称
            "蜜雪集团(02097.HK)",   # 含有括号的上市代码
            "*ST目标[600000.SH]",    # 含有特殊字符和方括号的上市代码
            "ABC1234(600000.SH)",    # 公司缩写后跟圆括号和代码
            "ABC*123[600000.SH]",    # 混合字符和方括号
            "ST公司(600000.HK)",     # 含有ST和代码
            "公司名称600000.SH" ,     # 没有括号和其他字符的普通格式
            "公司名称(600000.SH)",    # 括号和代码
            "公司名称[600000]",    # 方括号和代码
    ]
    # 执行匹配
    for input_str in test_cases:
        abbreviation, stock_code = extract_abbreviation_and_code(input_str)
        print(f"输入: {input_str} => 公司缩写: {abbreviation}, 上市代码: {stock_code}")
    
    from common import read_yaml_config

    config = read_yaml_config("/Users/mac/Desktop/python-venv/news-workflow/config.yaml")
    system_prompt_checker = config["prompts"]["system_prompt_checker"]
    user_prompt_checker = config["prompts"]["user_prompt_checker"]

    from langchain_ollama import ChatOllama
    llm_Jade = ChatOllama(model="Jade-ArliAI-Qwen2.5:latest", temperature = 0.7, num_predict = 1024,) # 32B model 35s
    llm_Qwen14 = ChatOllama(model="Qwen2.5:14b", temperature = 0.7,num_predict = 1024,) # 14B model 5s
    llm_ds14  = ChatOllama( model="deepseek-r1:14b",temperature = 0.7,num_predict = 1024,) # 14B model 12s

    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.runnables import RunnableParallel, RunnableLambda

    user_defined_runnables =  llm_Qwen14 | RunnableParallel({
        "JOutput": JsonOutputParser(),
        "Duration": RunnableLambda(lambda output: output.response_metadata['total_duration']/1e9)
    })

    # 测试用例
    test_cases = [
        "蜜雪集团", "浦发银行(600000.SH)", "*ST目标", 
    ]
    # 执行匹配  

    for input_str in test_cases:
        abbreviation, stock_code = extract_abbreviation_and_code(input_str)
        print(f"输入: {input_str} => 公司缩写: {abbreviation}, 上市代码: {stock_code}")
        if match_precise(abbreviation, stock_code):
            print(f"精确匹配: {abbreviation} => {dict_interested[abbreviation]}")
        else:
            print(f"精确匹配: {abbreviation} => 未匹配")
            print(f"模糊匹配: {abbreviation} => {match_fuzzy_llm(abbreviation, system_prompt_checker, user_prompt_checker, user_defined_runnables)}")