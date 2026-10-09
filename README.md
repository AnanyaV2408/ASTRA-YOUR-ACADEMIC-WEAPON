# ASTRA — RAG-Based Document Assistant

> **Your knowledge, at your command.**

ASTRA is an intelligent document assistant built using a Retrieval-Augmented Generation (RAG) pipeline. It allows users to upload PDF and TXT documents, ask questions about their contents, retrieve relevant sections, and generate answers grounded in the retrieved context using Google Gemini.

---

## ✨ Features

- Upload multiple PDF and TXT documents
- Manage uploaded documents
- Remove individual documents
- Clear all uploaded documents
- Semantic similarity search
- Retrieval-Augmented Generation (RAG)
- Retrieve the top 3 relevant text chunks
- Gemini-powered answer generation
- Display referenced source documents
- Conversational chat interface
- Handle missing documents and temporary AI service failures
- Aurora-inspired cosmic user interface

---

## 🧠 How ASTRA Works

ASTRA follows a Retrieval-Augmented Generation pipeline:

```text
             DOCUMENT UPLOAD
                   |
                   v
          PDF / TXT EXTRACTION
                   |
                   v
                CHUNKING
                   |
                   v
           EMBEDDING GENERATION
                   |
                   v
          IN-MEMORY VECTOR STORE
                   |
                   |
USER QUERY ------> QUERY EMBEDDING
                          |
                          v
                 SIMILARITY SEARCH
                          |
                          v
                TOP-3 CHUNK RETRIEVAL
                          |
                          v
                 GEMINI + CONTEXT
                          |
                          v
                  GROUNDED ANSWER
                          |
                          v
                  SOURCE REFERENCES
```

---

## 🔬 RAG Pipeline

### 1. Document Processing

Uploaded PDF files are processed using `pypdf`, while TXT files are decoded directly. The extracted text is passed to the chunking stage.

### 2. Chunking

Documents are divided into overlapping text chunks.

Current configuration:

- **Chunk size:** 500 words
- **Overlap:** 100 words

Overlapping chunks help preserve context between neighbouring sections.

### 3. Embedding Generation

Each text chunk is converted into a numerical vector using the `all-MiniLM-L6-v2` embedding model from Sentence Transformers.

The embeddings are normalized before being used for retrieval.

### 4. Similarity Search

When a user asks a question, ASTRA converts the query into an embedding using the same model.

It compares the query embedding against the stored document embeddings using a dot product. Since the embeddings are normalized, this corresponds to cosine similarity.

ASTRA retrieves the **top 3 most relevant chunks**.

### 5. Context-Aware Answer Generation

The retrieved chunks and user query are sent to Google Gemini.

The prompt instructs the model to:

- Answer using only the retrieved document context
- Avoid inventing facts
- Give a clear, direct response
- State when the requested information cannot be found in the retrieved context

This helps keep answers grounded in the uploaded documents.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend / UI | Streamlit |
| PDF Processing | pypdf |
| Text Embeddings | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| Similarity Search | NumPy |
| Large Language Model | Google Gemini |
| Configuration | Streamlit Secrets |

---

## 📁 Project Structure

```text
ASTRA/
├── app.py
├── document_processor.py
├── chunker.py
├── embedder.py
├── retriever.py
├── llm.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml
```

### File Responsibilities

**`app.py`**

The main Streamlit application. Handles the user interface, document management, chat interaction, and RAG pipeline orchestration.

**`document_processor.py`**

Extracts text from PDF and TXT documents.

**`chunker.py`**

Splits extracted text into overlapping chunks.

**`embedder.py`**

Generates normalized semantic embeddings using Sentence Transformers.

**`retriever.py`**

Calculates similarity scores and retrieves the most relevant document chunks.

**`llm.py`**

Sends the user's question and retrieved context to Gemini to generate a grounded answer.

**`requirements.txt`**

Lists the Python dependencies required to run ASTRA.

---

## ⚙️ Installation

### 1. Clone the repository

Replace the placeholder with your actual GitHub repository URL.

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ASTRA
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 API Key Configuration

ASTRA requires a Google Gemini API key.

Create the following file in the project root:

`.streamlit/secrets.toml`

Add your API key:

```toml
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```

Replace the placeholder with your own key.

**Security note:** Never commit your actual API key or `secrets.toml` to GitHub. The root `.gitignore` excludes this file.

---

## ▶️ Running ASTRA

From the project directory, activate your virtual environment and run:

```bash
streamlit run app.py
```

Streamlit will provide a local URL where the application can be opened in a browser.

---

## 💬 Using ASTRA

1. Launch the application.
2. Upload one or more PDF or TXT documents.
3. Wait for document indexing to complete.
4. Navigate to the chat interface.
5. Ask a question about the uploaded content.
6. ASTRA embeds the query and searches the stored document chunks.
7. The top 3 relevant chunks are passed to Gemini as context.
8. ASTRA displays the generated answer and source references.

---

## 🛡️ Error Handling

ASTRA includes handling for common situations.

### No documents uploaded

The application asks the user to upload a document before asking questions.

### Empty or unreadable documents

The application warns the user when a document contains no readable text.

### No relevant information found

ASTRA informs the user when relevant information cannot be found in the retrieved context.

### Temporary Gemini service failure

The application retries generation requests and provides a fallback message if the AI service remains unavailable.

---

## 🚀 Future Improvements

Potential future improvements include:

- Persistent vector database
- Document persistence across application restarts
- Improved chunking strategies
- Metadata-aware retrieval
- Configurable retrieval count
- Page-level source citations
- Streaming responses
- User authentication and private document collections

---

## 🎯 Project Objective

ASTRA demonstrates how Retrieval-Augmented Generation can combine document processing, semantic search, and large language models to build a document question-answering system.

The pipeline combines:

**Document Processing → Chunking → Embeddings → Similarity Search → Context Retrieval → LLM Generation**

The objective is to help users interact with their own documents through a simple interface while grounding generated answers in retrieved information.

---

## 👩‍💻 Built For

**NEXUS Recruitment 2026 — Round 1**

**Statement 2: RAG-Based Document Assistant**