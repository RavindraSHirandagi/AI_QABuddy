import sys
import os

# Add tools directory to path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from generate_test_cases import generate_cases_from_lm_studio
from handshake import check_lm_studio
from save_to_excel import save_cases_to_excel

def main():
    print("[*] Local LLM Test Case Generator (Powered by LM Studio)")
    print("---------------------------------------------------")
    
    # 0. Select Model
    print("[.] Checking available models in LM Studio...")
    models = check_lm_studio()
    if not models:
        print("[X] No models found or LM Studio is not running (Port 1234). Exiting.")
        return

    selected_model = models[0] # Default
    # precise match or substring match for mistral
    for m in models:
        if "mistral" in m.lower():
            selected_model = m
            break
            
    print(f"[+] Using model: {selected_model}")

    # 1. Capture Input
    if len(sys.argv) > 1:
        # Read from command line args if provided
        user_input = " ".join(sys.argv[1:])
        print(f"Read input from arguments: {user_input[:50]}...")
    else:
        # Interactive mode
        print("Please paste your requirements below. Type 'DONE' on a new line when finished:\n")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "DONE":
                    break
                lines.append(line)
            except EOFError:
                break
        user_input = "\n".join(lines).strip()
    
    if not user_input:
        print("[X] Error: No input provided. Exiting.")
        return

    print(f"\n[.] Processing... sending request to LM Studio ({selected_model})...")

    # 2. Generate
    test_cases = generate_cases_from_lm_studio(user_input, model=selected_model)
    
    if not test_cases:
        print("[X] Failed to generate test cases. Please check the logs or try again.")
        return

    print(f"\n[+] Generated {len(test_cases)} test cases.")

    # 3. Save
    # Create filename based on model name, sanitized
    safe_model_name = selected_model.replace(":", "_").replace("/", "_").replace("\\", "_")
    output_file = f"LLM_TestCase_{safe_model_name}.xlsx"
    
    success = save_cases_to_excel(test_cases, output_file)
    
    if success:
        print(f"\n[+] Success! Test cases saved to: {os.path.abspath(output_file)}")
        print("You can open this file in Excel.")
    else:
        print("\n[!] Failed to save file.")

if __name__ == "__main__":
    main()
