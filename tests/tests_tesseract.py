import codecs
from PIL import Image
import os
import sys
sys.path = ["src"] + sys.path
import tempfile

import unittest

from pyocr import builders
from pyocr import tesseract


class TestContext(unittest.TestCase):
    """
    These tests make sure the requirements for the tests are met.
    """
    def setUp(self):
        pass

    def test_available(self):
        self.assertTrue(tesseract.is_available(),
                        "Tesseract not found. Is it installed ?")

    def test_version(self):
        self.assertTrue(tesseract.get_version() in (
            (3, 2, 1),
            (3, 2, 2),
            (3, 3, 0),
        ), ("Tesseract does not have the expected version"
            " (3.3.0) ! Some tests will be skipped !"))

    def test_langs(self):
        langs = tesseract.get_available_languages()
        self.assertTrue("eng" in langs,
                        ("English training does not appear to be installed."
                         " (required for the tests)"))
        self.assertTrue("fra" in langs,
                        ("French training does not appear to be installed."
                         " (required for the tests)"))
        self.assertTrue("jpn" in langs,
                        ("Japanese training does not appear to be installed."
                         " (required for the tests)"))

    def tearDown(self):
        pass


class TestTxt(unittest.TestCase):
    """
    These tests make sure the "usual" OCR works fine. (the one generating
    a .txt file)
    """
    def setUp(self):
        pass

    def __test_txt(self, image_file, expected_output_file, lang='eng'):
        image_file = "tests/data/" + image_file
        expected_output_file = "tests/tesseract/" + expected_output_file

        expected_output = ""
        with codecs.open(expected_output_file, 'r', encoding='utf-8') \
                as file_descriptor:
            for line in file_descriptor:
                expected_output += line
        expected_output = expected_output.strip()

        output = tesseract.image_to_string(Image.open(image_file), lang=lang)

        self.assertEqual(output, expected_output)

    def test_basic(self):
        self.__test_txt('test.png', 'test.txt')

    @unittest.skipIf(tesseract.get_version() not in (
        (3, 2, 1),
        (3, 2, 2),
        (3, 3, 0),
    ), "This test only works with Tesseract 3.02.1")
    def test_european(self):
        self.__test_txt('test-european.jpg', 'test-european.txt')

    @unittest.skipIf(tesseract.get_version() not in (
        (3, 2, 1),
        (3, 2, 2),
        (3, 3, 0),
    ), "This test only works with Tesseract 3.02.1")
    def test_french(self):
        self.__test_txt('test-french.jpg', 'test-french.txt', 'fra')

    def test_japanese(self):
        self.__test_txt('test-japanese.jpg', 'test-japanese.txt', 'jpn')

    def tearDown(self):
        pass


class TestCharBox(unittest.TestCase):
    """
    These tests make sure that Tesseract box handling works fine.
    """
    def setUp(self):
        self.builder = tesseract.CharBoxBuilder()

    def __test_txt(self, image_file, expected_box_file, lang='eng'):
        image_file = "tests/data/" + image_file
        expected_box_file = "tests/tesseract/" + expected_box_file

        with codecs.open(expected_box_file, 'r', encoding='utf-8') \
                as file_descriptor:
            expected_boxes = self.builder.read_file(file_descriptor)
        expected_boxes.sort()

        boxes = tesseract.image_to_string(Image.open(image_file), lang=lang,
                                          builder=self.builder)
        boxes.sort()

        self.assertEqual(len(boxes), len(expected_boxes))

        for i in range(0, min(len(boxes), len(expected_boxes))):
            self.assertEqual(boxes[i], expected_boxes[i])

    def test_basic(self):
        self.__test_txt('test.png', 'test.box')

    def test_european(self):
        self.__test_txt('test-european.jpg', 'test-european.box')

    def test_french(self):
        self.__test_txt('test-french.jpg', 'test-french.box', 'fra')

    @unittest.skipIf(tesseract.get_version() not in (
        (3, 2, 1),
        (3, 2, 2),
        (3, 3, 0),
    ), "This test requires Tesseract 3.02.1")
    def test_japanese(self):
        self.__test_txt('test-japanese.jpg', 'test-japanese.box', 'jpn')

    def test_write_read(self):
        original_boxes = tesseract.image_to_string(
            Image.open("tests/data/test.png"), builder=self.builder)
        self.assertTrue(len(original_boxes) > 0)

        (file_descriptor, tmp_path) = tempfile.mkstemp()
        try:
            # we must open the file with codecs.open() for utf-8 support
            os.close(file_descriptor)

            with codecs.open(tmp_path, 'w', encoding='utf-8') as fdescriptor:
                self.builder.write_file(fdescriptor, original_boxes)

            with codecs.open(tmp_path, 'r', encoding='utf-8') as fdescriptor:
                new_boxes = self.builder.read_file(fdescriptor)

            self.assertEqual(len(new_boxes), len(original_boxes))
            for i in range(0, len(original_boxes)):
                self.assertEqual(new_boxes[i], original_boxes[i])
        finally:
            os.remove(tmp_path)

    def tearDown(self):
        pass


