from ftw.linkchecker.accumulator import Accumulator
from ftw.linkchecker.tests import FunctionalTestCase


class TestLinksInTextArea(FunctionalTestCase):

    def test_if_paths_from_textareas_are_correctly_joined_type_1(self):
        obj = self.textarea
        url = 'foo'
        accumulator = Accumulator(self.portal)
        res_path = accumulator._create_path_even_if_there_are_parent_pointers(
            obj, url)

        self.assertEqual(
            res_path,
            '/plone/contentpage/foo',
            'It is expected, that paths like "foo" are appended to the parent'
            'of the textarea.')

    def test_if_paths_from_textareas_are_correctly_joined_type_2(self):
        obj = self.textarea
        url = './foo'
        accumulator = Accumulator(self.portal)
        res_path = accumulator._create_path_even_if_there_are_parent_pointers(
            obj, url)

        self.assertEqual(
            res_path,
            '/plone/contentpage/foo',
            'It is expected, that paths like "./foo" are appended to the '
            'parent of the textarea.')

    def test_if_paths_from_textareas_are_correctly_joined_type_3(self):
        obj = self.textarea
        url = '/foo'
        accumulator = Accumulator(self.portal)
        res_path = accumulator._create_path_even_if_there_are_parent_pointers(
            obj, url)

        self.assertEqual(
            res_path,
            '/plone/foo',
            'It is expected, that paths like "/foo" are appended to the site'
            'root.')

    def test_if_paths_from_textareas_are_correctly_joined_type_4(self):
        obj = self.textarea
        url = '../../../../foo'
        accumulator = Accumulator(self.portal)
        res_path = accumulator._create_path_even_if_there_are_parent_pointers(
            obj, url)

        self.assertEqual(
            res_path,
            '/plone/foo',
            'It is expected, that paths like "../../../../foo" (which point to'
            ' a parent further up than actually existing) are appended to the '
            'site root.')
