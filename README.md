# Granite 3.3-2B Instruct — Pipeline Streamlit Chatbot (4-bit optional)

This repo contains a Streamlit chatbot using the **pipeline()** method from `transformers`
to load **ibm-granite/granite-3.3-2b-instruct** locally. It also includes:
- Warm Beige Notebook UI theme (beautiful, cozy design)
- 4-bit quantization support (optional, using bitsandbytes) to speed up model loading on CPU/GPU
- Calculators: EMI, SIP future value, Savings goal, Tax estimator
- Glossary (RAG-lite)
- Explain Like I'm 5 (ELI5) toggle
- Personas (Helpful Mentor, Strict Finance Coach, Casual Friend)
- Conversation memory (SQLite) and export (JSON/CSV/TXT)
- Embedded walkthrough GIF (assets/walkthrough.gif)
- A ready-to-run Google Colab notebook (`colab/run_streamlit_colab.ipynb`) to launch the app via ngrok

**Important notes before running**
- Running the model locally is heavy. 4-bit quantization reduces memory but may not work in all setups.
- If you have limited resources, prefer using Hugging Face Inference API (HF_TOKEN) instead of local pipeline.
- The Colab notebook attempts to install dependencies and run the app with ngrok. It includes optional quantization calls.
