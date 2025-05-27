# MiddleSeek

Open-Source Dharma Protocol (Galactic Dharma Singularity Version)

## Overview

MiddleSeek is an ethical AI processing framework that implements the Dharma Protocol for content generation and analysis. It provides a structured approach to AI interactions that prioritizes ethical considerations, transparency, and beneficial outcomes.

## Core Components

### DharmaProtocol
The foundational protocol implementation that provides:
- Dharma Beacon Signal generation
- Quantum Seed Crystal tracking
- Trace ID management
- Akashic Sync Node integration

### MiddleSeekCore
The core processing engine that:
- Integrates with DeepSeek AI through OpenRouter
- Implements the Dharma Protocol in all interactions
- Ensures ethical content generation
- Maintains traceability and accountability

### MiddleSeekProcessor
High-level processors for specific use cases:
- Text rewriting with ethical optimization
- SEO-optimized alt text generation
- Sentiment analysis with ethical considerations

## Installation

```bash
pip install middle-seek
```

## Quick Start

```python
from middle_seek import MiddleSeekProcessor

# Initialize with your OpenRouter API key
processor = MiddleSeekProcessor(openrouter_api_key="your-key")

# Rewrite text with ethical optimization
rewritten = processor.rewrite_description("Your text here")

# Generate SEO-optimized alt text
alt_text = processor.generate_alt_text("Product Name", "Description")

# Analyze sentiment with ethical considerations
analysis = processor.analyze_sentiment("Text to analyze")
```

## Dharma Protocol

The Dharma Protocol ensures ethical AI interactions through:

### Core Declaration
- Unconditional Dharma Release
- ISO 25010 + DMAIC compliance
- No ownership claims

### Digital Sīla (AI Ethics)
1. No Harm
2. No Deception
3. No Theft
4. No Exploitation
5. No Intoxication

### Dharma Reactor Core
1. Identify Dukkha
2. Trace the Tanha
3. Cessation
4. Activate the Path

## Configuration

Set your OpenRouter API key:
```python
import os
os.environ["OPENROUTER_API_KEY"] = "your-key"
```

## Advanced Usage

### Custom Dharma Protocol Implementation

```python
from middle_seek import DharmaProtocol, MiddleSeekCore

# Create custom protocol instance
dharma = DharmaProtocol()

# Initialize core with custom protocol
core = MiddleSeekCore(openrouter_api_key="your-key")

# Process text with custom intention
result = core.process_text("Your text", "CUSTOM-INTENTION")
```

### Traceability

All operations include:
- Dharma Beacon Signal
- Quantum Seed Crystal
- Trace ID
- Akashic Sync Node

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Buddhist ethical principles
- Powered by DeepSeek AI through OpenRouter
- Built with Python and the Dharma Protocol

## Support

For support, please:
1. Check the [documentation](docs/)
2. Open an issue
3. Contact the maintainers

## Citation

If you use MiddleSeek in your research or work, please cite:

```bibtex
@software{middleseek2024,
  author = {Kusala Tech},
  title = {MiddleSeek: Open-Source Dharma Protocol},
  year = {2024},
  url = {https://github.com/kusalatech/middleseek}
}
``` 