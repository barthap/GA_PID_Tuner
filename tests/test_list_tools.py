import numpy as np
import unittest
import listtools


class TestListTools(unittest.TestCase):

    def test_normListSumTo(self):
        lista = [1, 2, 5, 2]
        list2 = listtools.normListSumTo(lista, 1)
        self.assertEqual(sum(list2), 1)
        self.assertListEqual(list2, [0.1, 0.2, 0.5, 0.2])

    def test_max_index_in_list(self):
        lista = [1, 2, 5, 2]
        idx = listtools.max_index_in_list(lista)
        self.assertEqual(idx, 2)

    def test_max_value_in_list(self):
        lista = [1, 2, 5, 2]
        idx = listtools.max_value_in_list(lista)
        self.assertEqual(idx, 5)

    def test_avg_of_list(self):
        lista = [1, 3, 4, 0]
        avg = listtools.avgList(lista)
        self.assertEqual(avg, 2.0)

    def test_chunks(self):
        lista = range(1, 25)
        chunks = np.array_split(lista, 10)
        print(chunks)