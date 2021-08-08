from datetime import datetime
from typing import Any, Dict


class ValueNode:
    def __init__(self, value):
        self.value = value
        self.date_updated = datetime.now()

    def set_value(self, value):
        self.value = value
        self.date_updated = datetime.now()

    def get_value(self, value):
        return self.value


class Structure:
    def __init__(self):
        self._structure: Dict[Any, ValueNode] = {}
        self._set_all_node: ValueNode = None

    def get_val(self, index):
        if self._set_all_node and self._structure.get(index) and self._structure.get(index).date_updated < self._set_all_node.date_updated:
            return self._set_all_node.value
        else:
            if index in self._structure:
                return self._structure[index].value
            else:
                return None

    def set_val(self, index, value):
        self._structure[index] = ValueNode(value)

    def set_all(self, value):
        self._set_all_node = ValueNode(value)


s1 = Structure()
s1.set_val(1, 'green')
s1.set_val(5, 'blue')
s1.set_val(9, 'yellow')
print(s1.get_val(1))
print(s1.get_val(5))
print(s1.get_val('NotExistedValue'))
s1.set_all('black')
print(s1.get_val(1))
print(s1.get_val(5))
print(s1.get_val('NotExistedValue'))
