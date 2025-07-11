from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS  

def main():
    # Define the path for the embedding model
    EMBEDDING_MODEL = './KQA/m3e-base'

    # Step 1: Load documents
    loader = UnstructuredFileLoader('./KQA/蛋白运输物流信息.txt')
    data = loader.load()
    # print(f'data-->{data}')

    # Step 2: Split documents into chunks
    text_split = RecursiveCharacterTextSplitter(chunk_size=128,
                                                chunk_overlap=4)
    split_data = text_split.split_documents(data)
    # print(f'split_data-->{split_data}')

    # Step 3: Initialize Hugging Face model embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Step 4: Vectorize the split documents and store them
    db = FAISS.from_documents(split_data, embeddings)
    db.save_local('./KQA/faiss/camp')

    return split_data

if __name__ == '__main__':
    split_data = main()
    print(f'split_data-->{split_data}')

