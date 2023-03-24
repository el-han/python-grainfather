from copy import deepcopy
import logging


class GrainfatherStats:

    def __init__(self):
        self.log = logging.getLogger()

        # X
        self.target_temperature = None
        self.current_temperature = None
        # Y
        self.heat_power = None
        self.pump_status = None
        self.auto_mode_status = None
        self.stage_ramp_status = None
        self.interaction_mode_status = None
        self.interaction_code = None
        self.stage_number = None
        self.delayed_heat_mode = None
        # T
        self.timer_active = None
        self.time_left_minutes = None
        self.timer_total_start_time = None
        self.time_left_seconds = None
        # W
        self.heat_power_output_percentage = None
        self.is_timer_paused = None
        self.step_mash_mode = None
        self.is_recipe_interrupted = None
        self.manual_power_mode = None
        self.sparge_water_alert_displayed = None

    def update(self, state_str):
        kind = state_str[0]
        entries = state_str[1:-1].split(',')

        # print(kind + ' ' + str(entries))

        def _get(index):
            try:
                return float(entries[index])
            except IndexError:
                return None
            except ValueError:
                return None

        if kind == 'X':
            self.target_temperature = _get(0)
            self.current_temperature = _get(1)
        elif kind == 'Y':
            self.heat_power = _get(0)
            self.pump_status = _get(1)
            self.auto_mode_status = _get(2)
            self.stage_ramp_status = _get(3)
            self.interaction_mode_status = _get(4)
            self.interaction_code = _get(5)
            self.stage_number = _get(6)
            self.delayed_heat_mode = _get(7)
        elif kind == 'T':
            self.timer_active = _get(0)
            self.time_left_minutes = _get(1)
            self.timer_total_start_time = _get(2)
            self.time_left_seconds = _get(3)
        elif kind == 'W':
            self.heat_power_output_percentage = _get(0)
            self.is_timer_paused = _get(1)
            self.step_mash_mode = _get(2)
            self.is_recipe_interrupted = _get(3)
            self.manual_power_mode = _get(4)
            self.sparge_water_alert_displayed = _get(5)
        else:
            self.log.warning(f'Received unknown state update string: {state_str}')

    def to_dict(self):
        # get all class members as dict
        stats_dict = deepcopy(vars(self))

        # remove logger instance
        stats_dict.pop('log')

        return stats_dict
