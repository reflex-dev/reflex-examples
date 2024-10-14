# Reflex Chat App

A user-friendly, highly customizable Python web app designed to demonstrate LLMs in a ChatGPT format.

<div align="center">
<img src="./docs/demo.gif" alt="icon"/>
</div>

# Getting Started

You'll need a valid OpenAI subscription - save your API key under the environment variable `OPENAI_API_KEY`:

```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY" # replace me!
```

### 🧬 1. Clone the Repo

```bash
git clone https://github.com/reflex-dev/reflex-chat.git
```

### 📦 2. Install Reflex

To get started with Reflex, you'll need:

- Python 3.7+
- Node.js 12.22.0+ \(No JavaScript knowledge required!\)
- Pip dependencies: `reflex`, `openai`

Install `pip` dependencies with the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 🚀 3. Run the application

Initialize and run the app:

```
reflex init
reflex run
```

# Features

- 100% Python-based, including the UI, using Reflex
- Create and delete chat sessions
- The application is fully customizable and no knowledge of web dev is required to use it.
    - See https://reflex.dev/docs/styling/overview for more details 
- Easily swap out any LLM
- Responsive design for various devices

# Contributing

We welcome contributions to improve and extend the LLM Web UI. 
If you'd like to contribute, please do the following:
- Fork the repository and make your changes. 
- Once you're ready, submit a pull request for review.

# License

The following repo is licensed under the MIT License.
