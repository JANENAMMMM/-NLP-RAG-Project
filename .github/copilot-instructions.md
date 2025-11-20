# AI Coding Agent Guidelines for RAG Project

Welcome to the RAG (Retrieval Augmented Generation) system codebase. This document provides essential guidelines for AI coding agents to be productive in this project.

## Project Overview

The RAG system integrates multiple components to process academic data and enable efficient retrieval-augmented generation. Key features include:

- **PDF Parsing**: Splitting main text and annexes from Ewha University regulations.
- **Table Data Processing**: Converting CSV data into sentences for vectorization.
- **Vector Store**: Using FAISS with Upstage embeddings for similarity search.
- **RAG Pipeline**: Query-answering with Upstage Solar-pro2 LLM.

## Key Files and Directories

- `RAG_통합_최종.ipynb`: Main notebook for the integrated RAG pipeline.
- `2019_quota.csv`, `degrees.csv`, `contract_dept.csv`: CSV files for structured academic data.
- `degrees/`: Contains historical degree data files.
- `README.md`: High-level project overview and setup instructions.

## Developer Workflows

### Environment Setup
1. Install required libraries:
   ```bash
   pip install langchain_upstage langchain_community langchain-openai openai pdfplumber pandas faiss-cpu
   ```
2. Set the Upstage API key as an environment variable in the notebook:
   ```python
   import os
   os.environ['UPSTAGE_API_KEY'] = '<your-api-key>'
   ```

### Running the Pipeline
- Execute cells in `RAG_통합_최종.ipynb` sequentially.
- Ensure all required CSV files and the `ewha.pdf` file are in place.

### Debugging Tips
- **Windows Path Issues**: FAISS may encounter issues with non-ASCII paths. Use temporary directories for vector DB storage.
- **CSV Formatting**: Ensure CSV files are manually cleaned and formatted before use.

## Project-Specific Conventions

- **Chunking**: Use `RecursiveCharacterTextSplitter` with `chunk_size=1200` and `chunk_overlap=300` for text splitting.
- **Embedding Model**: Default to `Upstage Solar-embedding-1-large`.
- **Top-k Search**: Set `k=5` for similarity-based retrieval.

## Integration Points

- **External Dependencies**:
  - Upstage Solar-pro2 LLM for query-answering.
  - FAISS for vector database management.
- **Cross-Component Communication**:
  - Combine PDF text, annex text, and CSV data into a unified knowledge base.

## Examples

### CSV to Sentence Conversion
Refer to `RAG_표_벡터화.ipynb` for examples of converting CSV rows into sentences for vectorization.

### PDF Parsing
See `RAG_통합_최종.ipynb` for splitting main text and annexes using keyword-based logic.

---

For further details, consult the `README.md` or the respective notebooks. Reach out to contributors for specific questions.