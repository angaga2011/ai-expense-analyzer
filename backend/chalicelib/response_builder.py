def build_success_response(data: dict, message: str = "Document analyzed successfully.") -> dict:
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def build_error_response(message: str) -> dict:
    return {
        "success": False,
        "message": message,
    }
