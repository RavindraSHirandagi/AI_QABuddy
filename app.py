from flask import Flask, render_template, request, jsonify, send_file
import sys
import os
import pandas as pd
from io import BytesIO
import time
import tempfile

# Import our existing tools
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))
from generate_test_cases import generate_cases_from_lm_studio
from handshake import check_lm_studio
from save_to_excel import save_cases_to_excel
from file_parser import extract_text_from_file

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '.tmp')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_models', methods=['GET'])
def get_models():
    print("Request received for /get_models")
    base_url = request.args.get('base_url', 'http://localhost:1234')
    models = check_lm_studio(base_url=base_url)
    print(f"Returning models: {models}")
    return jsonify({"models": models})

@app.route('/generate', methods=['POST'])
def generate():
    # Handle both JSON and Multipart/Form-Data
    if request.is_json:
        data = request.json
        prompt = data.get('prompt', '')
        model = data.get('model')
        base_url = data.get('base_url', 'http://localhost:1234')
    else:
        # Form Data
        prompt = request.form.get('prompt', '')
        model = request.form.get('model')
        base_url = request.form.get('base_url', 'http://localhost:1234')
        
        # Check for file
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                try:
                    # Save file temporarily
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(filepath)
                    
                    # Extract text
                    print(f"Parsing file: {file.filename}")
                    extracted_text = extract_text_from_file(filepath)
                    
                    # Cleanup
                    os.remove(filepath)
                    
                    if extracted_text.startswith("Error"):
                         return jsonify({"error": extracted_text}), 400
                         
                    # Append/Replace prompt with file content
                    # We treat the file content as the requirement
                    prompt = f"Requirement Document Content:\n{extracted_text}\n\nAdditional Instructions: {prompt}"
                    
                except Exception as e:
                    return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

    if not prompt:
        return jsonify({"error": "No prompt or file provided"}), 400
    if not model:
        return jsonify({"error": "No model selected"}), 400

    print(f"Generating for prompt (length {len(prompt)})... with model: {model} at {base_url}")
    
    start_time = time.time()
    cases = generate_cases_from_lm_studio(prompt, model=model, base_url=base_url)
    end_time = time.time()
    
    execution_time = round(end_time - start_time, 2)
    
    if not cases:
        return jsonify({"error": "Failed to generate cases. Model returned empty output or error.", "execution_time": execution_time}), 500

    return jsonify({"test_cases": cases, "execution_time": execution_time, "model_name": model})

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    test_cases = data.get('test_cases', [])
    
    if not test_cases:
        return jsonify({"error": "No data to download"}), 400

    # Create Excel in memory
    df = pd.DataFrame(test_cases)
    
    # Define preferred column order matching the new schema
    preferred_order = ["TID", "TestType", "Priority", "TestCaseName", "Steps", "Expected_Result"]
    
    # Dynamic column selection: Preferred first, then any others found
    existing_cols = list(df.columns)
    final_cols = [c for c in preferred_order if c in existing_cols] + [c for c in existing_cols if c not in preferred_order]
    
    df = df[final_cols]

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
