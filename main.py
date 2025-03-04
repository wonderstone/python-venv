import yaml

# # 读取 YAML 配置文件
# def read_yaml_config(file_path):
#     with open(file_path, "r", encoding="utf-8") as f:
#         config = yaml.safe_load(f)
#     return config

# # 获取配置并替换占位符
# def get_prompt(config, info):
#     tmp_prompt = config["prompts"]["tmp_prompt"]
#     return tmp_prompt.format(info)

# # 使用配置
# config = read_yaml_config("config.yaml")

# # 假设 info 是需要替换的实际信息
# info = "这是待分析的新闻内容，包含需要分类的关键字和描述。"

# # 获取最终的提示语句
# final_prompt = get_prompt(config, info)

# # 输出最终的提示内容
# print(final_prompt)

import ast

import ast

# 原始字符串，没有引号
str_list = '[特斯拉, 比亚迪, 大众]'

# 将每个元素加上引号（注意可能存在空格，需要处理）
str_list_with_quotes = '[' + ', '.join(f'"{item.strip()}"' for item in str_list.strip('[]').split(',')) + ']'

# 使用 ast.literal_eval() 将修改后的字符串转化为列表
converted_list = ast.literal_eval(str_list_with_quotes)


# 整理为函数

def convert_str_to_list(str_list):
    # 将每个元素加上引号（注意可能存在空格，需要处理）
    str_list_with_quotes = '[' + ', '.join(f'"{item.strip()}"' for item in str_list.strip('[]').split(',')) + ']'
    # 使用 ast.literal_eval() 将修改后的字符串转化为列表
    return ast.literal_eval(str_list_with_quotes)


# 打印结果
print(converted_list)