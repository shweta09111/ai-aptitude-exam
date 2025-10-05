"""
Vercel serverless function handler
This is the entry point for Vercel deployment
"""

from app import app

# Vercel expects a handler for serverless functions
def handler(request, context):
    """Handle Vercel serverless function calls"""
    return app(request, context)

# For local development
if __name__ == '__main__':
    app.run(debug=True)
