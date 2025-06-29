#!/usr/bin/env python3
"""
Tileshop RAG Web UI - Flask-based web interface for the RAG system
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from simple_rag import SimpleTileshopRAG

app = Flask(__name__)
rag = SimpleTileshopRAG()

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat queries"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        response = rag.chat(query)
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync', methods=['POST'])
def sync_data():
    """API endpoint to sync product data"""
    try:
        rag.sync_data()
        return jsonify({'success': True, 'message': 'Data synced successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """API endpoint for product search"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = data.get('limit', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        results = rag.search_products(query, limit)
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5001, debug=True)