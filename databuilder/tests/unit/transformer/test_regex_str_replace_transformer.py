import unittest

from pyhocon import ConfigFactory

from databuilder.transformer.regex_str_replace_transformer import RegexStrReplaceTransformer


class TestRegexReplacement(unittest.TestCase):

    def test(self):
        # type: () -> None
        config = ConfigFactory.from_dict({
            'regex_replace_tuple_list': [('a', 'b'), ('c', 'a')],
            'attribute_name': 'val'
        })

        transformer = RegexStrReplaceTransformer()
        transformer.init(config)

        foo = Foo('abc')
        actual = transformer.transform(foo)

        self.assertEqual('bba', actual.val)


class Foo(object):
    def __init__(self, val):
        # type: (str) -> None
        self.val = val


if __name__ == '__main__':
    unittest.main()
