import pandas as pd
import os

def save_cases_to_excel(test_cases, filename="test_cases.xlsx"):
    """
    Saves a list of test case dictionaries to an Excel file.
    """
    try:
        df = pd.DataFrame(test_cases)
        
        # Ensure distinct columns order
        cols = ["test_name", "steps", "expected_result"]
        # Filter for only available columns to avoid errors if keys mismatch
        cols = [c for c in cols if c in df.columns]
        df = df[cols]
        
        # Rename for better readability
        df.rename(columns={
            "test_name": "Test Name",
            "steps": "Steps",
            "expected_result": "Expected Result"
        }, inplace=True)
        
        df.to_excel(filename, index=False)
        print(f"Successfully saved {len(df)} test cases to {os.path.abspath(filename)}")
        return True
    
    except PermissionError:
        print(f"Error: Permission denied. Is '{filename}' open in Excel? Please close it and try again.")
        return False
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        return False

if __name__ == "__main__":
    # Test run
    dummy_data = [
        {"test_name": "Test 1", "steps": "Step 1", "expected_result": "Pass"},
        {"test_name": "Test 2", "steps": "Step 2", "expected_result": "Fail"}
    ]
    save_cases_to_excel(dummy_data, "test_tools_output.xlsx")
