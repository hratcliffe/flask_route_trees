## Flask Route Trees

Simple code to generate pretty graphs of the routing trees
for a flask app. Indentifies @route decorators and attempts
to form a tree from the url hierarchy. Flask placeholders
are handled partly heuristically, controllable through config.

The example app in examples/example.py demonstrates all possible
function, although some parts rely on a particular coding
style.


## Dependencies
astroid https://github.com/PyCQA/astroid for generating the syntax trees
graphviz https://pypi.python.org/pypi/graphviz for generating plots

