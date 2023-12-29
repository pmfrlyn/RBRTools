import struct
import binascii

var = b"/\x07\x00\x00G\x00\x00\x00\x00\xbc\xbf<\x00\x00\x00\x00V\xd9\xbc?\xa8[\rE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\xe2\xa6x8Is\xee@\xa7a4B\xcd\xf4\x82@\xe3\x04Q?.\x1a\x8a\xbe=\x16\xb7B\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\xe85zD-0\xb5C9|\xb5C\x8e\xf3\xb3CA\nH>9 ?@\xbb\x88\x1eE\x9f\x12%;y\xb8\x1e\xc5\x00\x00\x00\x00\x00\x00\x00\x00_\x0bK5T\xf7!D\x0c\x07'D\x00\x00\x00\x00\x00\xd8VH3\x93\xabC\x15\x86\xabC\xf2\xfe\xaaC\x00\x00\x00\x00-n\x9fC\x00\x00\x00\x00\x93k\xaaC\x00\x00\x00\x00\x94k\xaaC\x00\x00\x00\x00\x95k\xaaC\x00\x00\x00\x00\x96k\xaaC\x00\x00\x00\x00\x97k\xaaC\x00\x00\x00\x00\xe5k\xaaC\x00\x00\x00\x00\xe6k\xaaC\x00\x00\x00\x00\x8aXH>9 ?\xc0o#\x1eE\xca_F<u\xf3\x1d\xc5\x00\x00\x00\x00\x00\x00\x00\x00\x96\x01t6T\xf7!D\x0c\x07'D\x00\x00\x00\x00\x00\xd8VH3\x93\xabC\x15\x86\xabC\x8e\xfb\xaaC\x00\x00\x00\x00\x85\xf2\x9eC\x00\x00\x00\x00\xabh\xaaC\x00\x00\x00\x00\xach\xaaC\x00\x00\x00\x00\xadh\xaaC\x00\x00\x00\x00\xaeh\xaaC\x00\x00\x00\x00\xafh\xaaC\x00\x00\x00\x00\x01i\xaaC\x00\x00\x00\x00\x01i\xaaC\x00\x00\x00\x00\xdf\x80K>\xb67\xd0\xc1\xfa\x84\x11EU\x00<\xbc\xba\xe4\x0f\xc5\x00\x00\x00\x00\x00\x00\x00\x00)\x05\x89\xb6P*%D\x85u'D\x00\x00\x00\x00\x00\xd8VH3\x93\xabC\x15\x86\xabC\xc2\x04\xabC\x00\x00\x00\x00\x97 \xa0C\x00\x00\x00\x00rp\xaaC\x00\x00\x00\x00sp\xaaC\x00\x00\x00\x00sp\xaaC\x00\x00\x00\x00sp\xaaC\x00\x00\x00\x00tp\xaaC\x00\x00\x00\x00\xc0p\xaaC\x00\x00\x00\x00\xc0p\xaaC\x00\x00\x00\x00\x03,H>\xb67\xd0All\x15E\xf5\xfb\x7f<\x9b\x0c\x17\xc5\x00\x00\x00\x00\x00\x00\x00\x007\x98\xad6P*%D\x85u'D\x00\x00\x00\x00\x00\xd8VH3\x93\xabC\xe7\x85\xabC~\xf8\xaaC\x07\x00\x00\x00\xc2\xc3\xa6C\x00\x00\x00\x00Hh\xaaC\x00\x00\x00\x00Ih\xaaC\x00\x00\x00\x00Jh\xaaC\x00\x00\x00\x00Lh\xaaC\x00\x00\x00\x00Mh\xaaC\x00\x00\x00\x00\xadh\xaaC\x00\x00\x00\x00\x96\x9b\x9fC\x00\x00\x00\x00"

