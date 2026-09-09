import unittest
from unittest.mock import patch
from logic.SDNF.minimized_pdnf_by_calculation_method import minimize_sdnf_by_calculation_method
from logic.SDNF.minimize_sdnf_by_spreadsheet_method import minimize_sdnf_by_spreadsheet_method
from logic.SDNF.minimize_sdnf_by_calculation_spreadsheet_method import minimize_sdnf_by_calculation_spreadsheet_method
from logic.SCNF.minimized_pcnf_by_calculation_method import minimize_sknf_by_calculation_method
from logic.SCNF.minimize_sсnf_by_spreadsheet_method import minimize_scnf_by_spreadsheet_method
from logic.SCNF.minimize_sсnf_by_calculation_spreadsheet_method import minimize_sсnf_by_calculation_spreadsheet_method

class MyTestCase(unittest.TestCase):

    def test_minimize_sdnf_by_calculation_method(self):
        result = minimize_sdnf_by_calculation_method("(!a&!b&!c)|(!a&b&!c)|(a&b&!c)")
        self.assertTrue(result == "b & !c | !a & !c" or result == "!a & !c | b & !c")

    def test_minimize_sdnf_by_spreadsheet_method(self):
        result = minimize_sdnf_by_spreadsheet_method("(!a&!b&!c)|(!a&b&!c)|(a&b&!c)")
        self.assertTrue(result == "b & !c | !a & !c" or result == "!a & !c | b & !c")

    def test_minimize_sdnf_by_calculation_spreadsheet_method(self):
        result = minimize_sdnf_by_calculation_spreadsheet_method("(!a&!b&!c)|(!a&b&!c)|(a&b&!c)")
        self.assertTrue(result == "b & !c | !a & !c" or result == "!a & !c | b & !c")

    def test_minimize_sknf_by_calculation_method(self):
        result = minimize_sknf_by_calculation_method("(a|b|!c)&(a|!b|!c)&(!a|b|c)&(!a|b|!c)&(!a|!b|!c)")
        self.assertTrue(result == "(!c) & (!a | b)" or result == "(!a | b) & (!c)")

    def test_minimize_scnf_by_spreadsheet_method(self):
        result = minimize_scnf_by_spreadsheet_method("(a|b|!c)&(a|!b|!c)&(!a|b|c)&(!a|b|!c)&(!a|!b|!c)")
        self.assertTrue(result == "(!c) & (!a | b)" or result == "(!a | b) & (!c)")

    def test_minimize_minimize_sсnf_by_calculation_spreadsheet_method(self):
        result = minimize_sсnf_by_calculation_spreadsheet_method("(a|b|!c)&(a|!b|!c)&(!a|b|c)&(!a|b|!c)&(!a|!b|!c)")
        self.assertTrue(result == "(!c) & (!a | b)" or result == "(!a | b) & (!c)")


# coverage run -m unittest discovercob
# coverage report -m