"""A command-line interface for static code analysis using a language model from Google Vertex."""
import argparse
import json
import os
import sys
from pathlib import Path

import vertex_code_analysis.vertex_model as vertex_model


def run_analysis(path: Path):
    path = path.resolve().relative_to(os.getcwd())
    user_code = path.read_text()
    prompt = vertex_model.get_prompt_for_user_code(user_code)
    
    model = vertex_model.get_model()
    print('Querying Google Vertex API', file=sys.stderr)
    chat = model.start_chat(
        context=vertex_model.get_context_prompt(),
        **vertex_model.PROMPT_PARAMETERS)
    response_struct = chat.send_message(prompt)
    response_text = response_struct.text
    try:
        response = json.loads(response_text, strict=False)
    except json.decoder.JSONDecodeError:
        raise RuntimeError(f'Received an invalid JSON:\n{response_text}')
    response = response['suggestions']
    suggestions = _parse_response(response)
        
    for line_num, message in suggestions:
        print('{}:{}:0: warning: {}'.format(path, line_num, message))


def _parse_response(response: list) -> list:
    comments = []
    for block in response:
        if block['confidence'] < vertex_model.CONFIDENCE_THRESHOLD:
            continue
        line_num = block['code_line_num']
        message = block.get('replacement_code') or ''
        explaination = block.get('explanation') or ''
        if explaination:
            message += '  # ' + explaination
        message = message.replace('\n', ' ')
        comments.append((line_num, message))
    return comments
        

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path, metavar='script.py',
                        help='Path to .py file')
    args = parser.parse_args()
    if not args.path.is_file():
        raise FileNotFoundError(f'File {args.path} not found')
    
    run_analysis(args.path)


if __name__ == '__main__':
    main()
