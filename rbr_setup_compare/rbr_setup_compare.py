#!/bin/env python3

from collections import defaultdict 
from dataclasses import dataclass
import pyparsing as pp
import sys

SECTIONS = [
    "Car",
    "Drive",
    "Engine",
    "VehicleControlUnit",
    "WheelLF",
    "WheelRF",
    "WheelLB",
    "WheelRB",
    "SpringDamperLF",
    "SpringDamperRF",
    "SpringDamperLB",
    "SpringDamperRB",
    "TyreLF",
    "TyreRF",
    "TyreLB",
    "TyreRB",
]

def lsp_section(section_name):
    number_value = pp.pyparsing_common.number()
    vector_value = (pp.pyparsing_common.number().setName("X") +
                    pp.pyparsing_common.number().setName("Y") +
                    pp.pyparsing_common.number().setName("Z"))
    
    section_id = pp.QuotedString(quoteChar="\"", unquoteResults=True).setName("section_id")
    key_value_pair = (pp.Word(pp.alphanums + "_").setName("key") + (number_value ^ vector_value).setName("value"))
    extra_key = pp.Word(pp.alphanums + "_").setName("extra_key")

    return pp.Group((pp.Literal(section_name).setName("section") +
                pp.Group(pp.nestedExpr(
                    content=pp.Group((
                        section_id ^
                        key_value_pair ^
                        extra_key
                    )).setName("KVPair")
                )
            ).setName("Values")))

def lsp_parser():
     return (
        pp.Literal("((") + pp.QuotedString(quoteChar="\"", unquoteResults=True).setName("header") +
            (
                pp.Or([lsp_section(secname) for secname in SECTIONS])
            )[len(SECTIONS),...] +
            pp.Literal("))")
        )

@dataclass
class Vector:
    x: float
    y: float
    z: float

    def __str__(self) -> str:
        return "{}, {}, {}".format(self.x, self.y, self.z)

class SetupSection(dict):
    def __init__(self, sect_name, sect_id):
        self.sect_name = sect_name
        self.sect_id = sect_id
        self.extrakeys = []

    def add_extra_key(self, keyname):
        self.extrakeys.append(keyname)

class CarSetup(dict):
    def __init__(self, name):
        self.name = name
        # initialize the sections
        self.update({section: None for section in SECTIONS})
        
    @staticmethod
    def from_parser(parser, name="default"):
        carsetup = CarSetup(name)

        for section in parser.asList()[2:-1]:
            section_name, sect_data = section[0], section[1:][0][0]
            section_id, setup_values = sect_data[0], sect_data[1:]
            
            carsetup[section_name] = SetupSection(section_name, section_id)
            for val in setup_values:
                if len(val) > 1:
                    continue
                carsetup[section_name].add_extra_key(val)
            
            for val in setup_values:
                if len(val) == 1:
                    continue
                if len(val) == 2: 
                    # normal key-value case
                    carsetup[section_name][val[0]] = val[1]
                elif len(val) == 4:
                    # vector case
                    carsetup[section_name][val[0]] = Vector(*val[1:])

        return carsetup

def parse_lsp_file(filename, setup_name="default"):
    setup_data = lsp_parser()

    with open(filename) as file:
        lsp_text = file.read()

    results = setup_data.parseString(lsp_text)

    return CarSetup.from_parser(results,)

def main(): 
    if len(sys.argv) != 3:
        print("Usage rbr_setup_compare.py file1 file2")
        exit(1)

    csetup = parse_lsp_file(sys.argv[1])
    csetup2 = parse_lsp_file(sys.argv[2])
    
    # compare setups
    diffs = defaultdict(list)

    for section_name, section_data in csetup.items():
        # compare
        for key, value in section_data.items():
            if value != csetup2[section_name][key]:
                diffs[section_name].append((key, value, csetup2[section_name][key]))
        
    if not diffs:
        print("No differences")
        exit

    for section_name, diff in diffs.items():
        print("{}:".format(section_name))
        for dk, dv1, dv2 in diff:
            print("\t{}: {} -> {}".format(dk, dv1, dv2))
        
if __name__ == "__main__": 
    main()