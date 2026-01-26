from flask import Flask, render_template, request, jsonify, send_file
import sys
import os
import pandas as pd
from io import BytesIO
import time

# Import our existing tools
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))
from generate_test_cases import generate_cases_from_ollama
from save_to_excel import save_cases_to_excel

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    print(f"Generating for prompt: {prompt[:50]}...")
    
    # Call the existing tool
    # Using 'qwen3:4b' or strictly whatever is working in the CLI
    start_time = time.time()
    cases = generate_cases_from_ollama(prompt, model="qwen3:4b")
    end_time = time.time()
    
    execution_time = round(end_time - start_time, 2)
    
    if not cases:
        return jsonify({"error": "Failed to generate cases. Model returned empty output.", "execution_time": execution_time}), 500

    return jsonify({"test_cases": cases, "execution_time": execution_time})

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    test_cases = data.get('test_cases', [])
    
    if not test_cases:
        return jsonify({"error": "No data to download"}), 400

    # Create Excel in memory
    df = pd.DataFrame(test_cases)
    cols = ["test_name", "steps", "expected_result"]
    cols = [c for c in cols if c in df.columns]
    df = df[cols]
    df.rename(columns={
        "test_name": "Test Name",
        "steps": "Steps",
        "expected_result": "Expected Result"
    }, inplace=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='test_cases.xlsx'
    )

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, port=5000)
