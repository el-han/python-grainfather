import xmltodict
import json


class GrainfatherRecipe():
    def __init__(self):
        self.boil_time = None
        self.mash_step_count = 0
        self.mash_volume = None
        self.sparge_volume = None
        self.show_water_treatment_alert = 0
        self.show_sparge_counter = 0
        self.show_sparge_alert = 1
        self.delayed_session = 0
        self.skip_start = 0
        self.recipe_name = None
        self.hop_stand_time = 0
        self.boil_addition_stop_count = 0
        self.boil_power_mode = 1
        self.strike_temp_mode = 0
        self.boil_addition_stops = []
        self.mash_steps = []

    def from_beerxml(self, filename):
        # Open BeerXML file and convert to dict
        with open(filename, 'r') as f:
            beerxml_dict = xmltodict.parse(f.read())['RECIPES']['RECIPE']

        self.recipe_name = beerxml_dict['NAME']
        if len(self.recipe_name) > 19:
            self.recipe_name = self.recipe_name[0:19]
        self.boil_time = int(beerxml_dict['BOIL_TIME'])

        water_mash_total = 0.0

        # Mash steps
        for mash_step in beerxml_dict['MASH']['MASH_STEPS']['MASH_STEP']:
            self.mash_steps.append({'temperature': int(mash_step['STEP_TEMP']),
                                    'time': int(mash_step['STEP_TIME'])})
            try:
                water_mash_step = float(mash_step['INFUSE_AMOUNT'])
                water_mash_total += water_mash_step
            except KeyError:
                pass
        self.mash_step_count = len(self.mash_steps)

        # Boil steps
        hops_times = set()
        for boil_addition_stop in beerxml_dict['HOPS']['HOP']:
            hops_times.add(self.boil_time - int(boil_addition_stop['TIME']))
        self.boil_addition_stops = sorted(list(hops_times), reverse=True)
        self.boil_addition_stop_count = len(self.boil_addition_stops)

        # Water volumes
        water_total = float(beerxml_dict['WATERS']['AMOUNT'])
        water_sparge = water_total - water_mash_total
        self.mash_volume = water_mash_total
        self.sparge_volume = water_sparge

        print(json.dumps(vars(self), indent=4))

    def to_ble_strings(self):
        ble_strings = []

        ble_strings.append(
            f'R{self.boil_time},{self.mash_step_count},{self.mash_volume},{self.sparge_volume},'
        )

        ble_strings.append(
            f'{self.show_water_treatment_alert},{self.show_sparge_counter},{self.show_sparge_alert},'
            f'{self.delayed_session},{self.skip_start},'
        )

        ble_strings.append(f'{self.recipe_name.upper()}')

        ble_strings.append(f'{self.hop_stand_time},{self.boil_addition_stop_count},'
                           f'{self.boil_power_mode},{self.strike_temp_mode},')

        for boil_addition_stop in self.boil_addition_stops:
            # Grainfather does not like 0 minutes hops time. Make it 1 minute!
            if boil_addition_stop == 0:
                ble_strings.append('1,')
            else:
                ble_strings.append(f'{boil_addition_stop},')

        for mash_step in self.mash_steps:
            mash_step_temperature = mash_step['temperature']
            mash_step_time = mash_step['time']
            ble_strings.append(f'{mash_step_temperature}:{mash_step_time},')

        return ble_strings
