import yaml

# 读取 YAML 配置文件
def read_yaml_config(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config

import ast


# 整理为函数

def convert_str_to_list(str_list):
    # 如果输入为空字符串，或者<无>
    if not str_list or str_list == "<无>":
        return []
    # 如果是若干个空格，返回空列表
    if str_list.isspace():    
        return []


    
    # 去除字符串中的额外的双引号
    str_list = str_list.replace('"', '')

    # 将每个元素加上引号（注意可能存在空格，需要处理）
    print(str_list)
    str_list_with_quotes = '[' + ', '.join(f'"{item.strip()}"' for item in str_list.strip('[]').split(',')) + ']'
    # 使用 ast.literal_eval() 将修改后的字符串转化为列表
    return ast.literal_eval(str_list_with_quotes)

def test_convert_str_to_list():

    # Test with a normal string list
    assert convert_str_to_list('["股票1", "股票2", "股票3"]') == ["股票1", "股票2", "股票3"]

    # Test with an empty string
    assert convert_str_to_list('') == []

    # Test with a string containing only spaces
    assert convert_str_to_list('   ') == []

    # Test with a string containing "<无>"
    assert convert_str_to_list('<无>') == []

    # Test with a string containing extra double quotes
    assert convert_str_to_list('["股票1", "股票2", "股票3"]') == ["股票1", "股票2", "股票3"]

    # Test with a string containing spaces between elements
    assert convert_str_to_list('[" 股票1 ", " 股票2 ", " 股票3 "]') == ["股票1", "股票2", "股票3"]

    # Test with a string containing mixed spaces and elements
    assert convert_str_to_list('[ "股票1" , "股票2" , "股票3" ]') == ["股票1", "股票2", "股票3"]



# 测试
if __name__ == "__main__":
    test_convert_str_to_list()