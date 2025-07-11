from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
import streamlit as st
from langchain.chains import ConversationalRetrievalChain
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Tongyi
import re
import hashlib
import uuid
from langchain.prompts import PromptTemplate

# Set API Key
os.environ["DASHSCOPE_API_KEY"] = "your_api_key"

# Set up web page
st.title("🧬 蛋白质研究问答助手")
st.write("上传蛋白质研究相关的PDF文献，获取专业解答")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'documents_processed' not in st.session_state:
    st.session_state.documents_processed = False
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'uploaded_files_hash' not in st.session_state:
    st.session_state.uploaded_files_hash = ""
if 'processed_documents' not in st.session_state:
    st.session_state.processed_documents = {}
if 'document_info' not in st.session_state:
    st.session_state.document_info = {}
if 'qa' not in st.session_state:
    st.session_state.qa = None
if 'docsearch' not in st.session_state:
    st.session_state.docsearch = None
if 'input_key' not in st.session_state:
    st.session_state.input_key = str(uuid.uuid4())
if 'show_question_in_input' not in st.session_state:
    st.session_state.show_question_in_input = False
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'new_answer' not in st.session_state: 
    st.session_state.new_answer = None
if 'new_query' not in st.session_state:  
    st.session_state.new_query = None
if 'new_sources' not in st.session_state:
    st.session_state.new_sources = None

# Clear history button
def clear_chat_history():
    st.session_state.chat_history = []
    st.session_state.query = ""
    st.session_state.input_key = str(uuid.uuid4())
    st.session_state.show_question_in_input = False
    st.session_state.new_answer = None
    st.session_state.new_query = None
    st.session_state.new_sources = None
    st.success("问答记录已清除")

# Sidebar function buttons
st.sidebar.title("操作面板")

# Clear chat history button
if st.sidebar.button("🗑️ 清除问答记录"):
    clear_chat_history()

# Common protein research questions
PROTEIN_QUESTIONS = [
    "蛋白质的结构层次有哪些？",
    "简述蛋白质折叠的过程",
    "蛋白质组学的研究方法有哪些？",
    "蛋白质功能预测的主要方法是什么？",
    "蛋白质-蛋白质相互作用的研究技术",
    "蛋白质结构预测的挑战是什么？",
    "蛋白质工程的主要应用领域",
    "解释蛋白质变性和复性的过程",
    "蛋白质定量分析的常用方法",
    "蛋白质纯化技术有哪些？"
]

# Display common questions in sidebar
st.sidebar.divider()
st.sidebar.title("常见蛋白质研究问题")
for i, question in enumerate(PROTEIN_QUESTIONS):
    if st.sidebar.button(question, key=f"q_{i}"):
        st.session_state.query = question
        st.session_state.show_question_in_input = True
        st.session_state.input_key = str(uuid.uuid4())

# Set up multiple PDF file upload
uploaded_files = st.file_uploader("上传蛋白质研究相关的PDF文献", 
                                 type="pdf", 
                                 accept_multiple_files=True)

# Save uploaded files to session_state
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files

def clean_text(text):
    """Clean illegal characters and surrogate pairs from text"""
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)
    try:
        return text.encode('utf-8', 'surrogatepass').decode('utf-8', 'ignore')
    except:
        return text.encode('utf-8', 'ignore').decode('utf-8', 'ignore')

def extract_text_from_pdf(pdf_reader, file_name):
    """Extract text from PDF and add document information"""
    raw_text = ""
    for i, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text:
            raw_text += f"文档[{file_name}] 第{i+1}页: {clean_text(text)}\n\n"
    return raw_text

def get_file_hash(uploaded_files):
    """Generate unique hash value for uploaded files"""
    if not uploaded_files:
        return ""
    
    hasher = hashlib.sha256()
    for file in uploaded_files:
        hasher.update(file.name.encode('utf-8'))
        hasher.update(file.getvalue())
    return hasher.hexdigest()

