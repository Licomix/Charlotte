# For media captions

def truncate_string(input_string: str, max_length: int = 1024) -> str:
    if len(input_string) > max_length:
        return input_string[:max_length]
    return input_string
