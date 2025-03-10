def parse_lnxrepl(line: str) -> dict:
    types = [int, float, int, int, *([float]*4), *([float]*4), int, *([float]*4), *([float]*4), *([int]*16), float, *([int]*4), float, float, int, *([float]*6)]
    parsed = [t(v) for t, v in zip(types, line.strip().split(' '))]
    if len(parsed) != len(types):
        print('Invalid line:', parsed)
        return None

    return {
        "entry_id": parsed[0],
        "timestamp": parsed[1],
        "state": parsed[2],
        "front_frame_ID": parsed[3],
        "front_ball_bb": parsed[4:8],
        "front_goal_bb": parsed[8:12],
        "mirror_frame_ID": parsed[12],
        "mirror_ball_bb": parsed[13:17],
        "mirror_goal_bb": parsed[17:21],
        "line_sensors": parsed[21:37],
        "heading": parsed[37],
        "motor_values": parsed[38:42],
        "robot_position": parsed[42:44],
        "n_field_robots": parsed[44],
        "enemy_positions": [(parsed[45 + i*2], parsed[46 + i*2]) for i in range(parsed[44])]
    }
