from flask import Flask, jsonify, request
from backend_funcs import get_models, run_model, get_category_runnable, get_routine_runnable, get_runnable_response
from common import read_yaml_config



app = Flask(__name__)

# 设定全局变量 DEFAULT_MODEL
DEFAULT_MODEL = "Qwen2.5:14b"

MODEL_NAMES = get_models()
# Define a route that returns the models supported by the API
@app.route("/getmodels")
def getmodels():
    try:
        MODEL_NAMES = get_models()
        # 如果MODEL_NAMES为空，则返回提示信息
        if not MODEL_NAMES:
            return jsonify({"error": "No models found"}), 500
        # 返回模型列表
        return jsonify({"models": MODEL_NAMES})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Define a route that runs the llm model
@app.route("/runmodel", methods=['POST'])
def runmodel():
    data = request.get_json()
    
    # 提供默认值
    model = data.get('Model', DEFAULT_MODEL)  # 默认模型名称
    temperature = data.get('Temperature', 0.7)  # 默认温度
    num_predict = data.get('NumPredict', 1024)  # 默认预测数量
    prompt = data.get('Prompt', 'Default prompt')  # 默认提示词

    try:
        # 调用 run_model 函数运行模型
        model_response = run_model(model, temperature, num_predict, prompt)
        return jsonify({"response": model_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Define a route that do the Category job
from common import read_yaml_config

@app.route("/category", methods=['POST'])
def category():
    data = request.get_json()

    # 提供默认值
    model = data.get('Model', "Qwen2.5:14b")  # 默认模型名称
    temperature = data.get('Temperature', 0.7)  # 默认温度
    num_predict = data.get('NumPredict', 1024)  # 默认预测数量
    news = data.get('News')  # 必须提供的字段
    category_list = data.get('CategoryList', ["收市综评", "公司新闻",  "其他"])  # 默认分类列表

    # 检查 News 是否存在
    if not news:
        return jsonify({"error": "Missing required field: 'News'"}), 400

    try:
        # 读取配置文件
        config = read_yaml_config("/Users/mac/Desktop/python-venv/news-workflow/config.yaml")
        system_prompt = config["prompts"]["system_prompt_classifier_new"]
        user_prompt = config["prompts"]["user_prompt_classifier_new"]

        # 获取结构化 LLM
        structured_llm = get_category_runnable(model, temperature, num_predict, category_list)

        # 调用分类器并获取响应
        category_response = get_runnable_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt.format(news, category=category_list.__str__()),
            runnable=structured_llm
        )
        return jsonify(category_response.model_dump())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Define a route that do the Summary job
@app.route("/summary", methods=['POST'])
def summary():
    data = request.get_json()
    
    # 提供默认值
    model = data.get('Model', DEFAULT_MODEL)  # 默认模型名称
    temperature = data.get('Temperature', 0.7)  # 默认温度
    num_predict = data.get('NumPredict', 1024)  # 默认预测数量
    news = data.get('News')  # 必须提供的字段

    # 检查 News 是否存在
    if not news:
        return jsonify({"error": "Missing required field: 'News'"}), 400


    try:
        # 读取配置文件
        config = read_yaml_config("/Users/mac/Desktop/python-venv/news-workflow/config.yaml")
        system_prompt = config["prompts"]["system_prompt_processor"]
        user_prompt = config["prompts"]["user_prompt_processor"]

        # 获取常规 runnable
        user_defined_runnables = get_routine_runnable(model, temperature, num_predict)

        # 调用处理器并获取响应
        summary_response = get_runnable_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt.format(news),
            runnable=user_defined_runnables
        )

        return jsonify({"response": summary_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Define a route that runs the fuzzy matching_llm model
@app.route("/matchfuzzyllm", methods=['POST'])
def matchfuzzyllm():
    data = request.get_json()
    
    # 提供默认值
    model = data.get('Model', DEFAULT_MODEL)  # 默认模型名称
    temperature = data.get('Temperature', 0.7)  # 默认温度
    num_predict = data.get('NumPredict', 1024)  # 默认预测数量
    abbreviation = data.get('Abbr')  # 必须提供的字段

    # 检查 Abbr 是否存在
    if not abbreviation:
        return jsonify({"error": "Missing required field: 'Abbr'"}), 400

    
    try:
        # 读取配置文件
        config = read_yaml_config("/Users/mac/Desktop/python-venv/news-workflow/config.yaml")
        system_prompt = config["prompts"]["system_prompt_checker"]
        user_prompt = config["prompts"]["user_prompt_checker"]

        # 获取模糊匹配 runnable
        fuzzy_llm = get_routine_runnable(model, temperature, num_predict)

        # 调用处理器并获取响应
        match_fuzzy_response = get_runnable_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt.format(abbreviation),
            runnable=fuzzy_llm
        )

        return jsonify({"response": match_fuzzy_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 运行 Flask 应用
    # app.run(debug=True)
    app.run()
                                                                                                                                            