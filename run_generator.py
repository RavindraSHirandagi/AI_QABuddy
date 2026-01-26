import sys
import os

# Add tools directory to path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from generate_test_cases import generate_cases_from_ollama
from save_to_excel import save_cases_to_excel

def main():
    print("[*] Local LLM Test Case Generator (Powered by Ollama)")
    print("---------------------------------------------------")
    
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

    print("\n[.] Processing... sending request to Ollama (this may take a moment)...")

    # 2. Generate
    test_cases = generate_cases_from_ollama(user_input)
    
    if not test_cases:
        print("[X] Failed to generate test cases. Please check the logs or try again.")
        return

    print(f"\n[+] Generated {len(test_cases)} test cases.")

    # 3. Save
    output_file = "test_cases.xlsx"
    success = save_cases_to_excel(test_cases, output_file)
    
    if success:
        print(f"\n[+] Success! file saved to: {output_file}")
        print("You can open this file in Excel.")
    else:
        print("\n[!] Failed to save file.")

if __name__ == "__main__":
    main()
