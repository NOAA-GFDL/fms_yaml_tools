# Following information from PEP 440 (https://peps.python.org/pep-0440/)
__version__ = "2022.02.dev1"


class TableParseError(Exception):
    """Excpetion when error hit while converting a *_table file
       to YAML"""

    def __init__(self, file, lineno, line, message=None):
        self.file = file
        self.lineno = lineno
        self.line = line

        if message is None:
            self.message = f"Parse error: file: {self.file}({self.lineno}\n"
            self.message += f"line: {self.line}"
        else:
            self.message = message

    def __str__(self):
        return self.message
