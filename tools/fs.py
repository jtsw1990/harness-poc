'''Set of tools for manipulating the file system.'''


write_file_tool = {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file at the specified path. Use this when the user asks you to create or edit a file. Always use this tool instead of trying to format the answer as a file content. Only use this tool once and more more than once in a loop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file"
                    }
                }, "required": ["path", "content"]
            }
        }
    }


def write_file(path: str, content: str) -> str:
    print("tool has been called")
    '''Write content to a file at the specified path.'''
    with open(path, 'w') as f:
        f.write(content)

    return f'File written to {path} with content: {content}'