class TestDigits(unittest.TestCase):
    """
    These tests make sure that Tesseract digits handling works fine.
    """
    def setUp(self):
        self.builder = tesseract.DigitBuilder()

    def __test_text(self, image_file, expected_output_file, lang='eng'):
        image_file = "tests/data/" + image_file
        expected_output_file = "tests/tesseract/" + expected_output_file

        expected_output = ""
        with codecs.open(expected_output_file, 'r', encoding='utf-8') \
                as file_descriptor:
            for line in file_descriptor:
                expected_output += line
        expected_output = expected_output.strip()

        output = tesseract.image_to_string(Image.open(image_file), lang=lang,
                                           builder=self.builder)

        self.assertEqual(output, expected_output)

    def test_digits(self):
        self.__test_text('test-digits.png', 'test-digits.txt')


class TestWordBox(unittest.TestCase):
    """
    These tests make sure that Tesseract box handling works fine.
    """
    def setUp(self):
        self.builder = builders.WordBoxBuilder()

    def __test_txt(self, image_file, expected_box_file, lang='eng'):
        image_file = "tests/data/" + image_file
        expected_box_file = "tests/tesseract/" + expected_box_file

        with codecs.open(expected_box_file, 'r', encoding='utf-8') \
                as file_descriptor:
            expected_boxes = self.builder.read_file(file_descriptor)
        expected_boxes.sort()

        boxes = tesseract.image_to_string(Image.open(image_file), lang=lang,
                                          builder=self.builder)
        boxes.sort()

        self.assertTrue(len(boxes) > 0)
        self.assertEqual(len(boxes), len(expected_boxes))

        for i in range(0, min(len(boxes), len(expected_boxes))):
            try:
                # python 2.7
                self.assertEqual(type(expected_boxes[i].content), unicode)
                self.assertEqual(type(boxes[i].content), unicode)
            except NameError:
                # python 3
                self.assertEqual(type(expected_boxes[i].content), str)
                self.assertEqual(type(boxes[i].content), str)
            self.assertEqual(boxes[i], expected_boxes[i])

    def test_basic(self):
        self.__test_txt('test.png', 'test.words')

    def test_european(self):
        self.__test_txt('test-european.jpg', 'test-european.words')

    def test_french(self):
        self.__test_txt('test-french.jpg', 'test-french.words', 'fra')

    @unittest.skipIf(tesseract.get_version() not in (
        (3, 2, 1),
        (3, 2, 2),
        (3, 3, 0),
    ), "This test requires Tesseract 3.02.1")
    def test_japanese(self):
        self.__test_txt('test-japanese.jpg', 'test-japanese.words', 'jpn')

    def test_write_read(self):
        original_boxes = tesseract.image_to_string(
            Image.open("tests/data/test.png"), builder=self.builder)
        self.assertTrue(len(original_boxes) > 0)

        (file_descriptor, tmp_path) = tempfile.mkstemp()
        try:
            # we must open the file with codecs.open() for utf-8 support
            os.close(file_descriptor)

            with codecs.open(tmp_path, 'w', encoding='utf-8') as fdescriptor:
                self.builder.write_file(fdescriptor, original_boxes)

            with codecs.open(tmp_path, 'r', encoding='utf-8') as fdescriptor:
                new_boxes = self.builder.read_file(fdescriptor)

            self.assertEqual(len(new_boxes), len(original_boxes))
            for i in range(0, len(original_boxes)):
                self.assertEqual(new_boxes[i], original_boxes[i])
        finally:
            os.remove(tmp_path)

    def tearDown(self):
        pass


