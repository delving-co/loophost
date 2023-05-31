from typing import Any, Dict


def build(setup_kwargs: Dict[str, Any]) -> None:
    print("Inside the Build method")
    setup_kwargs.update(
        {
            "zip_safe": False,
        }
    )
