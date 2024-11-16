# GPTCodeFeeder

Streamlining large codebases for seamless GPT analysis.

## Purpose

**GPTCodeFeeder** is a tool designed to handle large project directories by splitting them into manageable chunks for processing by ChatGPT. Whether you're using the OpenAI API or manually interacting with ChatGPT, GPTCodeFeeder ensures your code is structured, optimized, and ready for analysis or interaction.

---

## Description

GPTCodeFeeder provides:
1. **Chunking Large Files**: Automatically splits large files into smaller, token-limited chunks for easy processing.
2. **Dynamic Optimization**: Dynamically calculates the optimal chunk size to minimize the number of chunks required.
3. **Multiple Modes**:
   - **API Mode**: Automatically sends chunks to OpenAI's API for analysis.
   - **Web Mode**: Prepares files for manual input into ChatGPT, including detailed instructions.
4. **Custom Actions**: Allows specifying what ChatGPT should do with the code, such as summarizing, analyzing, reviewing, or generating README files.
5. **Preserves Structure**: Provides a clear overview of your project directory structure for better understanding and context.

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/q3alique/GPTCodeFeeder.git
   ```
2. Navigate to the project folder:
   ```bash
   cd GPTCodeFeeder
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

GPTCodeFeeder can be run in two modes: **API** and **Web**.

### Basic Command
```bash
python GPTCodeFeeder.py --project <path-to-your-project> --type <api|web> --action <action>
```

### Parameters
- `--project`: Path to the project directory.
- `--type`: Mode of operation.
  - `api`  : Use the OpenAI API to process the code.
  - `web`  : Generate files for manual input into ChatGPT.
- `--action`: Specifies what ChatGPT should do with the code.
  - `summarize`      : Provide a high-level summary of the code.
  - `analyze`        : Perform a detailed analysis and provide usage examples.
  - `improve`        : Suggest improvements to the code.
  - `explain`        : Explain the code's functions and techniques in detail.
  - `code-review`    : Conduct a security-oriented code review.
  - `usage`          : Generate usage examples for all functionalities.
  - `generate-readme`: Create a `README.md` file for the project.
  - `instructions`   : Provide detailed installation or compilation instructions for the application.

---

### Examples

#### API Mode
```bash
python GPTCodeFeeder.py --project ./MyProject --type api --action summarize
```

#### Web Mode
```bash
python GPTCodeFeeder.py --project ./MyProject --type web --action code-review
```

---

## Disclaimers

1. **API Key**: Ensure you have a valid OpenAI API key when using API mode.
2. **Quota and Billing**: Using the OpenAI API may incur costs. Check your subscription and usage limits.
3. **Manual Input**: In Web mode, all chunks must be manually copied and pasted into ChatGPT for processing.
4. **Large Projects**: For extremely large projects, processing time and resources may vary.

---

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
