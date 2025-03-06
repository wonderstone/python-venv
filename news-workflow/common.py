import yaml

# 读取 YAML 配置文件
def read_yaml_config(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


import json
import re

def process_model_output(output: str):
    # 清除多余的标签和文本，如 <think> 或其他额外的描述信息
    cleaned_output = re.sub(r'<[^>]*>', '', output)
    
    # 查找并提取 JSON 格式的部分
    json_match = re.search(r'```json\n([\s\S]*?)\n```', cleaned_output)
    
    if json_match:
        json_str = json_match.group(1)  # 提取 JSON 字符串部分
        try:
            # 尝试解析 JSON
            parsed_data = json.loads(json_str)
            
            # 你可以在这里添加额外的验证步骤，例如检查返回的键是否符合预期
            if '涉及公司' in parsed_data and '简要分析' in parsed_data:
                return parsed_data
            else:
                raise ValueError("JSON structure is invalid.")
        except json.JSONDecodeError:
            raise ValueError("Failed to decode JSON from output.")
    else:
        raise ValueError("No valid JSON found in the output.")


if __name__ == "__main__":
    # 示例用法：
    output_qwen = '''```json
    {
    "涉及公司": "[特斯拉, 比亚迪]",
    "简要分析": "新闻中提到了特斯拉推出面向中低端市场的车型Model Q，并且讨论了其可能与比亚迪在电池技术方面的合作。"
    }
    ```'''

    output_deepseek = '''<think>
    好的，我来分析一下这篇关于Model Q的新闻文本中提到的公司。首先，新闻开头提到了特斯拉是Model Q的制造商，并且讨论了他们的市场策略和定价。接着，在技术亮点部分，文章指出Model Q可能采用比亚迪的电池技术，特别是磷酸铁锂电池。比亚迪作为一家知名的汽车和电池制造公司，在这里被明确提及。

    因此，文中涉及的公司包括特斯拉和比亚迪。特斯拉负责生产Model Q，而比亚迪则在电池技术方面可能与之合作。这些信息清楚地表明了两家公司的存在及其在Model Q项目中的角色。
    </think>

    ```json
    {
    "涉及公司": ["特斯拉", "比亚迪"],
    "简要分析": "文中提到Model Q是特斯拉的车型，并讨论了其市场定位和价格策略，同时提到了可能与比亚迪合作使用其电池技术。"
    }
    ```'''
    # 处理 Qwen 输出
    print(process_model_output(output_qwen))

    # 处理 Deepseek 输出
    print(process_model_output(output_deepseek))
