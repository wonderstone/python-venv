import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 加载BERT模型和tokenizer（使用中文BERT）
model_name = "bert-base-chinese"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

# 将文本转化为BERT输入格式并获取其向量表示
def get_bert_embedding(text):
    # Tokenize the text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    
    # Get the embeddings from BERT
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 获取[CLS]标记的嵌入（通常表示整个句子的语义）
    embeddings = outputs.last_hidden_state[:, 0, :].numpy()
    return embeddings

# 计算句子之间的相似度
def get_sentence_similarity(sentence1, sentence2):
    emb1 = get_bert_embedding(sentence1)
    emb2 = get_bert_embedding(sentence2)
    return cosine_similarity(emb1, emb2)[0][0]

# 定义model_output和目标标签
model_output = "公司分析"
target_labels = ["公司新闻", "收盘综评", "其他"]

# 计算model_output与每个目标标签的相似度
for label in target_labels:
    similarity = get_sentence_similarity(model_output, label)
    print(f"Similarity between '{model_output}' and '{label}': {similarity:.4f}")