import os 

def load_instruction_file(file_path: str = None, default: str = "") -> str:
    """ 
    Load the content of an instruction file. 
    If the file does not exist, raise a FileNotFoundError.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Instruction file not found: {file_path}")
    
    with open(file_path, 'r', encoding="utf8") as file:
        content = file.read()
        return content
    
    return default