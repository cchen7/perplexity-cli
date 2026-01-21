# Perplexity CLI

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

An interactive command-line interface for [Perplexity](https://perplexity.ai) search powered by the Sonar API. Get real-time AI responses with web search capabilities directly in your terminal.

## ✨ Features

- **🌊 Streaming Responses** - See AI responses as they're generated in real-time
- **💾 Session Management** - Save and load conversation sessions
- **⌨️ Slash Commands** - Intuitive commands for navigation and control
- **🎛️ Configurable** - Custom system prompts and model selection
- **📊 Smart Context** - Automatic conversation summarization when approaching token limits
- **🎨 Rich Output** - Beautiful terminal formatting with Markdown support

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- [Perplexity API key](https://docs.perplexity.ai/guides/getting-started)

### Installation

```bash
# Clone the repository
git clone https://github.com/cchen7/perplexity-cli.git
cd perplexity-cli

# Install dependencies
pip install -r requirements.txt

# Set your API key
export PPLX_API_KEY="your-api-key-here"

# Run the CLI
python perplexity_cli.py
```

## 📖 Usage

### Basic Conversation

Simply type your question and press Enter:

```
❯ What's the latest news about AI?
```

The response streams in real-time with proper formatting.

### Slash Commands

| Command | Description |
|---------|-------------|
| `/new` | Start a new conversation |
| `/save` | Save current session to disk |
| `/load` | Load a previous session |
| `/clear` | Clear conversation history |
| `/model` | Switch between models |
| `/system` | Set custom system prompt |
| `/sessions` | List saved sessions |
| `/help` | Show available commands |
| `/exit` | Exit the CLI |

### Example Session

```
┌─────────────────────────────────────────┐
│         Perplexity CLI                  │
│  Interactive search with real-time AI  │
│                                         │
│  Model: sonar-pro                       │
│  Type /help for available commands      │
└─────────────────────────────────────────┘

❯ What is quantum computing?

Quantum computing is a type of computation that harnesses quantum 
mechanical phenomena like superposition and entanglement...

❯ /save
? Session name: quantum-research
Session saved to quantum-research.json

❯ /exit
Goodbye!
```

## ⚙️ Configuration

Configuration is stored in `~/.perplexity-cli/config.yaml`:

```yaml
model: sonar-pro
system_prompt: "You are a helpful AI assistant with real-time search capabilities."
input_token_limit: 3000
output_token_limit: 1000
auto_save: false
session_dir: ~/.perplexity-cli/sessions
```

## 🤖 Available Models

| Model | Description |
|-------|-------------|
| `sonar` | Fast, efficient model for quick queries |
| `sonar-pro` | Enhanced capabilities (default) |
| `sonar-reasoning` | Advanced reasoning for complex questions |
| `sonar-reasoning-pro` | Most capable model for in-depth analysis |

## 📁 Project Structure

```
perplexity-cli/
├── perplexity_cli.py    # Main CLI application
├── api.py               # Perplexity API client
├── session.py           # Session management
├── config.py            # Configuration handling
├── requirements.txt     # Python dependencies
├── test_cli.py          # Integration tests
├── LICENSE              # Apache 2.0 license
└── README.md            # This file
```

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PPLX_API_KEY` | Your Perplexity API key | Yes |

## 🧪 Running Tests

```bash
export PPLX_API_KEY="your-api-key"
python test_cli.py
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🔗 Resources

- [Perplexity API Documentation](https://docs.perplexity.ai/home)
- [API Playground](https://perplexity.ai/account/api/playground)
- [Get API Key](https://docs.perplexity.ai/guides/getting-started)
