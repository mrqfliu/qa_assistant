# 🧬 Protein Research Document QA System

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue" alt="Python">
  <img src="https://img.shields.io/badge/Model-ChatGLM6B|Qwen-green" alt="Models">
  <img src="https://img.shields.io/badge/RAG-Enabled-success" alt="RAG">
  <img src="https://img.shields.io/badge/Privacy-Offline-critical" alt="Privacy">
</div>

## 📌 Project Overview

An intelligent document QA system specifically designed for protein research, combining local large models (ChatGLM-6B) and cloud API models (Tongyi Qianwen). Core features:

- 🔒 **Fully offline operation** - Sensitive data never leaves the local environment
- 🤖 **Dual-model engine** - Seamless switching between local and cloud models
- 🧠 **Intelligent RAG architecture** - Retrieval-Augmented Generation based on protein documents
- 📚 **Multi-document support** - Process multiple research papers simultaneously
- 🔍 **Answer traceability** - Provide answer sources and reference locations

## ✨ Core Features

### 🔒 Offline Private Deployment
- Local models handle sensitive data without internet connection
- Full local processing pipeline: document parsing, vectorization, QA
- Zero data transmission risk, compliant with enterprise security standards

### 🤖 Multi-Model Support
| Model Type | Model Name | Use Case | Features |
|------------|------------|----------|----------|
| 🖥️ Local Model | ChatGLM-6B | Sensitive data/Offline environment | No data leakage |
| ☁️ Web API | Tongyi Qianwen | Complex problem solving | Stronger reasoning |
| 🔍 Embedding Model | M3E-base | Text vectorization | Chinese optimized, efficient retrieval |

### 📚 Local Knowledge Base QA
1. **Document Processing**:
   - PDF text extraction and cleaning
   - Intelligent chunking
   - Metadata extraction (file name, page number)
 
2. **Knowledge Building**:
   - FAISS vector index construction
   - Text embeddings with M3E model
   - Dynamic knowledge base updates

3. **Intelligent QA**:
   - Professional protein research Q&A
   - Strict prompt constraints to prevent hallucinations
   - Source annotation (document + page number)

### 📝 Conversation Management
- Complete conversation history
- One-click clear history
- Expandable/collapsible answer sources

## ⚙️ Installation Guide

### 1. Create Conda Environment
```bash
conda create -n protein-qa python=3.10
conda activate protein-qa
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

For Chinese users, use Tsinghua mirror:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. Download Models
#### M3E Embedding Model
```bash
git lfs install
git clone https://huggingface.co/moka-ai/m3e-base
```

#### ChatGLM-6B Local Model
```bash
git lfs install
git clone https://huggingface.co/THUDM/chatglm-6b
```

## 🚀 Quick Start

### 1. Configure Environment
#### Tongyi Qianwen API Key (Required for API mode)
DASHSCOPE_API_KEY=your_api_key_here

#### Local Model Path
model_path=./models/chatglm-6b

### 2. Launch Web Application
```bash
streamlit run protein_qa_assistant.py
```

## ⚠️ Important Notes

1. **Hardware Requirements**:
   - Local mode: ≥16GB RAM (32GB recommended)
   - GPU acceleration: CUDA 11+ required
   - Disk space: Reserve ≥20GB (including models)

2. **Document Limitations**:
   - Local mode supports TXT/PDF, API mode supports PDF
   - Recommended ≤50 pages/document
   - Compatible with Chinese/English documents

3. **First-time Usage**:
   - Local model loading takes several minutes
   - Knowledge base build time proportional to document size
   - Start with small documents for testing

## ❓ Frequently Asked Questions

**Q: How is research data security guaranteed?**
A: Local mode processes all data on-device with no storage/transmission. API mode only sends question text and processed text fragments, meeting enterprise security standards.

**Q: How to prevent model hallucination?**
A: Strict prompt constraint: "Answer strictly based on provided documents only."

**Q: What document formats are supported?**
A: Currently supports PDF research papers and technical documents.

## 📜 License

[MIT License](LICENSE) - Free for academic and commercial use

---

**Research Tip**: Add protein database links (UniProt, PDB, RCSB) in the sidebar for quick access! 🧪🔬
```