# Check for new file uploads
current_hash = get_file_hash(st.session_state.uploaded_files)
if current_hash != st.session_state.uploaded_files_hash:
    st.session_state.documents_processed = False
    st.session_state.uploaded_files_hash = current_hash

if st.session_state.uploaded_files and not st.session_state.documents_processed:
    with st.spinner("正在处理蛋白质文献..."):
        try:
            all_texts = []
            document_info = {}
            
            for file_idx, uploaded_file in enumerate(st.session_state.uploaded_files):
                if uploaded_file.name in st.session_state.processed_documents:
                    raw_text = st.session_state.processed_documents[uploaded_file.name]
                else:
                    doc_reader = PdfReader(uploaded_file)
                    raw_text = extract_text_from_pdf(doc_reader, uploaded_file.name)
                    st.session_state.processed_documents[uploaded_file.name] = raw_text
                
                text_splitter = CharacterTextSplitter(
                    separator="\n\n",
                    chunk_size=500,
                    chunk_overlap=100
                )
                texts = text_splitter.split_text(raw_text)
                all_texts.extend(texts)
                
                document_info[file_idx] = {
                    "name": uploaded_file.name,
                    "pages": len(doc_reader.pages) if 'doc_reader' in locals() else "已处理"
                }
            
            EMBEDDING_MODEL = "/share/org/BGI/bgi_wangdt/liuqifan/chatglm/KQA/m3e-base"
            embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            
            docsearch = FAISS.from_texts(all_texts, embeddings)
            st.session_state.docsearch = docsearch
            
            custom_prompt_template = """你是一个专业的蛋白质研究助手，专门回答用户关于上传文献的问题。请根据以下上下文来回答问题。
            如果问题与上下文无关，或者上下文没有提供足够的信息来回答问题，请回答"这个问题与上传的文献无关，我无法回答"。
            即使你知道答案，但如果答案没有在提供的上下文中明确提及，也不要回答。
            请使用专业、准确的语言回答蛋白质研究相关问题。
            
            上下文:
            {context}
            
            问题: {question}
            回答:"""
            
            CUSTOM_QUESTION_PROMPT = PromptTemplate(
                input_variables=["context", "question"], 
                template=custom_prompt_template
            )
            
            st.session_state.qa = ConversationalRetrievalChain.from_llm(
                llm=Tongyi(model_name="qwen-max"),
                retriever=docsearch.as_retriever(
                    search_type="mmr",
                    search_kwargs={"k": 5}
                ),
                return_source_documents=True,
                combine_docs_chain_kwargs={"prompt": CUSTOM_QUESTION_PROMPT}
            )
            
            st.session_state.documents_processed = True
            st.session_state.document_info = document_info
            
            st.success(f"成功处理 {len(st.session_state.uploaded_files)} 个文献!")
            for file_idx, info in document_info.items():
                st.info(f"📄 {info['name']} - {info['pages']}页")
            
        except Exception as e:
            st.error(f"处理文献时出错: {str(e)}")

