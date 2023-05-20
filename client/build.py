from typing import Any, Dict
from setuptools import Extension


def build(setup_kwargs: Dict[str, Any]) -> None:
    print("Inside the Build method")
    setup_kwargs.update(
        {
            "zip_safe": False,
            "build_golang": {"root": "github.com/10in30/loophost"},
            "ext_modules": [
                Extension(
                    "loophost",
                    ["loophost/main.go"],
                    ["loophost/reverseproxy"],
                    py_limited_api=True,
                    define_macros=[("Py_LIMITED_API", None)],
                )
            ],
            "setup_requires": ["setuptools-golang"],
        }
    )
