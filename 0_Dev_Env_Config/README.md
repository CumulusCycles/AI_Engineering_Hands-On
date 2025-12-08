# Dev Enviroment Config
Content for [Dev Environment Config](https://youtu.be/36sbUO2LaOk) video.

*Note*: Please follow the [Intro](https://youtu.be/HaXveXkSwlQ) video to install required software if you haven't done so already.

## Create Viurtual Environment
```bash
cd YOUR_PROJECT_DIR

uv venv --python python3.12
source .venv/bin/activate
```

## Install Libraries / Dependencies
1. Create `requirements.txt` file
```python
jupyterlab
ollama
openai
python-dotenv
``` 

2. Install Dependencies
```bash
uv pip install -r requirements.txt
```

## Add OpenAI API Key to `.env`

1. Create a `.env` file with your OpenAPI API Key
```txt
OPENAI_API_KEY=replace-with-your-actual-api-key
```
**IMPORTANT**: Be sure `.env` is in your `.gitignore` file before pushing to GitHub!

## Run Notebooks

### OpenAI Demo
```bash
uv run --with jupyter jupyter lab ./openai_demo.ipynb
```

### Ollama Demo
```bash
uv run --with jupyter jupyter lab ./ollama_demo.ipynb
```

## Deactivate Virtual Env
```bash
deactivate
```