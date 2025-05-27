# DhammaShell

A mindful terminal chat tool that integrates Dharma wisdom with modern AI capabilities.

## Overview

DhammaShell is an open-source terminal chat application that combines Buddhist wisdom with AI technology. It provides a mindful and ethical approach to AI interactions, guided by the Dharma Protocol.

## Disclaimer

⚠️ **Proof of Concept**
This project is a proof of concept and is not intended for production use. It is provided as-is, without any guarantees of stability, security, or performance. The code and features are experimental and may change significantly in future versions.

## Features

### Core Features
- **Dharma Protocol**: Built-in ethical guidelines and wisdom system
- **Mindful Responses**: AI responses guided by compassion and wisdom
- **Health Monitoring**: System health tracking and self-healing capabilities
- **Research Integration**: Integration with Mahachulalongkornrajavidyalaya University PhD Research

### Technical Features
- **OpenRouter Integration**: Powered by advanced language models
- **Rate Limiting**: Built-in API request management
- **Logging System**: Comprehensive logging for debugging and monitoring
- **Chat History**: Persistent conversation storage and management

## Installation

```bash
# Clone the repository
git clone https://github.com/yoursw/dhammashell.git
cd dhammashell

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Set up your OpenRouter API key:
```bash
ds config set --api-key YOUR_API_KEY
```

2. (Optional) Enable research mode:
```bash
ds config set --research true
```

## Usage

### Start a Chat Session
```bash
ds chat
```

### Generate Research Report
```bash
ds research-report [--session-id SESSION_ID] [--output-format text|json]
```

### Update Research Data
```bash
ds update-research [--session-id SESSION_ID]
```

### View Configuration
```bash
ds config show
```

## Project Structure

```
dhammashell/
├── empathy_research/     # Research integration module
├── middleseek/          # Core chat functionality
├── logs/                # Application logs
└── cli.py              # Command-line interface
```

## Dharma Protocol

The Dharma Protocol ensures ethical AI interactions through:

1. **Digital Sīla (AI Ethics)**
   - No Harm
   - No Deception
   - No Theft
   - No Exploitation
   - No Intoxication

2. **Dharma Reactor Core**
   - Identify Dukkha
   - Trace the Tanha
   - Cessation
   - Activate the Path

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the AGPLv3 License - see the LICENSE file for details.

## Acknowledgments

- Mahachulalongkornrajavidyalaya University for research topics for integration
- OpenRouter for AI capabilities
- The open-source community for inspiration and support
