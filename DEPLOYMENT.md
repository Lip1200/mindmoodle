# Mental Health Support Companion - Deployment Guide

This guide explains how to deploy the Chainlit Copilot mental health support assistant and embed it in Moodle.

## Overview

The Mental Health Support Companion is a Chainlit-powered chatbot that provides:
- ✅ Crisis keyword detection
- ✅ Safe, non-medical responses
- ✅ Hallucination filtering using mellea library
- ✅ Easy embedding in Moodle HTML blocks
- ✅ Privacy-focused anonymous usage
- ✅ Mobile-responsive design

## Prerequisites

- Python 3.8 or higher
- A server to host the Chainlit application (cloud hosting, VPS, or Docker)
- Access to Moodle with permission to add HTML blocks
- (Optional) OpenAI API key or other LLM provider for production use

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Lip1200/mindmoodle.git
cd mindmoodle
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Chainlit (for the chat interface)
- pytest (for running tests)

Note: We use a safety filtering approach inspired by the mellea library's validation patterns, but don't require mellea as a direct dependency. See MELLEA.md for details.

### 3. Configure the Application (Optional)

For production use with a real LLM:

1. Set up your LLM API credentials (e.g., OpenAI):
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. Update `app.py` to use your LLM instead of placeholder responses:
   ```python
   # Replace the placeholder response generation in generate_response()
   # with actual LLM calls using OpenAI, Anthropic, or your preferred provider
   ```

### 4. Test Locally

Run the application locally to test:

```bash
chainlit run app.py
```

Open your browser to `http://localhost:8000` to test the chat interface.

### 5. Deploy to Production

#### Option A: Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t mental-health-copilot .
docker run -p 8000:8000 mental-health-copilot
```

#### Option B: Cloud Hosting (Heroku, Railway, etc.)

Create a `Procfile`:

```
web: chainlit run app.py --host 0.0.0.0 --port $PORT
```

Deploy using your platform's instructions.

#### Option C: VPS Deployment

1. Set up a reverse proxy (nginx):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

2. Run with systemd or supervisor for persistence

3. Use Let's Encrypt for HTTPS:
   ```bash
   certbot --nginx -d your-domain.com
   ```

### 6. Embed in Moodle

1. Open `moodle_widget.html`
2. Replace `YOUR_CHAINLIT_SERVER_URL` with your deployed server URL
3. In Moodle:
   - Go to your course
   - Turn editing on
   - Add a new HTML block
   - Paste the modified HTML from `moodle_widget.html`
   - Save changes

The chat widget will appear in the bottom-right corner of the page.

## Configuration

### Crisis Keywords

Edit `CRISIS_KEYWORDS` in `app.py` to customize crisis detection:

```python
CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", 
    # Add more keywords as needed
]
```

### Crisis Resources

Update `CRISIS_RESOURCES` in `app.py` with appropriate resources for your region:

```python
CRISIS_RESOURCES = """
Your customized crisis resources here...
"""
```

### Safety Requirements (mellea)

The mellea library filters responses to ensure:
- No medical diagnoses
- No prescription of medications
- No claims of being a therapist
- Grounded, factual responses
- Maintained AI identity

Customize in `create_safety_requirements()` function in `app.py`.

### Widget Appearance

Customize the widget in `moodle_widget.html`:
- Colors: Modify the CSS gradient in `#mh-chat-button`
- Position: Change `bottom` and `right` values
- Size: Adjust `width` and `height` of the iframe container

## Security Considerations

1. **HTTPS Required**: Always use HTTPS in production to protect user privacy
2. **CORS Configuration**: Configure Chainlit to allow embedding from your Moodle domain
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Content Security Policy**: Configure CSP headers appropriately
5. **Privacy**: No conversation data is stored by default - configure as needed

## Monitoring and Maintenance

### Logs

Monitor application logs for:
- Safety requirement violations (filtered responses)
- Crisis keyword detections
- Error messages

### Updates

Regularly update dependencies:

```bash
pip install --upgrade -r requirements.txt
```

### Testing

Test the safety filters regularly:

```bash
python test_safety.py  # Run safety tests
```

## Troubleshooting

### Widget Not Appearing

1. Check browser console for errors
2. Verify CHAINLIT_SERVER_URL is correct
3. Check CORS settings on the server
4. Ensure Moodle allows iframe embedding

### Responses Being Filtered

If too many responses are being filtered:
1. Review the mellea requirements in `app.py`
2. Adjust the safety checks if needed (carefully!)
3. Monitor logs to understand what's being filtered

### Performance Issues

1. Implement caching for common responses
2. Use a CDN for static assets
3. Scale horizontally with load balancer
4. Consider using a faster LLM provider

## Support

For issues or questions:
- GitHub Issues: https://github.com/Lip1200/mindmoodle/issues
- Documentation: See README.md

## License

See LICENSE file for details.
