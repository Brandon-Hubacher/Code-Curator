from __future__ import annotations

import itertools as it
import math
import re
from pathlib import Path

from manim import Animation
from manim import Code
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename

from code_curator.animations.code_transform import CodeTransform
from code_curator.animations.singly_linked_list.transform_sll import TransformSinglyLinkedList
from code_curator.code.code_highlighter import CodeHighlighter
from code_curator.code.one_dark_colors import OneDarkStyle
from code_curator.code.python_lexer import MyPythonLexer


class CustomCode(Code):
    def __init__(
        self,
        file_name: str | None = None,
        tab_width: int = 1,
        indentation_chars: str = " ",
        font="Monospace",
        font_size=24,
        stroke_width=0,
        margin: float = 0.1,
        background: str | None = None,
        background_stroke_width: float = 0,
        background_stroke_color: str = "#FFFFFF",
        corner_radius=0.0,
        insert_line_no: bool = False,
        line_spacing: float = 0.5,
        line_no_buff: float = 0.2,
        # style: str = "nord",
        style: str = OneDarkStyle,
        language: str = "python",
        background_color: str | None = None,
        **kwargs,
    ) -> None:
        self.lexer = MyPythonLexer()
        super().__init__(
            file_name=file_name,
            tab_width=tab_width,
            indentation_chars=indentation_chars,
            font=font,
            font_size=font_size,
            stroke_width=stroke_width,
            margin=margin,
            background=background,
            background_stroke_width=background_stroke_width,
            background_stroke_color=background_stroke_color,
            corner_radius=corner_radius,
            insert_line_no=insert_line_no,
            line_spacing=line_spacing,
            line_no_buff=line_no_buff,
            style=style,
            language=language,
            **kwargs,
        )
        self.background_mobject.set_opacity(0)
        self._highlighter = None

        self.scale(0.5)

    @property
    def num_lines(self) -> int:
        return len(self.code)

    @property
    def max_line_height(self):
        # It looks like lines that immediately following an empty line have the height for both of them.
        #  So, exclude those lines.
        lines_to_consider = [self.code[0].height]
        for prev_line, curr_line in it.pairwise(self.code):
            if math.isclose(prev_line.height, 0):
                continue

            lines_to_consider.append(curr_line.height)

        return max(lines_to_consider)

    @property
    def max_line_width(self):
        # I want the max line width including the indentation chars at the beginning of a line
        min_starting_x = min(line.get_left()[0] for line in self.code)
        max_ending_x = max(line.get_right()[0] for line in self.code)
        return max_ending_x - min_starting_x

    @property
    def highlighter(self) -> CodeHighlighter:
        return self._highlighter

    @highlighter.setter
    def highlighter(self, highlighter: CodeHighlighter) -> None:
        self._highlighter = highlighter
        self._highlighter.code = self

    # TODO: Give better name than fade in. I'd like to have the entire mobject be on the screen just with 0 opacity
    #  So, fading in is misleading because it implies that it's not yet present on the screen.
    def fade_in_lines(self, *line_numbers: int) -> tuple[CustomCode, Animation]:
        copy = self._create_animation_copy()
        for line_no in line_numbers:
            copy.code[line_no].set_opacity(1)

        return copy, TransformSinglyLinkedList(self, copy)

    def fade_in_substring(self, substring: str, occurrence: int = 1) -> tuple[CustomCode, Animation]:
        copy = self._create_animation_copy()
        copy.get_code_substring(substring, occurrence=occurrence).set_opacity(1)
        return copy, TransformSinglyLinkedList(self, copy)

    def saturation_highlight_substring(self, substring: str, occurrence: int = 1) -> tuple[CustomCode, Animation]:
        copy = self._create_animation_copy()
        substring_start_index = self.get_substring_starting_index(substring, occurrence=occurrence)

        desaturate_opacity = 0.25
        copy.code.lines_text[:substring_start_index].set_opacity(desaturate_opacity)
        copy.code.lines_text[substring_start_index + len(substring) :].set_opacity(desaturate_opacity)

        return copy, TransformSinglyLinkedList(self, copy)

    def change_code_text(self, new_code_string: str) -> tuple[CustomCode, Animation]:
        copy = self._create_animation_copy()
        copy._original__init__(code=new_code_string)

        return CodeTransform(self, CustomCode(code=new_code_string))

    def get_substring_starting_index(self, substring: str, occurrence: int = 1, line_index: int | None = None) -> int:
        num_found: int = 0
        start_index: int = 0
        while True:
            start_index: int = self.code_string.find(substring, start_index)

            num_found += 1
            if num_found == occurrence:
                return start_index

            start_index += 1

    def get_code_substring(self, substring: str, occurrence: int = 1):
        start_index: int = self.get_substring_starting_index(substring, occurrence=occurrence)
        return self.code.lines_text[start_index : start_index + len(substring)]

    def get_line(self, line_number: int):
        return self.code[line_number - 1]

    def get_line_at(self, line_index: int):
        return self[2][line_index]

    def has_highlighter(self) -> bool:
        return self.highlighter is not None

    def create_highlighter(self):
        self.highlighter = CodeHighlighter(self)
        self.add(self.highlighter)
        return self.highlighter

    def move_highlighter(self, num_lines: int) -> None:
        return self.highlighter.move(num_lines)

    def move_highlighter_to_substring(self, substring: str, occurrence: int = 1, num_lines: int | None = None):
        return self.highlighter.move_to_substring(
            substring,
            occurrence=occurrence,
            num_lines=num_lines,
        )

    def set_background_color(self, color: str) -> None:
        self.background_mobject.set(color=color)

    def _create_animation_copy(self) -> CustomCode:
        attr_name = "_copy_for_animation"
        if not hasattr(self, attr_name):
            setattr(self, attr_name, self.copy())

        return getattr(self, attr_name)

    def _gen_html_string(self):
        """Function to generate html string with code highlighted and stores in variable html_string."""
        self.html_string = _hilite_me(
            self.code_string,
            self.language,
            self.style,
            self.insert_line_no,
            "border:solid gray;border-width:.1em .1em .1em .8em;padding:.2em .6em;",
            self.file_path,
            self.line_no_from,
            lexer=self.lexer
        )

        if self.generate_html_file:
            output_folder = Path() / "assets" / "codes" / "generated_html_files"
            output_folder.mkdir(parents=True, exist_ok=True)
            (output_folder / f"{self.file_name}.html").write_text(self.html_string)


