import unittest

from pyhocon import ConfigFactory

from databuilder.transformer.regex_str_replace_transformer import RegexStrReplaceTransformer


class TestRegexReplacement(unittest.TestCase):

    def test(self):
        # type: () -> None
        transformer = self._default_test_transformer()

        foo = Foo('abc')
        actual = transformer.transform(foo)

        self.assertEqual('bba', actual.val)

    def test_numeric_val(self):
        # type: () -> None
        transformer = self._default_test_transformer()

        foo = Foo(6)
        actual = transformer.transform(foo)

        self.assertEqual(6, actual.val)

    def test_none_val(self):
        # type: () -> None
        transformer = self._default_test_transformer()

        foo = Foo(None)
        actual = transformer.transform(foo)

        self.assertEqual(None, actual.val)

    def _default_test_transformer(self):
        # type: () -> RegexStrReplaceTransformer
        config = ConfigFactory.from_dict({
            'regex_replace_tuple_list': [('a', 'b'), ('c', 'a')],
            'attribute_name': 'val'
        })

        transformer = RegexStrReplaceTransformer()
        transformer.init(config)

        return transformer


class Foo(object):
    def __init__(self, val):
        # type: (str) -> None
        self.val = val


if __name__ == '__main__':
    unittest.main()
