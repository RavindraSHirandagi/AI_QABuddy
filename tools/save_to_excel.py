import pandas as pd
import os

def save_cases_to_excel(test_cases, filename="test_cases.xlsx"):
    """
    Saves a list of test case dictionaries to an Excel file.
    """
    try:
        df = pd.DataFrame(test_cases)
        
        df = pd.DataFrame(test_cases)
        
        # Define preferred column order
        preferred_order = ["TID", "TestType", "Priority", "TestCaseName", "Steps", "Expected_Result"]
        
        # Normalize column names to match preferred order (simple mapping)
        # Verify which columns actually exist in the dataframe
        existing_cols = list(df.columns)
        
        # Create a sorted list of columns: preferred ones first, then others
        final_cols = [c for c in preferred_order if c in existing_cols] + [c for c in existing_cols if c not in preferred_order]
        
        df = df[final_cols]
        
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