def _insert_line_numbers_in_html(html: str, line_no_from: int):
    """Function that inserts line numbers in the highlighted HTML code.

    Parameters
    ---------
    html
        html string of highlighted code.
    line_no_from
        Defines the first line's number in the line count.

    Returns
    -------
    :class:`str`
        The generated html string with having line numbers.
    """
    match = re.search("(<pre[^>]*>)(.*)(</pre>)", html, re.DOTALL)
    if not match:
        return html
    pre_open = match.group(1)
    pre = match.group(2)
    pre_close = match.group(3)

    html = html.replace(pre_close, "</pre></td></tr></table>")
    numbers = range(line_no_from, line_no_from + pre.count("\n") + 1)
    format_lines = "%" + str(len(str(numbers[-1]))) + "i"
    lines = "\n".join(format_lines % i for i in numbers)
    html = html.replace(
        pre_open,
        "<table><tr><td>" + pre_open + lines + "</pre></td><td>" + pre_open,
        )
    return html


def _hilite_me(
        code: str,
        language: str,
        style: str,
        insert_line_no: bool,
        divstyles: str,
        file_path: Path,
        line_no_from: int,
        lexer,
):
    """Function to highlight code from string to html.

    Parameters
    ---------
    code
        Code string.
    language
        The name of the programming language the given code was written in.
    style
        Code style name.
    insert_line_no
        Defines whether line numbers should be inserted in the html file.
    divstyles
        Some html css styles.
    file_path
        Path of code file.
    line_no_from
        Defines the first line's number in the line count.
    """
    style = style or "colorful"
    defstyles = "overflow:auto;width:auto;"

    formatter = HtmlFormatter(
        style=style,
        linenos=False,
        noclasses=True,
        cssclass="",
        cssstyles=defstyles + divstyles,
        prestyles="margin: 0",
    )
    if language is None and file_path:
        # lexer = guess_lexer_for_filename(file_path, code)
        html = highlight(code, lexer, formatter)
    elif language is None:
        raise ValueError(
            "The code language has to be specified when rendering a code string",
        )
    else:
        html = highlight(code, get_lexer_by_name(language, **{}), formatter)
    if insert_line_no:
        html = _insert_line_numbers_in_html(html, line_no_from)
    html = "<!-- HTML generated by Code() -->" + html
    return html
