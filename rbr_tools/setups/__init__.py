from dataclasses import dataclass

from .parser import lsp_parser, SECTIONS

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

    return CarSetup.from_parser(results, setup_name)