import sys

PY2 = sys.version_info[0] == 2

if PY2:
    implements_to_string = lambda x: x.encode('utf-8')
else:
    implements_to_string = lambda x: x
