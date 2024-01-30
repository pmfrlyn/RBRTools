import rbr_tools.setups.parser as lsparser
from rbr_tools.setups import parse_lsp_file, CarSetup, SetupSection

import os.path

LSP_PATH = os.path.join("samples", "clio_tarmac_qubits.lsp")
                        
def test_parser_creation():
    the_parser = lsparser.lsp_parser()
    assert the_parser is not None


def test_parser_parses():
    carsetup = parse_lsp_file(LSP_PATH)
    assert isinstance(carsetup, CarSetup)

    assert isinstance(carsetup["Drive"], SetupSection)

def test_parser_parses_floats():
    carsetup = parse_lsp_file(LSP_PATH)
    assert isinstance(carsetup, CarSetup)
    assert isinstance(carsetup["Drive"]["CenterDiffMaxTorque"], float)