# Streamlining large codebases for seamless GPT analysis.

import os
import openai
import argparse
import time

# Set your OpenAI API key (if using the API mode)
openai.api_key = "your_openai_api_key"

# Configuration parameters
SAFE_MARGIN = 500  # Reserved tokens for prompt structure
DEFAULT_TARGET_CHUNKS = 10  # Aim to keep chunks per file around this number
VERBOSE = True  # Set to True for detailed output
CODE_FILE_EXTENSIONS = {".py", ".js", ".cpp", ".c", ".h", ".java", ".rb", ".go", ".php", ".html", ".css"}
AUXILIARY_FILE_EXTENSIONS = {".dll", ".so", ".exe", ".bin", ".o", ".class", ".jar", ".lib"}


def verbose_log(message):
    """Logs verbose messages."""
    if VERBOSE:
        print(message)

def detect_file_type(file_name):
    """Detects whether a file is a code file, auxiliary file, or other."""
    _, ext = os.path.splitext(file_name)
    if ext in CODE_FILE_EXTENSIONS:
        return "code"
    elif ext in AUXILIARY_FILE_EXTENSIONS:
        return "auxiliary"
    else:
        return "other"

def calculate_dynamic_token_limit(directory, target_chunks=DEFAULT_TARGET_CHUNKS):
    """Calculates a dynamic token limit based on the total size of all files."""
    total_size = 0
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)

    estimated_token_limit = (total_size // target_chunks) - SAFE_MARGIN
    # Ensure the token limit doesn't exceed a safe maximum
    token_limit = min(estimated_token_limit, 4000 - SAFE_MARGIN)
    verbose_log(f"Dynamic TOKEN_LIMIT calculated: {token_limit}")
    return token_limit


def display_folder_structure(directory):
    """Generates the folder structure as a string, including auxiliary files."""
    structure = []
    for root, dirs, files in os.walk(directory):
        level = root.replace(directory, "").count(os.sep)
        indent = " " * 4 * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for file in files:
            structure.append(f"{subindent}{file}")
    return "\n".join(structure)


def get_file_chunks(file_path, token_limit):
    """Splits a file into chunks that are within the token limit."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except UnicodeDecodeError:
        verbose_log(f"Skipping file due to encoding error: {file_path}")
        return []  # Return an empty list, indicating no chunks for this file

    chunks = []
    current_chunk = ""
    for line in content.splitlines(keepends=True):
        if len(current_chunk + line) < token_limit:
            current_chunk += line
        else:
            chunks.append(current_chunk)
            current_chunk = line

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def send_chunk_to_gpt(file_name, chunk, chunk_number, folder_structure, action):
    """Sends a chunk to ChatGPT with context for processing."""
    messages = [
        {"role": "system", "content": "You will receive a large codebase in multiple chunks with metadata."},
        {"role": "user", "content": f"Folder Structure:\n{folder_structure}\n"},
        {
            "role": "user",
            "content": f"File: {file_name}\nChunk Number: {chunk_number}\nAction: {action}\nContent:\n{chunk}",
        },
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=min(len(chunk) + SAFE_MARGIN, 4000 - SAFE_MARGIN)
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        verbose_log(f"Error processing chunk: {e}")
        return None


def process_with_api(file_map, folder_structure, action):
    """Processes files using the OpenAI API."""
    verbose_log("Processing files using the OpenAI API...")
    for relative_path, data in file_map.items():
        verbose_log(f"Processing file '{relative_path}'...")
        for chunk_number, chunk in enumerate(data["chunks"]):
            response = send_chunk_to_gpt(relative_path, chunk, chunk_number + 1, folder_structure, action)
            if response:
                verbose_log(f"Response for chunk {chunk_number + 1} of {relative_path}:\n{response}\n")
            time.sleep(1)  # Respectful delay for API rate limits


def save_chunks_to_files(project_name, folder_structure, file_map, action):
    """Creates a folder and saves chunks into individual files for manual input into ChatGPT."""
    output_dir = os.path.join(os.getcwd(), project_name)
    os.makedirs(output_dir, exist_ok=True)
    verbose_log(f"Creating project folder: {output_dir}")

    # Save chunk_0.txt
    chunk_0_path = os.path.join(output_dir, "chunk_0.txt")
    with open(chunk_0_path, "w", encoding="utf-8") as f:
        f.write("### Initial Instructions for ChatGPT ###\n")
        f.write("We are providing a large codebase in multiple chunks along with the folder structure.\n")
        f.write("Each chunk represents a part of the code and includes metadata such as file name and chunk number.\n")
        f.write("Please wait until all chunks are provided before analyzing the code.\n")
        f.write("Once all chunks are received, analyze the code to:\n")
        f.write("1. Understand how the code works as a whole.\n")
        f.write("2. Provide a basic explanation of its functionalities.\n")
        f.write("3. Memorize the full codebase (not as independent chunks).\n")
        f.write("After memorizing, follow the instructions for the specified action.\n")
        f.write("Folder Structure:\n")
        f.write(folder_structure)
    verbose_log(f"Saved initial instructions as {chunk_0_path}")

    # Save individual chunks
    file_counter = 1
    for relative_path, data in file_map.items():
        for chunk_number, chunk in enumerate(data["chunks"]):
            output_file = os.path.join(output_dir, f"chunk_{file_counter}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"File: {relative_path}\n")
                f.write(f"Chunk Number: {chunk_number + 1}\n")
                f.write("Content:\n")
                f.write(chunk)
            verbose_log(f"Saved chunk {chunk_number + 1} of {relative_path} as {output_file}")
            file_counter += 1

    # Save final instructions
    final_file = os.path.join(output_dir, f"chunk_{file_counter}.txt")
    formatted_action = action.replace("-", " ").title()  # Converts 'code-review' to 'Code Review'
    with open(final_file, "w", encoding="utf-8") as f:
        f.write("### Final Instructions for ChatGPT ###\n")
        f.write("All chunks have been provided.\n")
        f.write("You now have the complete project code and structure.\n")
        f.write("Memorize it completely, then perform the following action:\n")
        f.write(f"**Action: {formatted_action}**\n")
        if action == "summarize":
            f.write("Summarize the code, providing a high-level overview of its structure and main functionalities.\n")
        elif action == "analyze":
            f.write("Perform a detailed analysis of the code's functionalities, characteristics, and usage examples.\n")
        elif action == "improve":
            f.write("Provide suggestions and improvements that could enhance the code.\n")
        elif action == "explain":
            f.write("Explain the code in detail, including how it works, its functions, and the technologies/techniques used.\n")
        elif action == "code-review":
            f.write("Conduct a detailed code review from a pentester's perspective, highlighting vulnerabilities and fixes.\n")
        elif action == "usage":
            f.write("Generate usage examples for every functionality and argument, including explanations and expected responses.\n")
        elif action == "generate-readme":
            f.write("Create a downloadable `README.md` file containing purpose, description, installation, usage, and disclaimers.\n")
        elif action == "instructions":
            f.write("Provide detailed installation or compilation instructions for the application.\n")
            f.write("Include specific commands, dependencies, and any other requirements to set it up.\n")
    verbose_log(f"Saved final instructions as {final_file}")



def process_directory(directory, token_limit):
    """Processes each file in the directory, breaking code files into chunks."""
    file_map = {}
    verbose_log(f"Mapping directory structure for '{directory}'...")
    folder_structure = display_folder_structure(directory)
    verbose_log(folder_structure)

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            file_type = detect_file_type(file)

            if file_type == "code":
                # Process code files into chunks
                file_map[relative_path] = {"path": file_path, "chunks": get_file_chunks(file_path, token_limit)}
                verbose_log(f"Included for processing: {relative_path}")
            elif file_type == "auxiliary":
                # Log auxiliary files but do not chunk
                verbose_log(f"Auxiliary file (excluded from processing): {relative_path}")
            else:
                # Log other files
                verbose_log(f"Other file (excluded from processing): {relative_path}")

    verbose_log("Directory structure mapped successfully.\n")
    return file_map, folder_structure


def main():
    parser = argparse.ArgumentParser(
        description="Process a project directory for ChatGPT analysis.",
        formatter_class=argparse.RawTextHelpFormatter  
    )

    parser.add_argument(
        "--project", 
        type=str, 
        required=True, 
        help="Path to the project directory"
    )
    
    parser.add_argument(
        "--type", 
        type=str, 
        required=True, 
        choices=["api", "web"], 
        help=(
            "Mode of operation:\n"
            "  api  : Use the OpenAI API to process the code.\n"
            "  web  : Generate files for manual input into ChatGPT."
        )
    )
    
    parser.add_argument(
        "--action", 
        type=str, 
        required=True,
        choices=[
            "summarize", 
            "analyze", 
            "improve", 
            "explain", 
            "code-review", 
            "usage", 
            "generate-readme",
            "instructions"
        ],
        help=(
            "Specifies what ChatGPT should do with the code:\n"
            "  summarize      : Provide a high-level summary of the code.\n"
            "  analyze        : Perform a detailed analysis and provide usage examples.\n"
            "  improve        : Suggest improvements to the code.\n"
            "  explain        : Explain the code's functions and techniques in detail.\n"
            "  code-review    : Conduct a security-oriented code review.\n"
            "  usage          : Generate usage examples for all functionalities.\n"
            "  generate-readme: Create a `README.md` file for the project.\n"
            "  instructions   : Provide detailed installation or compilation instructions for the application.\n"
        )
    )

    args = parser.parse_args()

    # Remaining logic for handling arguments
    project_dir = args.project
    operation_type = args.type
    action = args.action

    # Step 1: Calculate dynamic token limit
    token_limit = calculate_dynamic_token_limit(project_dir)

    # Step 2: Process the directory
    file_map, folder_structure = process_directory(project_dir, token_limit)

    # Step 3: Handle based on type
    if operation_type == "api":
        verbose_log("API mode selected. Processing with OpenAI API...")
        process_with_api(file_map, folder_structure, action)
    elif operation_type == "web":
        verbose_log("Web mode selected. Creating files for manual input into ChatGPT...")
        project_name = os.path.basename(os.path.normpath(project_dir))
        save_chunks_to_files(project_name, folder_structure, file_map, action)

    verbose_log("\nScript processing completed.\n")


if __name__ == "__main__":
    main()
