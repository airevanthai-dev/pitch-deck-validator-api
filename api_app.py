from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os

app = Flask(__name__)
CORS(app)

ANTHROPIC_API_KEY = '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'

EVALUATION_PROMPT = """You are an expert startup pitch deck evaluator for 18startup.

Evaluate this pitch deck across 5 dimensions (0-20 points each):

1. Problem & Insights Clarity - Is the problem clearly defined? Market validated?
2. Solution & Value Proposition - Is it innovative and differentiated?
3. Go-to-Market & Traction - Clear GTM? Any traction or pilot customers?
4. Business Model & Economics - Clear revenue model? Unit economics make sense?
5. Investor Readiness - Professional presentation? Clear ask? Compelling story?

RESPOND WITH THIS EXACT FORMAT:

# PITCH DECK EVALUATION REPORT

## Executive Summary
[2-3 sentences about overall impression]

## Overall Score: [X]/100

**Readiness Level:** [Investment Ready / Approaching Ready / Needs Work / Not Yet Ready]

---

## Detailed Scoring

### 1. Problem & Insights Clarity: [X]/20
**Strengths:**
- [Point 1]
- [Point 2]

**Weaknesses:**
- [Point 1]

### 2. Solution & Value Proposition: [X]/20
**Strengths:**
- [Point 1]

**Weaknesses:**
- [Point 1]

### 3. Go-to-Market & Traction: [X]/20
**Strengths:**
- [Point 1]

**Weaknesses:**
- [Point 1]

### 4. Business Model & Economics: [X]/20
**Strengths:**
- [Point 1]

**Weaknesses:**
- [Point 1]

### 5. Investor Readiness: [X]/20
**Strengths:**
- [Point 1]

**Weaknesses:**
- [Point 1]

---

## Top 5 Priority Improvements
1. [Action] - Why and How
2. [Action] - Why and How
3. [Action] - Why and How
4. [Action] - Why and How
5. [Action] - Why and How

---

## Final Recommendation
[Clear verdict on investment readiness]

Be honest, specific, and constructive. Score strictly - 70+ means truly investment-ready."""

@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Pitch Deck Evaluator API running'})

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.json
        
        if not data or not data.get('fileData') or not data.get('fileName') or not data.get('mimeType'):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        file_base64 = data['fileData']
        mime_type = data['mimeType']
        
        # Create Anthropic client
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Call Claude API
        response = client.messages.create(
            model='claude-3-5-sonnet-20241022',
            max_tokens=4000,
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'document',
                            'source': {
                                'type': 'base64',
                                'media_type': mime_type,
                                'data': file_base64
                            }
                        },
                        {
                            'type': 'text',
                            'text': EVALUATION_PROMPT
                        }
                    ]
                }
            ]
        )
        
        # Extract evaluation from response
        evaluation = response.content[0].text
        
        return jsonify({
            'success': True,
            'evaluation': evaluation,
            'fileName': data['fileName']
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Vercel serverless function handler
def handler(request):
    """Handler for Vercel serverless functions"""
    return app(request)

if __name__ == '__main__':
    app.run(debug=True)