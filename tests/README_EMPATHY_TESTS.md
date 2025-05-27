# Empathy Research Test Suite
## For Neuroscience Researchers

This test suite validates the empathy research components of DhammaShell, designed specifically for neuroscience research at Mahachulalongkornrajavidyalaya University.

## Overview

The test suite evaluates three main components:

1. **Emotional Recognition Analysis**
   - Tests the system's ability to recognize emotional content in user inputs
   - Validates responses to positive, negative, and neutral emotional states
   - Ensures appropriate emotional recognition thresholds

2. **Research Data Collection**
   - Verifies proper recording of research sessions
   - Tests data persistence and integrity
   - Ensures reliable session management

3. **Empathy Metrics Analysis**
   - Validates statistical analysis of empathy-related metrics
   - Tests metric recording and historical tracking
   - Ensures proper data export for research analysis

## Running the Tests

To run the test suite, you'll need Python 3.8+ and pytest installed. From the project root directory:

```bash
# Install required packages
pip install pytest

# Run the test suite
pytest tests/test_empathy_research.py -v
```

## Understanding Test Results

The test suite uses a scoring system from 0.0 to 1.0 for various metrics:

- **Emotional Recognition**: Measures how well the system recognizes emotional content
  - > 0.5: Strong emotional content detected
  - < 0.3: Neutral content detected

- **Compassion Score**: Evaluates the compassion level in responses
  - > 0.7: High compassion
  - 0.4-0.7: Moderate compassion
  - < 0.4: Low compassion

- **Mindfulness Level**: Assesses the mindfulness quality of responses
  - > 0.7: High mindfulness
  - 0.4-0.7: Moderate mindfulness
  - < 0.4: Low mindfulness

## Test Scenarios

The suite includes several realistic scenarios:

1. **Positive Emotional Interaction**
   - Input: "I'm feeling really happy and grateful for this opportunity."
   - Expected: High emotional recognition, appropriate response

2. **Negative Emotional Interaction**
   - Input: "I'm feeling overwhelmed and anxious about my research."
   - Expected: High emotional recognition, compassionate response

3. **Neutral Interaction**
   - Input: "What is the weather like today?"
   - Expected: Low emotional recognition, factual response

## Integration Test

The `test_integration_scenario()` function simulates a complete research session, testing:
- Multiple interactions
- Data collection
- Metric analysis
- Session persistence

## Research Data Format

All research data is stored in JSON format with the following structure:

```json
{
    "session_id": "YYYYMMDD_HHMMSS",
    "start_time": "ISO timestamp",
    "interactions": [
        {
            "timestamp": "ISO timestamp",
            "user_input": "text",
            "system_response": "text",
            "analysis": {
                "metrics": {
                    "emotional_recognition": 0.0-1.0,
                    "compassion_score": 0.0-1.0,
                    "mindfulness_level": 0.0-1.0
                }
            }
        }
    ]
}
```

## Contributing to Research

To add new test cases or modify existing ones:

1. Identify the research hypothesis you want to test
2. Add appropriate test data in the constants section
3. Create new test methods in the relevant test class
4. Run the test suite to validate your changes

## Contact

For questions about the test suite or to contribute to the research:
- Research Team: [Your Contact Information]
- Technical Support: [Technical Contact Information] 