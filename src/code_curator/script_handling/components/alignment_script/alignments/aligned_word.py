import json

class AlignedWord:
    def __init__(self, word_info: dict):
        self._start = word_info['start']
        self._end = word_info['end']
        self._text = word_info['text']
        self._duration = round(self._end - self._start, 2)

    def __str__(self):
        return f'word: {self._text}  start: {self._start}  end: {self._end}  duration: {self._duration}'

    def __repr__(self):
        return self._text

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def text(self):
        return self._text

    @property
    def duration(self):
        return self._duration