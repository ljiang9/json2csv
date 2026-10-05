"""python -m json2csv 入口。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from json2csv import main

if __name__ == "__main__":
    main()
