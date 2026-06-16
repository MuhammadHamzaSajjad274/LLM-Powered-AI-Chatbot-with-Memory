#!/bin/bash

# Simple script to set environment variables and run the Streamlit app

# Set API keys (uncomment and set your keys if using OpenAI or Deepseek)
# export OPENAI_API_KEY="your-openai-api-key-here"
# export DEEPSEEK_API_KEY="your-deepseek-api-key-here"

# Run the Streamlit app
streamlit run app.py --server.port 8501 --server.address localhost


