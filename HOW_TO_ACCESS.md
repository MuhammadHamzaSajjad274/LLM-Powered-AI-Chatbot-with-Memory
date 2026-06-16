# How to Open and Check the Chatbot

## 🚀 Quick Start

### Step 1: Start the Streamlit App

Open a terminal/command prompt in the project directory and run:

```bash
streamlit run app.py
```

Or if you're in PowerShell:
```powershell
streamlit run app.py
```

### Step 2: Access the Chatbot

Once the app starts, you'll see output like:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

**Open your web browser and go to:**
- **http://localhost:8501**
- Or **http://127.0.0.1:8501**

### Step 3: Using the Chatbot

1. **Type your message** in the chat input at the bottom
2. **Press Enter** or click send
3. The chatbot will respond using:
   - RAG (Retrieval-Augmented Generation) from past conversations
   - Long-term memory stored in ChromaDB
   - The configured LLM (Local/OpenAI/Deepseek)

### Step 4: Check Features

**Sidebar (left side) shows:**
- ⚙️ **Configuration**: Current LLM type
- 💬 **Conversation**: Clear conversation button
- 📊 **Memory Stats**: 
  - Stored Chunks (from ChromaDB)
  - Current Messages (in this session)
- ℹ️ **About**: Information about the chatbot

## 🔧 Troubleshooting

### If the browser doesn't open automatically:
1. Manually open your browser
2. Type `http://localhost:8501` in the address bar
3. Press Enter

### If you see an error:
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify your LLM configuration in `configs/model_config.yaml`
3. For local LLM: Ensure model path is set or model will download (may take time)
4. For OpenAI/Deepseek: Set API keys as environment variables

### To stop the app:
- Press `Ctrl+C` in the terminal where Streamlit is running

## 📝 Configuration

Before using, check/edit `configs/model_config.yaml`:
- Set LLM type: `local`, `openai`, or `deepseek`
- For API modes, set environment variables:
  ```bash
  # Windows PowerShell
  $env:OPENAI_API_KEY="your-key-here"
  $env:DEEPSEEK_API_KEY="your-key-here"
  ```

## ✅ What to Expect

- **First run**: May take time to load embeddings model and LLM
- **Local LLM**: First time will download model (can be several GB)
- **Subsequent runs**: Faster startup as models are cached

Enjoy chatting with your AI assistant! 🤖


