from collections import namedtuple

MESSAGE_LENGTH = 664

FORMAT_INFO = (
    ("<", ""),                         # little endian
    ("I", "general.total_steps"),
    ("I", "stage.index"),
    ("f", "stage.progress"),
    ("f", "stage.total_race_time"),
    ("f", "stage.drive_line_location"),
    ("f", "stage.distance_to_end"),    # meters or feet(?) depending on config

    ("f", "control.steering_input"),
    ("f", "control.throttle_input"),
    ("f", "control.brake_input"),
    ("f", "control.handbrake_input"),
    ("f", "control.clutch_input"),
    ("i", "control.current_gear"),
    ("f", "control.brake_pressure"),
    ("f", "control.handbrake_pressure"),

    ("i", "car.index"),
    ("f", "car.speed"),                               # in mph or kmh depending on config
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
    ("f", "engine.radiator_coolant_temperature"),       # kelvin
    ("f", "engine.engine_coolant_temperature"),         # kelvin
    ("f", "engine.engine_temperature"),                # kelvin

    ("f", "suspension.lf.spring_deflection"),
    ("f", "suspension.lf.rollbar_force"),
    ("f", "suspension.lf.spring_force"),
    ("f", "suspension.lf.damper_force"),
    ("f", "suspension.lf.strut_force"),
    ("i", "suspension.lf.helper_spring_is_active"),

    ("f", "suspension.lf.damper.damage"),
    ("f", "suspension.lf.damper.pistonvelocity"),

    ("f", "suspension.lf.brake.layer_temperature"),    # kelvin?
    ("f", "suspension.lf.brake.temperature"),         # kelvin?
    ("f", "suspension.lf.brake.wear"),

    ("f", "suspension.lf.tire.pressure"),
    ("f", "suspension.lf.tire.temperature"),
    ("f", "suspension.lf.tire.carcass_temperature"),
    ("f", "suspension.lf.tire.tread_temperature"),
    ("I", "suspension.lf.tire.current_segment"),

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

    ("f", "suspension.rf.brake.layer_temperature "),
    ("f", "suspension.rf.brake.temperature"),
    ("f", "suspension.rf.brake.wear"),

    ("f", "suspension.rf.tire.pressure"),
    ("f", "suspension.rf.tire.temperature"),
    ("f", "suspension.rf.tire.carcass_temperature"),
    ("f", "suspension.rf.tire.tread_temperature"),
    ("I", "suspension.rf.tire.current_segment"),

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

    ("f", "suspension.lb.brake.layer_temperature"),
    ("f", "suspension.lb.brake.temperature"),
    ("f", "suspension.lb.brake.wear"),

    ("f", "suspension.lb.tire.pressure"),
    ("f", "suspension.lb.tire.temperature"),
    ("f", "suspension.lb.tire.carcass_temperature"),
    ("f", "suspension.lb.tire.tread_temperature"),
    ("I", "suspension.lb.tire.current_segment"),

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

    ("f", "suspension.rb.brake.layer_temperature"),
    ("f", "suspension.rb.brake.temperature"),
    ("f", "suspension.rb.brake.wear"),

    ("f", "suspension.rb.tire.pressure"),
    ("f", "suspension.rb.tire.temperature"),
    ("f", "suspension.rb.tire.carcass_temperature"),
    ("f", "suspension.rb.tire.tread_temperature"),
    ("I", "suspension.rb.tire.current_segment"),

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

FORMAT_STRUCT_PATTERN = "".join(instruction for instruction, _ in FORMAT_INFO)
FORMAT_FIELDS = tuple(field for _, field in FORMAT_INFO if field)
