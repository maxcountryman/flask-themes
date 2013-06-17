import sys

PY2 = sys.version_info[0] == 2
_identity = lambda x: x

if PY2:
    implements_to_string = lambda x: x.__unicode__().encode('utf-8')
else:
    implements_to_string = lambda x: x
