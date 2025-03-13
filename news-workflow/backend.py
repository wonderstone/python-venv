from flask import Flask, jsonify, request
from backend_funcs import get_models, run_model, run_category, run_processor,match_fuzzy_llm
from common import read_yaml_config



app = Flask(__name__)

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
    
    # 检查请求体中是否包含必要的字段
    if 'Model' not in data or 'Temperature' not in data or 'NumPredict' not in data or 'Prompt' not in data:
        return jsonify({"error": "Missing required fields in request"}), 400
    
    model = data['Model']
    temperature = data['Temperature']
    num_predict = data['NumPredict']
    prompt = data['Prompt']
    
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
    
    # 检查请求体中是否包含必要的字段
    if 'Model' not in data or 'Temperature' not in data or 'NumPredict' not in data or 'News' not in data or 'CategoryList' not in data:
        return jsonify({"error": "Missing required fields in request"}), 400
    
    model = data['Model']
    temperature = data['Temperature']
    num_predict = data['NumPredict']
    news = data['News']
    category_list = data['CategoryList']                            
    ctstr =  category_list.__str__()

    try:
        
        # 读取配置文件
        config = read_yaml_config("/Users/mac/Desktop/python-venv/news-workflow/config.yaml")
        system_prompt = config["prompts"]["system_prompt_classifier_new"]
        user_prompt = config["prompts"]["user_prompt_classifier_new"]
        prompt = system_prompt + user_prompt.format(news, category= ctstr)
        # 调用 run_category 函数运行分类器
        category_response = run_category(model, temperature, num_predict, category_list, prompt)
        return jsonify({"response": category_response.model_dump()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Define a route that do the Summary job
@app.route("/summary", methods=['POST'])
def summary():
    data = request.get_json()
    
    # 检查请求体中是否包含必要的字段
    if 'Model' not in data or 'Temperature' not in data or 'NumPredict' not in data or 'News' not in data:
        return jsonify({"error": "Missing required fields in request"}), 400

    model = data['Model']
    temperature = data['Temperature']
    num_predict = data['NumPredict']
    news = data['News']

    try:
        # 读取配置文件
        config = read_yaml_config("/Users/mac/Desktop/python-venv/news-workflow/config.yaml")
        system_prompt = config["prompts"]["system_prompt_processor"]
        user_prompt = config["prompts"]["user_prompt_processor"]
        prompt = system_prompt + user_prompt.format(news)
        # 调用 run_summary 函数运行摘要,返回摘要结果 dict
        summary_response = run_processor(model, temperature, num_predict, prompt)
        return jsonify(summary_response)
    except Exception as e:
        return jsonify({"error": str(e)}),

# Define a route that runs the fuzzy matching_llm model
@app.route("/matchfuzzyllm", methods=['POST'])
def matchfuzzyllm():
    data = request.get_json()
    
    # 检查请求体中是否包含必要的字段
    if 'Model' not in data or 'Temperature' not in data or 'NumPredict' not in data or 'Abbr' not in data:
        return jsonify({"error": "Missing required fields in request"}), 400
    
    model = data['Model']
    temperature = data['Temperature']
    num_predict = data['NumPredict']

    
    abbreviation = data['Abbr']
    
    try:
        # 读取配置文件
        config = read_yaml_config("/Users/mac/Desktop/python-venv/news-workflow/config.yaml")
        system_prompt_checker = config["prompts"]["system_prompt_checker"]
        user_prompt_checker = config["prompts"]["user_prompt_checker"]
        prompt = system_prompt_checker + user_prompt_checker.format(abbreviation)
        # 调用 match_fuzzy_llm 函数运行模糊匹配
        fuzzy_response = match_fuzzy_llm(model, temperature, num_predict, prompt)
        return jsonify({"response": fuzzy_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 运行 Flask 应用
    # app.run(debug=True)
    app.run()
                                                                                                                                            