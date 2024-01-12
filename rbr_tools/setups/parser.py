import pyparsing as pp


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
    key_value_pair = (pp.Word(pp.alphanums + "_").setName("key") + 
                      (number_value ^ vector_value).setName("value"))
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