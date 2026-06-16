# Common Issues & Fixes

## Model not found error

Make sure the .gguf file is inside the models/ folder and model_path in model_config.yaml matches exactly.

## HuggingFace token error

Make sure .env file exists in project root (not .env.example) and contains HF_API_TOKEN=your-actual-token

## ChromaDB errors

Delete the vectorstore/chroma_db/ folder and restart the app. It will be recreated automatically.

## streamlit: command not found

Make sure your virtual environment is activated:

Windows: `venv\Scripts\activate`

Mac/Linux: `source venv/bin/activate`

## Port already in use

```bash
streamlit run app.py --server.port 8502
```
