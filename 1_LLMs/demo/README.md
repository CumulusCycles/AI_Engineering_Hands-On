# LLM Demo Notebooks

This folder contains hands-on demonstration notebooks that explore Large Language Models (LLMs) from foundational concepts to practical API usage.

## Overview

These notebooks progress from understanding the internal mechanics of LLMs to working with production-ready APIs:

1. **LLM Pipeline Demo** - Understanding how LLMs process text internally
2. **OpenAI Chat Completions Demo** - Working with OpenAI's cloud-based API
3. **Ollama and OpenAI Demo** - Working with local LLMs and API compatibility

## Notebooks

### 1. LLM Pipeline Demo (`1_LLM_Pipeline_demo.ipynb`)

**Focus**: Internal mechanics of LLM processing

This notebook demonstrates the fundamental pipeline that transforms text into meaningful numerical representations:

- **Text Input** - Starting with raw text
- **Tokenization** - Breaking text into tokens (subword units)
- **Embeddings** - Converting tokens to dense numerical vectors
- **Visualizations** - 2D/3D PCA projections of embedding space
- **Attention Mechanisms** - How transformers focus on relevant tokens
- **Hidden States** - Internal neuron activations
- **Sentiment Analysis** - How models encode different meanings
- **Word Analogies** - Semantic relationships in vector space

**Key Learning Outcomes**:
- Understand how text is converted to numbers
- See how similar texts produce similar embeddings
- Visualize how transformers process language internally
- Explore the relationship between words and their vector representations

### 2. OpenAI Chat Completions Demo (`2_OpenAI_Chat_Completions_demo.ipynb`)

**Focus**: Practical API usage with OpenAI's cloud models

This notebook demonstrates the OpenAI Chat Completions API through progressive examples:

- **Basic Single Message** - Simple API calls
- **System Messages** - Controlling assistant behavior
- **Multi-Turn Conversations** - Context management
- **Model Comparison** - Different model capabilities
- **Parameters** - Temperature, max_tokens
- **Structured Output** - JSON mode for programmatic responses
- **Chain-of-Thought Reasoning** - Step-by-step reasoning for complex problems

**Key Learning Outcomes**:
- Learn the Chat Completions API structure
- Understand roles (system, user, assistant)
- Master conversation context management
- Configure response behavior with parameters
- Get structured, parseable outputs
- Use chain-of-thought prompting for complex reasoning tasks

**Prerequisites**:
- OpenAI API key (set in `.env` file as `OPENAI_API_KEY`)
- API access requires internet connection

### 3. Ollama and OpenAI Demo (`3_Ollama_and_OpenAI_demo.ipynb`)

**Focus**: Local LLM usage and API compatibility

This notebook demonstrates two approaches to running LLMs locally with Ollama:

**Part 1: Native Ollama API**
- Direct Ollama library usage
- Local model interactions
- Privacy and offline capabilities

**Part 2: OpenAI-Compatible API Format**
- Using OpenAI client with Ollama
- Code compatibility between providers
- Switching between local and cloud models

**Key Learning Outcomes**:
- Run LLMs entirely on your machine
- Understand privacy and cost benefits of local models
- Use the same code with different providers
- Compare native vs. compatible API approaches

**Prerequisites**:
- [Ollama installed](https://ollama.ai/download)
- Ollama service running (`ollama serve`)
- Model pulled (e.g., `ollama pull llama3.2:3b`)

## Prerequisites

### Environment Setup

1. **Create a virtual environment** (recommended):
```bash
uv venv --python=python3.12
source .venv/bin/activate
```

2. **Install dependencies**:
```bash
uv pip install -r requirements.txt -q
```

### Additional Setup by Notebook

- **Notebook 1** (LLM Pipeline): No additional setup needed
- **Notebook 2** (OpenAI): Requires `.env` file with `OPENAI_API_KEY=your-key`
- **Notebook 3** (Ollama): Requires Ollama installed and running

## Recommended Learning Path

1. **Start with Notebook 1** - Build foundational understanding of how LLMs work internally
2. **Move to Notebook 2** - Learn practical API usage with OpenAI
3. **Complete with Notebook 3** - Explore local alternatives and API compatibility

## Dependencies

All notebooks require the packages listed in `requirements.txt`:
- `torch` - PyTorch for deep learning operations
- `transformers` - Hugging Face transformers library
- `sentence-transformers` - Embedding models
- `scikit-learn` - Machine learning utilities (PCA)
- `matplotlib` & `seaborn` - Visualization
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- `ollama` - Ollama Python client

## Notes

- **Model Downloads**: First runs of Notebook 1 will download models (DistilBERT, sentence-transformers), which may take time
- **API Costs**: Notebook 2 uses OpenAI's API and incurs costs based on usage
- **Local Resources**: Notebook 3 runs models locally and requires sufficient RAM/GPU for best performance
