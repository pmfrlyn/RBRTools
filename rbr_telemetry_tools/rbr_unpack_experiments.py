import pprint
from rbr_telemetry_tools import process_telemetry_packet, configure_map_index

TELEMETRY_PACKET = b"/\x07\x00\x00G\x00\x00\x00\x00\xbc\xbf<\x00\x00\x00\x00V\xd9\xbc?\xa8[\rE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\xe2\xa6x8Is\xee@\xa7a4B\xcd\xf4\x82@\xe3\x04Q?.\x1a\x8a\xbe=\x16\xb7B\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\xe85zD-0\xb5C9|\xb5C\x8e\xf3\xb3CA\nH>9 ?@\xbb\x88\x1eE\x9f\x12%;y\xb8\x1e\xc5\x00\x00\x00\x00\x00\x00\x00\x00_\x0bK5T\xf7!D\x0c\x07'D\x00\x00\x00\x00\x00\xd8VH3\x93\xabC\x15\x86\xabC\xf2\xfe\xaaC\x00\x00\x00\x00-n\x9fC\x00\x00\x00\x00\x93k\xaaC\x00\x00\x00\x00\x94k\xaaC\x00\x00\x00\x00\x95k\xaaC\x00\x00\x00\x00\x96k\xaaC\x00\x00\x00\x00\x97k\xaaC\x00\x00\x00\x00\xe5k\xaaC\x00\x00\x00\x00\xe6k\xaaC\x00\x00\x00\x00\x8aXH>9 ?\xc0o#\x1eE\xca_F<u\xf3\x1d\xc5\x00\x00\x00\x00\x00\x00\x00\x00\x96\x01t6T\xf7!D\x0c\x07'D\x00\x00\x00\x00\x00\xd8VH3\x93\xabC\x15\x86\xabC\x8e\xfb\xaaC\x00\x00\x00\x00\x85\xf2\x9eC\x00\x00\x00\x00\xabh\xaaC\x00\x00\x00\x00\xach\xaaC\x00\x00\x00\x00\xadh\xaaC\x00\x00\x00\x00\xaeh\xaaC\x00\x00\x00\x00\xafh\xaaC\x00\x00\x00\x00\x01i\xaaC\x00\x00\x00\x00\x01i\xaaC\x00\x00\x00\x00\xdf\x80K>\xb67\xd0\xc1\xfa\x84\x11EU\x00<\xbc\xba\xe4\x0f\xc5\x00\x00\x00\x00\x00\x00\x00\x00)\x05\x89\xb6P*%D\x85u'D\x00\x00\x00\x00\x00\xd8VH3\x93\xabC\x15\x86\xabC\xc2\x04\xabC\x00\x00\x00\x00\x97 \xa0C\x00\x00\x00\x00rp\xaaC\x00\x00\x00\x00sp\xaaC\x00\x00\x00\x00sp\xaaC\x00\x00\x00\x00sp\xaaC\x00\x00\x00\x00tp\xaaC\x00\x00\x00\x00\xc0p\xaaC\x00\x00\x00\x00\xc0p\xaaC\x00\x00\x00\x00\x03,H>\xb67\xd0All\x15E\xf5\xfb\x7f<\x9b\x0c\x17\xc5\x00\x00\x00\x00\x00\x00\x00\x007\x98\xad6P*%D\x85u'D\x00\x00\x00\x00\x00\xd8VH3\x93\xabC\xe7\x85\xabC~\xf8\xaaC\x07\x00\x00\x00\xc2\xc3\xa6C\x00\x00\x00\x00Hh\xaaC\x00\x00\x00\x00Ih\xaaC\x00\x00\x00\x00Jh\xaaC\x00\x00\x00\x00Lh\xaaC\x00\x00\x00\x00Mh\xaaC\x00\x00\x00\x00\xadh\xaaC\x00\x00\x00\x00\x96\x9b\x9fC\x00\x00\x00\x00"

configure_map_index("samples/Tracks.ini")

processed_data = process_telemetry_packet(TELEMETRY_PACKET, unit="C")

pprint.pprint({k: v for k, v in processed_data.items() if "stage" in k})

#RBR_MAPS_INI = "samples/Tracks.ini"

#import configparser

#config = configparser.ConfigParser()
#config.read(RBR_MAPS_INI)
#maps = {int(s[3:]): config[s]["StageName"].replace("\"", "") for s in config.sections() if "Map" in s and "StageName" in config[s]}

#print(maps)