# coding:utf-8
# Import required packages
from langchain.prompts import PromptTemplate
from get_vector import *
from model import ChatGLM2

# Load FAISS vector database
EMBEDDING_MODEL = './KQA/m3e-base'
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
db = FAISS.load_local('./KQA/faiss/camp', embeddings,allow_dangerous_deserialization=True)


def get_related_content(related_docs):
    related_content = []
    for doc in related_docs:
        related_content.append(doc.page_content.replace('\n\n', '\n'))
    return '\n'.join(related_content)

def define_prompt():
    question = '我要的蛋白当前存放地点是哪里，有多少瓶，从哪个城市出发，采用什么方式运输，预计何时到达重庆实验室，运输过程采用什么温控方式'
    docs = db.similarity_search(question, k=1)
    # print(f'docs-->{docs}')
    related_docs = get_related_content(docs)

    # Build the prompt template
    PROMPT_TEMPLATE = """
           基于以下已知信息，简洁和专业的来回答用户的问题。不允许在答案中添加编造成分。
           已知内容:
           {context}
           问题:
           {question}"""
    prompt = PromptTemplate(input_variables=["context", "question"],
                            template=PROMPT_TEMPLATE)

    my_prompt = prompt.format(context=related_docs,
                                question=question)
    return my_prompt

def qa():
    llm = ChatGLM2()
    llm.load_model(model_path='./chatglm-6b')
    my_prompt = define_prompt()
    result = llm.invoke(my_prompt)
    return result

if __name__ == '__main__':
    result = qa()
    print(f'result-->{result}')
    

