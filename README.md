# MindMoodle - Mental Health Support Companion 💚

A Chainlit Copilot chat widget for mental health support, designed to be embedded in Moodle HTML blocks.

## Features

🛡️ **Safe & Responsible**
- Crisis keyword detection with immediate resource display
- Safety filtering inspired by mellea library to prevent hallucinations and medical advice
- No diagnoses or prescriptions
- Clear AI identity - never claims to be a therapist

💬 **Supportive & Accessible**
- Empathetic, student-focused responses
- Anonymous usage for privacy
- Mobile-responsive design
- Accessible to screen readers

🔧 **Easy Integration**
- Simple JavaScript snippet for Moodle HTML blocks
- Copilot widget with customizable appearance
- Works with any LLM provider (OpenAI, Anthropic, etc.)

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run locally:**
   ```bash
   chainlit run app.py
   ```

3. **Test the interface:**
   Open `http://localhost:8000` in your browser

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:
- Docker deployment
- Cloud hosting (Heroku, Railway, etc.)
- VPS setup with nginx
- Moodle integration

## Architecture

- **app.py** - Main Chainlit application with crisis detection and mellea safety filtering
- **moodle_widget.html** - JavaScript snippet for Moodle HTML block integration
- **chainlit.md** - Welcome message and information for users
- **.chainlit** - Chainlit configuration file
- **copilot_config.py** - Copilot widget settings

## Safety Features

### Crisis Detection
Automatically detects crisis-related keywords and displays immediate resources:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Campus counseling services

### Safety Filtering (mellea-inspired)
Uses a validation pattern inspired by the mellea library to validate all responses and ensure they:
- Don't provide medical diagnoses
- Don't prescribe medications
- Don't claim to be a therapist
- Don't hallucinate facts
- Maintain clear AI identity

## Customization

### Update Crisis Keywords
Edit `CRISIS_KEYWORDS` in `app.py`

### Customize Crisis Resources
Edit `CRISIS_RESOURCES` in `app.py` with region-specific resources

### Change Widget Appearance
Modify CSS in `moodle_widget.html`:
- Colors
- Position
- Size
- Animation

### Integrate Your LLM
Replace the placeholder responses in `generate_response()` with your LLM API calls (OpenAI, Anthropic, etc.)

## Privacy & Security

- Anonymous usage by default
- No conversation storage (configure as needed)
- HTTPS recommended for production
- CORS configuration required for embedding
- Client-side crisis detection for faster response

## Example Usage

### In Moodle
1. Copy the content from `moodle_widget.html`
2. Replace `YOUR_CHAINLIT_SERVER_URL` with your deployed URL
3. Add as an HTML block in your Moodle course
4. Students will see a chat widget in the bottom-right corner

### Standalone
Access the chat interface directly at your deployed URL for a full-page experience.

## Contributing

Contributions are welcome! Please ensure:
- Safety features remain intact
- Tests pass
- Documentation is updated
- Changes align with mental health best practices

## Important Notes

⚠️ **This is NOT a replacement for professional mental health care**

This tool is designed to:
- Provide emotional support
- Offer coping strategies
- Direct users to professional resources when needed

It does NOT:
- Diagnose mental health conditions
- Prescribe treatment
- Replace therapy or counseling

Users in crisis should always be directed to:
- Campus counseling centers
- Crisis hotlines (988, Crisis Text Line)
- Emergency services when appropriate

## License

See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Chainlit](https://chainlit.io/)
- Safety filtering powered by [mellea](https://github.com/ibm-granite/mellea)
- Designed for student mental health and wellbeing

## Support

For questions or issues, please open an issue on GitHub.
