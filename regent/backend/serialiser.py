"""
Regent serialiser

Serialises a class's attributes to JSON
"""
from importlib import import_module
import json


def get_class_from_name(module_name, class_name):
    """
    Given a module and class name, return the class
    """
    module = import_module(module_name)
    if not hasattr(module, class_name):
        raise ValueError('Cannot serialise {} - not found in {}'.format(
            class_name, module_name,
        ))

    return getattr(module, class_name)


class Serialisable(object):
    def serialise(self):
        """
        Return a tuple representing this object instance

            (module_name, class_name, attrs)
        """
        module_name = self.__module__
        class_name = self.__class__.__name__

        # Test it's actually there
        get_class_from_name(module_name, class_name)

        # Serialise the attributes
        attrs = self.serialise_attrs()

        return (module_name, class_name, attrs)

    def serialise_attrs(self):
        """
        Serialise all instance attributes which don't start with an underscore
        """
        attrs = {k: v for k, v in vars(self).items() if not k.startswith('_')}
        return json.dumps()


def deserialise(module_name, class_name, attrs):
    """
    Return an instantiated Serialisable object which was previously serialised
    """
    cls = get_class_from_name(module_name, class_name)
    obj = cls()
    for key, value in attrs.items():
        setattr(obj, key, value)
    return obj
