"""
Copilot configuration for embedding the Mental Health Support Companion
into external web pages (e.g., Moodle HTML blocks).

This configuration enables the Chainlit Copilot widget functionality.
"""

# Copilot widget settings
COPILOT_ENABLED = True

# Widget appearance
COPILOT_BUTTON_COLOR = "#4A90E2"  # Calming blue color
COPILOT_BUTTON_ICON = "💚"  # Heart icon for mental health support

# Widget positioning
COPILOT_POSITION = "bottom-right"  # Position of the chat button

# Widget behavior
COPILOT_ALLOW_ANONYMOUS = True  # Allow anonymous usage for privacy
COPILOT_INITIAL_MESSAGE = "Hi! I'm here to support you. How are you feeling today?"