# If documents are processed, display Q&A interface
if st.session_state.get('documents_processed', False):
    # Display document information
    st.sidebar.divider()
    st.sidebar.subheader("已上传文献")
    for file_idx, info in st.session_state.document_info.items():
        st.sidebar.info(f"📄 {info['name']} ({info['pages']}页)")
    
    # Display chat history
    if st.session_state.chat_history:
        st.subheader("问答历史")
        for i, (query, answer, sources) in enumerate(st.session_state.chat_history):
            st.markdown(f"**问题 {i+1}:** {query}")
            st.markdown(f"**回答 {i+1}:** {answer}")
            
            if sources:
                with st.expander(f"查看来源信息 (问题 {i+1})"):
                    for j, source in enumerate(sources):
                        st.text_area(
                            label=f"来源 {i+1}-{j+1}",
                            value=source, 
                            height=100, 
                            key=f"source_{i}_{j}", 
                            label_visibility="collapsed"
                        )
            
            st.divider()
    
    # Display newly generated Q&A
    if st.session_state.new_query and st.session_state.new_answer:
        st.subheader(f"问题: {st.session_state.new_query}")
        st.subheader("专业解答:")
        st.write(st.session_state.new_answer)
        
        if st.session_state.new_sources:
            with st.expander("查看来源文献"):
                for j, source in enumerate(st.session_state.new_sources):
                    st.text_area(
                        label=f"当前来源 {j+1}", 
                        value=source, 
                        height=100, 
                        label_visibility="collapsed"
                    )
        
        # Add to history
        st.session_state.chat_history.append(
            (st.session_state.new_query, st.session_state.new_answer, st.session_state.new_sources)
        )
        
        # Reset new Q&A state
        st.session_state.new_query = None
        st.session_state.new_answer = None
        st.session_state.new_sources = None
    
    # Get user query
    input_value = st.session_state.query if st.session_state.show_question_in_input else ""
    
    query = st.text_input(
        "输入您关于蛋白质研究的问题", 
        value=input_value,  # Display question based on state
        key=st.session_state.input_key,  # Use unique key
    )
    # Add a generate button
    generate_button = st.button("生成答案")
    
    if (generate_button and query) or (st.session_state.show_question_in_input and query):
        with st.spinner("正在检索文献并生成专业答案..."):
            try:
                # Pass the question and chat history to the conversation chain to get model output
                result = st.session_state.qa({"question": query, "chat_history": st.session_state.chat_history})
                answer = result["answer"]
                source_documents = result['source_documents']
                
                # Extract source information
                source_info = []
                if source_documents:
                    for doc in source_documents[:3]:  # Display up to 3 sources
                        if "文档[" in doc.page_content and "]" in doc.page_content:
                            doc_name = doc.page_content.split("文档[", 1)[1].split("]", 1)[0]
                            page_info = doc.page_content.split("第", 1)[1].split("页", 1)[0] if "第" in doc.page_content else "未知页码"
                            content = doc.page_content.split(":", 1)[1] if ":" in doc.page_content else doc.page_content
                            
                            source_info.append(f"📄 {doc_name} (第{page_info}页): {clean_text(content)[:250]}...")
                        else:
                            source_info.append(clean_text(doc.page_content)[:250] + "...")
                
                # Store new Q&A results
                st.session_state.new_query = query
                st.session_state.new_answer = answer
                st.session_state.new_sources = source_info
                
                # Clear input box
                st.session_state.query = ""
                st.session_state.input_key = str(uuid.uuid4())
                st.session_state.show_question_in_input = False
                
                # Rerun to display new Q&A
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"生成答案时出错: {str(e)}")

# Protein research resources
st.sidebar.divider()
st.sidebar.subheader("蛋白质研究资源")
st.sidebar.markdown("[UniProt 蛋白质数据库](https://www.uniprot.org/)")
st.sidebar.markdown("[PDB 蛋白质结构数据库](https://www.rcsb.org/)")
st.sidebar.markdown("[Protein Data Bank](https://www.wwpdb.org/)")
st.sidebar.markdown("[NCBI 蛋白质资源](https://www.ncbi.nlm.nih.gov/protein)")

# Introduction to protein research
st.sidebar.divider()
st.sidebar.title("蛋白质研究简介")
st.sidebar.write("""
蛋白质是生命活动的主要执行者，参与细胞结构构建、代谢调控、信号传导等关键生物过程。
**主要研究方向**:
- 蛋白质结构预测
- 蛋白质功能注释
- 蛋白质相互作用网络
- 蛋白质工程与设计
- 蛋白质组学分析
""")

# If no documents are uploaded, display prompt
if not st.session_state.uploaded_files:
    st.info("请上传蛋白质研究相关的PDF文献以开始问答")