# based on the struct found in rbr.telemetry.data.TelemetryData.h
FORMAT_INFO = (
    ("<", ""),                         #little endian                    
    ("I", "general.total_steps"),
    ("i", "stage.index"),
    ("f", "stage.progress"),
    ("f", "stage.total_race_time"),    #seconds?
    ("f", "stage.drive_line_location"),
    ("f", "stage.distance_to_end"),    #meters or feet(?) depending on config
 
    ("f", "control.steering_input"),
    ("f", "control.throttle_input"),
    ("f", "control.brake_input"),
    ("f", "control.handbrake_input"),
    ("f", "control.clutch_input"),
    ("i", "control.current_gear"),
    ("f", "control.brake_pressure"),
    ("f", "control.handbrake_pressure"),
 
    ("i", "car.index"),
    ("f", "car.speed"),                               #in mph or kmh depending on config
    ("f", "car.position_x"),
    ("f", "car.position_y"),
    ("f", "car.position_z"),
    ("f", "car.roll"),
    ("f", "car.pitch"),
    ("f", "car.yaw"),
 
    ("f", "car.velocities.surge"),
    ("f", "car.velocities.sway"),
    ("f", "car.velocities.heave"),
    ("f", "car.velocities.roll"),
    ("f", "car.velocities.pitch"),
    ("f", "car.velocities.yaw"),
    
    ("f", "car.accelerations.surge"),
    ("f", "car.accelerations.sway"),
    ("f", "car.accelerations.heave"),
    ("f", "car.accelerations.roll"),
    ("f", "car.accelerations.pitch"),
    ("f", "car.accelerations.yaw"),       
    
    ("f", "engine.rpm"),
    ("f", "engine.radiatorCoolantTemperature"),       #kelvin
    ("f", "engine.engineCoolantTemperature"),         #kelvin
    ("f", "engine.engineTemperature"),                #kelvin
    
    ("f", "suspension.lf.spring_deflection"),
    ("f", "suspension.lf.rollbar_force"),
    ("f", "suspension.lf.spring_force"),
    ("f", "suspension.lf.damper_force"),
    ("f", "suspension.lf.strut_force"),
    ("i", "suspension.lf.helper_spring_is_active"),
    
    ("f", "suspension.lf.damper.damage"),
    ("f", "suspension.lf.damper.pistonvelocity"),
    
    ("f", "suspension.lf.brake.layertemperature"),    #kelvin?
    ("f", "suspension.lf.brake.temperature"),         #kelvin?
    ("f", "suspension.lf.brake.wear"),
    
    ("f", "suspension.lf.tire.pressure"),
    ("f", "suspension.lf.tire.temperature"),
    ("f", "suspension.lf.tire.carcassTemperature"),
    ("f", "suspension.lf.tire.treadTemperature"),
    ("I", "suspension.lf.tire.currentSegment"),
    
    ("f", "suspension.lf.tire.segment1.temperature"),
    ("f", "suspension.lf.tire.segment1.wear"),
    
    ("f", "suspension.lf.tire.segment2.temperature"),
    ("f", "suspension.lf.tire.segment2.wear"),
    
    ("f", "suspension.lf.tire.segment3.temperature"),
    ("f", "suspension.lf.tire.segment3.wear"),
    
    ("f", "suspension.lf.tire.segment4.temperature"),
    ("f", "suspension.lf.tire.segment4.wear"),
    
    ("f", "suspension.lf.tire.segment5.temperature"),
    ("f", "suspension.lf.tire.segment5.wear"),
    
    ("f", "suspension.lf.tire.segment6.temperature"),
    ("f", "suspension.lf.tire.segment6.wear"),
    
    ("f", "suspension.lf.tire.segment7.temperature"),
    ("f", "suspension.lf.tire.segment7.wear"),
    
    ("f", "suspension.lf.tire.segment8.temperature"),
    ("f", "suspension.lf.tire.segment8.wear"),
    
    ("f", "suspension.rf.spring_deflection"),
    ("f", "suspension.rf.rollbar_force"),
    ("f", "suspension.rf.spring_force"),
    ("f", "suspension.rf.damper_force"),
    ("f", "suspension.rf.strut_force"),
    ("i", "suspension.rf.helper_spring_is_active"),
    
    ("f", "suspension.rf.damper.damage"),
    ("f", "suspension.rf.damper.pistonvelocity"),
    
    ("f", "suspension.rf.brake.layertemperature "),
    ("f", "suspension.rf.brake.temperature"),
    ("f", "suspension.rf.brake.wear"),
    
    ("f", "suspension.rf.tire.pressure"),
    ("f", "suspension.rf.tire.temperature"),
    ("f", "suspension.rf.tire.carcassTemperature"),
    ("f", "suspension.rf.tire.treadTemperature"),
    ("I", "suspension.rf.tire.currentSegment"),
    
    ("f", "suspension.rf.tire.segment1.temperature"),
    ("f", "suspension.rf.tire.segment1.wear"),
    
    ("f", "suspension.rf.tire.segment2.temperature"),
    ("f", "suspension.rf.tire.segment2.wear"),
    
    ("f", "suspension.rf.tire.segment3.temperature"),
    ("f", "suspension.rf.tire.segment3.wear"),
    
    ("f", "suspension.rf.tire.segment4.temperature"),
    ("f", "suspension.rf.tire.segment4.wear"),
    
    ("f", "suspension.rf.tire.segment5.temperature"),
    ("f", "suspension.rf.tire.segment5.wear"),
    
    ("f", "suspension.rf.tire.segment6.temperature"),
    ("f", "suspension.rf.tire.segment6.wear"),
    
    ("f", "suspension.rf.tire.segment7.temperature"),
    ("f", "suspension.rf.tire.segment7.wear"),
    
    ("f", "suspension.rf.tire.segment8.temperature"),
    ("f", "suspension.rf.tire.segment8.wear"),
    
    ("f", "suspension.lb.spring_deflection"),
    ("f", "suspension.lb.rollbar_force"),
    ("f", "suspension.lb.spring_force"),
    ("f", "suspension.lb.damper_force"),
    ("f", "suspension.lb.strut_force"),
    ("i", "suspension.lb.helper_spring_is_active"),
    
    ("f", "suspension.lb.damper.damage"),
    ("f", "suspension.lb.damper.pistonvelocity"),
    
    ("f", "suspension.lb.brake.layertemperature "),
    ("f", "suspension.lb.brake.temperature"),
    ("f", "suspension.lb.brake.wear"),
    
    ("f", "suspension.lb.tire.pressure"),
    ("f", "suspension.lb.tire.temperature"),
    ("f", "suspension.lb.tire.carcassTemperature"),
    ("f", "suspension.lb.tire.treadTemperature"),
    ("I", "suspension.lb.tire.currentSegment"),
    
    ("f", "suspension.lb.tire.segment1.temperature"),
    ("f", "suspension.lb.tire.segment1.wear"),
    
    ("f", "suspension.lb.tire.segment2.temperature"),
    ("f", "suspension.lb.tire.segment2.wear"),
    
    ("f", "suspension.lb.tire.segment3.temperature"),
    ("f", "suspension.lb.tire.segment3.wear"),
    
    ("f", "suspension.lb.tire.segment4.temperature"),
    ("f", "suspension.lb.tire.segment4.wear"),
    
    ("f", "suspension.lb.tire.segment5.temperature"),
    ("f", "suspension.lb.tire.segment5.wear"),
    
    ("f", "suspension.lb.tire.segment6.temperature"),
    ("f", "suspension.lb.tire.segment6.wear"),
    
    ("f", "suspension.lb.tire.segment7.temperature"),
    ("f", "suspension.lb.tire.segment7.wear"),
    
    ("f", "suspension.lb.tire.segment8.temperature"),
    ("f", "suspension.lb.tire.segment8.wear"),

    ("f", "suspension.rb.spring_deflection"),
    ("f", "suspension.rb.rollbar_force"),
    ("f", "suspension.rb.spring_force"),
    ("f", "suspension.rb.damper_force"),
    ("f", "suspension.rb.strut_force"),
    ("i", "suspension.rb.helper_spring_is_active"),
   
    ("f", "suspension.rb.damper.damage"),
    ("f", "suspension.rb.damper.pistonvelocity"),
   
    ("f", "suspension.rb.brake.layertemperature "),
    ("f", "suspension.rb.brake.temperature"),
    ("f", "suspension.rb.brake.wear"),
   
    ("f", "suspension.rb.tire.pressure"),
    ("f", "suspension.rb.tire.temperature"),
    ("f", "suspension.rb.tire.carcassTemperature"),
    ("f", "suspension.rb.tire.treadTemperature"),
    ("I", "suspension.rb.tire.currentSegment"),
   
    ("f", "suspension.rb.tire.segment1.temperature"),
    ("f", "suspension.rb.tire.segment1.wear"),
   
    ("f", "suspension.rb.tire.segment2.temperature"),
    ("f", "suspension.rb.tire.segment2.wear"),
   
    ("f", "suspension.rb.tire.segment3.temperature"),
    ("f", "suspension.rb.tire.segment3.wear"),
   
    ("f", "suspension.rb.tire.segment4.temperature"),
    ("f", "suspension.rb.tire.segment4.wear"),
   
    ("f", "suspension.rb.tire.segment5.temperature"),
    ("f", "suspension.rb.tire.segment5.wear"),
   
    ("f", "suspension.rb.tire.segment6.temperature"),
    ("f", "suspension.rb.tire.segment6.wear"),
   
    ("f", "suspension.rb.tire.segment7.temperature"),
    ("f", "suspension.rb.tire.segment7.wear"),
   
    ("f", "suspension.rb.tire.segment8.temperature"),
    ("f", "suspension.rb.tire.segment8.wear")
) 

format_string = "".join((instruction for instruction, varname in FORMAT_INFO))
unpackt = struct.unpack_from(format_string, var , offset=0)
