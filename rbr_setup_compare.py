#!/bin/env python3
import sys
from collections import defaultdict 

from rbr_tools.setups import parse_lsp_file

def main(): 
    if len(sys.argv) != 3:
        print("Usage rbr_setup_compare.py file1 file2")
        sys.exit(1)

    csetup = parse_lsp_file(sys.argv[1])
    csetup2 = parse_lsp_file(sys.argv[2])

    # compare setups
    diffs = defaultdict(list)

    for section_name, section_data in csetup.items():
        for key, value in section_data.items():
            if value != csetup2[section_name][key]:
                diffs[section_name].append((key, value, csetup2[section_name][key]))
        
    if not diffs:
        print("No differences")
        sys.exit()

    for section_name, diff in diffs.items():
        print("\n{}:".format(section_name))
        for dk, dv1, dv2 in diff:
            print("\t{}: {} -> {}".format(dk, dv1, dv2))
        

if __name__ == "__main__": 
    main()