class TestLineBox(unittest.TestCase):
    """
    These tests make sure that Tesseract box handling works fine.
    """
    def setUp(self):
        self.builder = builders.LineBoxBuilder()

    def __test_txt(self, image_file, expected_box_file, lang='eng'):
        image_file = "tests/data/" + image_file
        expected_box_file = "tests/tesseract/" + expected_box_file

        boxes = tesseract.image_to_string(Image.open(image_file), lang=lang,
                                          builder=self.builder)
        boxes.sort()

        with codecs.open(expected_box_file, 'r', encoding='utf-8') \
                as file_descriptor:
            expected_boxes = self.builder.read_file(file_descriptor)
        expected_boxes.sort()

        self.assertEqual(len(boxes), len(expected_boxes))

        for i in range(0, min(len(boxes), len(expected_boxes))):
            for j in range(0, len(boxes[i].word_boxes)):
                self.assertEqual(type(boxes[i].word_boxes[j]),
                                 type(expected_boxes[i].word_boxes[j]))
            self.assertEqual(boxes[i], expected_boxes[i])

    def test_basic(self):
        self.__test_txt('test.png', 'test.lines')

    def test_european(self):
        self.__test_txt('test-european.jpg', 'test-european.lines')

    def test_french(self):
        self.__test_txt('test-french.jpg', 'test-french.lines', 'fra')

    @unittest.skipIf(tesseract.get_version() not in (
        (3, 2, 1),
        (3, 2, 2),
        (3, 3, 0),
    ), "This test requires Tesseract 3.02.1")
    def test_japanese(self):
        self.__test_txt('test-japanese.jpg', 'test-japanese.lines', 'jpn')

    def test_write_read(self):
        original_boxes = tesseract.image_to_string(
            Image.open("tests/data/test.png"), builder=self.builder)
        self.assertTrue(len(original_boxes) > 0)

        (file_descriptor, tmp_path) = tempfile.mkstemp()
        try:
            # we must open the file with codecs.open() for utf-8 support
            os.close(file_descriptor)

            with codecs.open(tmp_path, 'w', encoding='utf-8') as fdescriptor:
                self.builder.write_file(fdescriptor, original_boxes)

            with codecs.open(tmp_path, 'r', encoding='utf-8') as fdescriptor:
                new_boxes = self.builder.read_file(fdescriptor)

            self.assertEqual(len(new_boxes), len(original_boxes))
            for i in range(0, len(original_boxes)):
                self.assertEqual(new_boxes[i], original_boxes[i])
        finally:
            os.remove(tmp_path)

    def tearDown(self):
        pass


class TestOrientation(unittest.TestCase):
    def test_can_detect_orientation(self):
        self.assertTrue(tesseract.can_detect_orientation())

    def test_orientation_0(self):
        img = Image.open('tests/data/test.png')
        result = tesseract.detect_orientation(img, lang='eng')
        self.assertEqual(result['angle'], 0)

    def test_orientation_90(self):
        img = Image.open('tests/data/test-90.png')
        result = tesseract.detect_orientation(img, lang='eng')
        self.assertEqual(result['angle'], 90)


def get_all_tests():
    all_tests = unittest.TestSuite()

    test_names = [
        'test_available',
        'test_version',
        'test_langs',
    ]
    tests = unittest.TestSuite(map(TestContext, test_names))
    all_tests.addTest(tests)

    test_names = [
        'test_basic',
        'test_european',
        'test_french',
    ]
    tests = unittest.TestSuite(map(TestTxt, test_names))
    all_tests.addTest(tests)

    test_names = [
        'test_basic',
        'test_european',
        'test_french',
        'test_japanese',
        'test_write_read',
    ]
    tests = unittest.TestSuite(map(TestCharBox, test_names))
    all_tests.addTest(tests)
    tests = unittest.TestSuite(map(TestWordBox, test_names))
    all_tests.addTest(tests)
    tests = unittest.TestSuite(map(TestLineBox, test_names))
    all_tests.addTest(tests)

    test_names = [
        'test_digits'
    ]
    tests = unittest.TestSuite(map(TestDigits, test_names))
    all_tests.addTest(tests)

    test_names = [
        'test_can_detect_orientation',
        'test_orientation_0',
        'test_orientation_90',
    ]
    tests = unittest.TestSuite(map(TestOrientation, test_names))
    all_tests.addTest(tests)

    return all_tests
