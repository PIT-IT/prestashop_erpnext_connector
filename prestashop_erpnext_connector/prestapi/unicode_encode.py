#!/usr/bin/env python
# -*- coding: utf-8 -*-

def unicode2encoding(text, encoding='utf-8'):
    if isinstance(text, str):
        try:
            text = text.encode(encoding)
        except Exception:
            pass
    return text

def encode(text, encoding='utf-8'):
    if isinstance(text, (str)):
        return unicode2encoding(text, encoding=encoding)
    return str(text)
