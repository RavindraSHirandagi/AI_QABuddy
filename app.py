from flask import Flask, render_template, request, jsonify, send_file
import sys
import os
import pandas as pd
from io import BytesIO
import time
import tempfile

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

# Import tools
from generate_test_cases import generate_cases_from_server
from generate_test_plan import generate_plan_from_server
from handshake import check_ai_server
from save_to_excel import save_cases_to_excel
from save_to_docx import save_plan_to_docx
from save_to_pdf import save_plan_to_pdf
from file_parser import extract_text_from_file

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '.tmp')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DEFAULT_BASE_URL = "http://localhost:11434"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_models', methods=['GET'])
def get_models():
    print("Request received for /get_models")
    base_url = request.args.get('base_url', DEFAULT_BASE_URL)
    models = check_ai_server(base_url=base_url)
    print(f"Returning models: {models}")
    return jsonify({"models": models})

def process_upload_and_prompt(req):
    """Helper to handle file uploads and prompt construction"""
    if req.is_json:
        data = req.json
        prompt = data.get('prompt', '')
        model = data.get('model')
        base_url = data.get('base_url', DEFAULT_BASE_URL)
        return prompt, model, base_url, None
    else:
        prompt = req.form.get('prompt', '')
        model = req.form.get('model')
        base_url = req.form.get('base_url', DEFAULT_BASE_URL)
        
        if 'file' in req.files:
            file = req.files['file']
            if file and file.filename != '':
                try:
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(filepath)
                    print(f"Parsing file: {file.filename}")
                    extracted_text = extract_text_from_file(filepath)
                    os.remove(filepath)
                    
                    if extracted_text.startswith("Error"):
                         return None, None, None, extracted_text
                         
                    prompt = f"Requirement Document Content:\n{extracted_text}\n\nAdditional Instructions: {prompt}"
                except Exception as e:
                    return None, None, None, f"Failed to process file: {str(e)}"
        
        return prompt, model, base_url, None

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    prompt, model, base_url, error = process_upload_and_prompt(request)
    if error: return jsonify({"error": error}), 500
    if not prompt: return jsonify({"error": "No prompt provided"}), 400
    if not model: return jsonify({"error": "No model selected"}), 400

    print(f"Generating Test Plan with model: {model} at {base_url}")
    start_time = time.time()
    plan = generate_plan_from_server(prompt, model=model, base_url=base_url)
    end_time = time.time()
    
    execution_time = round(end_time - start_time, 2)
    
    if isinstance(plan, dict) and "error" in plan:
         return jsonify({"error": plan["error"], "execution_time": execution_time}), 500

    token_usage = None
    if isinstance(plan, dict):
        token_usage = plan.pop("usage", None) # Remove usage from plan object so it doesn't clutter the UI view logic

    if not plan:
        return jsonify({"error": "Model failed to generate a valid JSON plan."}), 500
        
    return jsonify({"test_plan": plan, "execution_time": execution_time, "model_name": model, "token_usage": token_usage})

@app.route('/download_plan_pdf', methods=['POST'])
def download_plan_pdf():
    data = request.json
    plan = data.get('test_plan', {})
    
    if not plan:
        return jsonify({"error": "No plan data to download"}), 400

    output = BytesIO()
    success = save_plan_to_pdf(plan, output)
    output.seek(0)
    
    if success:
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"TestPlan.pdf"
        )
    else:
        return jsonify({"error": "Failed to generate PDF"}), 500

@app.route('/download_plan', methods=['POST'])
def download_plan():
    data = request.json
    plan = data.get('test_plan', {})
    
    if not plan:
        return jsonify({"error": "No plan data to download"}), 400

    output = BytesIO()
    success = save_plan_to_docx(plan, output)
    output.seek(0)
    
    if success:
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=f"TestPlan.docx"
        )
    else:
        return jsonify({"error": "Failed to generate DOCX"}), 500

@app.route('/generate', methods=['POST'])
def generate():
    prompt, model, base_url, error = process_upload_and_prompt(request)
    if error: return jsonify({"error": error}), 500
    if not prompt: return jsonify({"error": "No prompt provided"}), 400
    if not model: return jsonify({"error": "No model selected"}), 400

    print(f"Generating Cases with model: {model} at {base_url}")
    start_time = time.time()
    cases = generate_cases_from_server(prompt, model=model, base_url=base_url)
    end_time = time.time()
    
    execution_time = round(end_time - start_time, 2)
    
    if isinstance(cases, dict) and "error" in cases:
        return jsonify({"error": cases["error"], "execution_time": execution_time}), 500

    token_usage = None
    final_cases = cases
    if isinstance(cases, dict) and "test_cases" in cases:
        # Extract usage if present
        token_usage = cases.get("usage")
        final_cases = cases["test_cases"]
    elif isinstance(cases, dict) and "usage" in cases:
         # Edge case if wrapped differently, e.g. the list was returned raw but we wrapped it in generate_cases_from_server
         token_usage = cases.get("usage")
         # If "test_cases" is missing but "usage" exists, maybe the dict ITSELF is the container of other keys?
         # Or maybe it was a list that got wrapped into {"test_cases": list, "usage": {}} by our previous fix.
         # Let's check if 'test_cases' is there.
         if "test_cases" in cases:
             final_cases = cases["test_cases"]
         else:
             # This implies the dict might just BE a single test case? Unlikely.
             # Or maybe the repair logic returned a dict without "test_cases".
             # Let's assume the dict itself is the data minus usage.
             final_cases = {k: v for k, v in cases.items() if k != "usage"}
             # But likely "test_cases" is just parsed.get("test_cases") which might be None if structure failed.
             pass
         
    if not final_cases:
        return jsonify({"error": "Failed to generate cases.", "execution_time": execution_time}), 500

    return jsonify({"test_cases": final_cases, "execution_time": execution_time, "model_name": model, "token_usage": token_usage})

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    test_cases = data.get('test_cases', [])
    
    if not test_cases:
        return jsonify({"error": "No data to download"}), 400

    # Create Excel in memory
    df = pd.DataFrame(test_cases)
    
    # Normalization
    rename_map = {
        "test_id": "TID", "tid": "TID",
        "test_type": "TestType", "type": "TestType", "testtype": "TestType",
        "priority": "Priority", 
        "test_name": "TestCaseName", "test_case_name": "TestCaseName", "name": "TestCaseName", "TestName": "TestCaseName",
        "steps": "Steps", "step": "Steps",
        "expected_result": "Expected_Result", "expected": "Expected_Result", "result": "Expected_Result", "description": "TestCaseName"
    }
    df = df.rename(columns=rename_map)
    
    # Sorting columns
    preferred_order = ["TID", "TestType", "Priority", "TestCaseName", "Steps", "Expected_Result"]
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
