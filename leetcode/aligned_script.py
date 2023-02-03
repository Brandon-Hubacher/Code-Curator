from __future__ import annotations

import json

from .aligned_word import AlignedWord

class AlignedScript:
    def __init__(self, text_data: dict):
        self._words = self._dict_to_words(text_data) if not self._dict_contains_aligned_words(text_data) else text_data

    def __str__(self):
        return json.dumps(self._words, indent=4, default=str)

    def get_word(self, word_number: int) -> AlignedWord:
        return self._words[word_number]

    def get_word_start(self, word_number: int) -> float:
        return self.get_word(word_number=word_number).start

    def get_word_end(self, word_number: int) -> float:
        return self.get_word(word_number=word_number).end

    def get_word_text(self, word_number: int) -> str:
        return self.get_word(word_number=word_number).text

    def get_word_duration(self, word_number: int) -> float:
        return self.get_word(word_number=word_number).duration

    def get_full_duration(self) -> float:
        index = 0
        first = 0
        last = 0
        for key in self._words:
            if index == 0:
                first = key
            if index == len(self._words) - 1:
                last = key
            index += 1
        return self.get_word_duration_from_to(first, last)

    def get_words_from_to(self, start: int, end: int) -> AlignedScript:
        ''' Inclusive bounds'''
        sub_dict = {}
        # sub_dict_index = 1
        for word_num in range(start, end + 1):
            # sub_dict[sub_dict_index] = self.get_word(word_num)
            sub_dict[word_num] = self.get_word(word_num)
            # sub_dict_index += 1
        return AlignedScript(text_data=sub_dict)

    def get_word_duration_from_to(self, start: int, end: int) -> float:
        return self.get_word_end(end) - self.get_word_start(start)

    def get_occurrences(self, text: str) -> Iterable[AlignedWord]:
        pass

    def _dict_contains_aligned_words(self, d: dict) -> boolean:
        for value in d.values():
            if isinstance(value, AlignedWord): return True
        return False

    def _dict_to_words(self, all_text_data: dict) -> dict[AlignedWord]:
        all_words_data = {}
        for word_num, text_data in all_text_data.items():
            if not isinstance(word_num, int): continue
            all_words_data[word_num] = AlignedWord(text_data)
        return all_words_data