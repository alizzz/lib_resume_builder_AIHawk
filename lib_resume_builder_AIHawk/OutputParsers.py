from __future__ import annotations
from langchain_core.output_parsers.list import ListOutputParser

import re
from abc import abstractmethod
from collections import deque
from typing import AsyncIterator, Deque, Iterator, List, TypeVar, Union, Optional
from pydantic import BaseModel

from langchain_core.messages import BaseMessage
from langchain_core.output_parsers.transform import BaseTransformOutputParser

T = TypeVar("T")


class DelimitedListOutputParser(ListOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""
    delimiter:Optional[str]='\n'

    def __init__(self, delimiter=None, **kwargs):
        # Set delimiter manually, without calling super().__init__()
        object.__setattr__(self, "delimiter", delimiter)

        # Initialize the parent with the remaining kwargs
        super().__init__(**kwargs)

    def set_delimiter(self, delimiter = '\n'):
        self.delimiter = delimiter

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Check if the langchain object is serializable.
        Returns True."""
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object.

        Returns:
            A list of strings.
            Default is ["langchain", "output_parsers", "list"].
        """
        return ["langchain", "output_parsers", "list"]

    def get_format_instructions(self) -> str:
        """Return the format instructions for the comma-separated list output."""
        return (
            f"Your response should be a list of values, delimited by `{self.delimiter}`\n"
            f"eg: `foo{self.delimiter} bar{self.delimiter} baz` or `foo{self.delimiter}bar{self.delimiter}baz`\n"
            f"Do not output ``` or any other delimeters or placeholder with exception only {self.delimiter}"
        )

    def parse(self, text: str) -> List[str]:
        """Parse the output of an LLM call.

        Args:
            text: The output of an LLM call.

        Returns:
            A list of strings.
        """
        return [part.strip() for part in text.split(self.delimiter) if part]

    @property
    def _type(self) -> str:
        return "delimiter-separated-list"

