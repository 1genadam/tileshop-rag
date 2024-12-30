from flask import Flask, jsonify
import os
app = Flask(__name__)
@app.route('/')
def home():
   return jsonify({"message": "analytics Service is running!"})
@app.route('/health')
def health():
   return jsonify({"status": "healthy"})
if __name__ == "__main__":
   port = int(os.environ.get("PORT", 8086))
   app.run(host='0.0.0.0', port=port)
