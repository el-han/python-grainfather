import asyncio
import re
import logging

from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic, BleakError

from .grainfather_recipe import GrainfatherRecipe
from .grainfather_stats import GrainfatherStats


DEVICE_UUID = '0000cdd0-0000-1000-8000-00805f9b34fb'
READ_CHAR_UUID = '0003cdd1-0000-1000-8000-00805f9b0131'
WRITE_CHAR_UUID = '0003cdd2-0000-1000-8000-00805f9b0131'


class Grainfather():

    def __init__(self):
        self.log = logging.getLogger('grainfather')

        self.client = None

        self.read_data = ''

        self.stats = GrainfatherStats()

        self.update_stats_callback = None

        self.stopevent = asyncio.Event()

    async def connect(self, address=None):

        if address is not None:
            self.log.info(f'Using Grainfather with address {address}')
        else:
            # Try to automatically find Grainfather and determin its address
            self.log.info('No address provided. Searching for Grainfather...')
            address = await Grainfather.discover()
            self.log.info(f'Found Grainfather with address {address}')

        self.client = BleakClient(address, disconnected_callback=self.__disconnect_callback)

        await self.client.connect()
        self.stats.set_connected(True)
        self.log.info('Connected to grainfather')
        if self.update_stats_callback is not None:
            self.update_stats_callback(self.stats)

    async def discover():
        device = await BleakScanner.find_device_by_name('Grain')
        return device.address

    def __disconnect_callback(self, client: BleakClient):
        self.stats.set_connected(False)
        self.log.error('Connection to Grainfather lost.')
        if self.update_stats_callback is not None:
            self.update_stats_callback(self.stats)

    def __callback(self, sender: BleakGATTCharacteristic, data: bytearray):
        self.read_data = self.read_data + data.decode()

        try_to_match = True

        while try_to_match:

            m = re.match(r'([ABCEFITVWXY][^ABCEFITVWXY]*)([ABCEFITVWXY])', self.read_data)

            if m:
                entry = self.read_data[m.start(1):m.end(1)]
                self.read_data = self.read_data[m.end(1):-1]

                self.stats.update(entry)

                if self.update_stats_callback is not None:
                    self.update_stats_callback(self.stats)

            else:
                try_to_match = False

    async def run(self, callback=None):
        if self.client is None:
            self.log.error('Not connected to Grainfather')
            return

        self.update_stats_callback = callback

        await self.client.start_notify(READ_CHAR_UUID, self.__callback)

        while not self.stopevent.is_set():
            if not self.client.is_connected:
                # Reconnect
                try:
                    await self.client.connect()
                    self.stats.set_connected(True)
                    self.log.info('Connected to grainfather')
                    if self.update_stats_callback is not None:
                        self.update_stats_callback(self.stats)
                    await self.client.start_notify(READ_CHAR_UUID, self.__callback)
                except BleakError:
                    pass
            await asyncio.sleep(0.001)

        # self.client.stop_notify(READ_CHAR_UUID)
        self.client.disconnect()

    def stop(self):
        self.stopevent.set()

    async def send_command(self, command: str):
        if self.client is None:
            self.log.error('Not connected to Grainfather')
            return

        ble_command = command.encode('ascii')

        if len(ble_command) > 19:
            raise ValueError

        while len(ble_command) < 19:
            ble_command = ble_command + b' '

        await self.client.write_gatt_char(WRITE_CHAR_UUID, ble_command)
        self.log.debug(f'sent command string: {ble_command}')

    async def send_command_raw(self, command: str):
        if self.client is None:
            self.log.error('Not connected to Grainfather')
            return

        ble_command = command.encode('ascii')
        await self.client.write_gatt_char(WRITE_CHAR_UUID, ble_command)
        self.log.debug(f'sent command string: {ble_command}')

    async def send_recipe_beerxml(self, filename):
        recipe = GrainfatherRecipe()
        recipe.from_beerxml(filename)
        recipe_strings = recipe.to_ble_strings()

        for recipe_string in recipe_strings:
            await self.send_command(recipe_string)

    async def dismiss_boil_addition_alert(self):
        await self.send_command('A')

    async def cancel_timer(self):
        await self.send_command('C')

    async def decrement_target_temp(self):
        await self.send_command('D')

    async def cancel_or_finish_session(self):
        await self.send_command('F')

    async def pause_or_resume_timer(self):
        await self.send_command('G')

    async def toggle_heat(self):
        await self.send_command('H')

    async def interaction_complete(self):
        await self.send_command('I')

    async def turn_off_heat(self):
        await self.send_command('K0')

    async def turn_on_heat(self):
        await self.send_command('K1')

    async def turn_off_pump(self):
        await self.send_command('L0')

    async def turn_on_pump(self):
        await self.send_command('L1')

    async def get_current_boil_temp(self):
        await self.send_command('M')

    async def toggle_pump(self):
        await self.send_command('P')

    async def disconnect_manual_mode_no_action(self):
        await self.send_command('Q0')

    async def disconnect_and_cancel_session(self):
        await self.send_command('Q1')

    async def disconnect_auto_mode_no_action(self):
        await self.send_command('Q2')

    async def press_set(self):
        await self.send_command('T')

    async def increment_target_temp(self):
        await self.send_command('U')

    async def disable_sparge_water_alert(self):
        await self.send_command('V')

    async def get_firmware_version(self):
        await self.send_command('X')

    async def reset_controller(self):
        await self.send_command('Z')

    async def reset_recipe_interrupted(self):
        await self.send_command('!')

    async def turn_off_sparge_counter_mode(self):
        await self.send_command('D0')

    async def turn_on_sparge_counter_mode(self):
        await self.send_command('D1')

    async def turn_off_boil_control_mode(self):
        await self.send_command('E0')

    async def turn_on_boil_control_mode(self):
        await self.send_command('E1')

    async def exit_manual_power_control_mode(self):
        await self.send_command('F0')

    async def enter_manual_power_control_mode(self):
        await self.send_command('F1')

    async def get_controller_voltage_and_units(self):
        await self.send_command('G')

    async def turn_off_sparge_alert_mode(self):
        await self.send_command('H0')

    async def turn_on_sparge_alert_mode(self):
        await self.send_command('H1')

    async def set_delayed_heat_function(self, minutes, seconds):
        await self.send_command(f'B{minutes},{seconds},')

    async def set_local_boil_temp_to(self, temperature):
        await self.send_command(f'E{temperature},')

    async def set_boil_time_to(self, minutes):
        await self.send_command(f'J{minutes},')

    async def skip_to_step(self, step_num, can_edit_time, time_left_minutes, time_left_seconds, skip_ramp, disable_add_grain):
        await self.send_command(f'N{step_num},{can_edit_time},{time_left_minutes},{time_left_seconds},{skip_ramp},{disable_add_grain},')

    async def set_new_timer(self, minutes):
        await self.send_command(f'S{minutes},')

    async def set_new_timer_with_seconds(self, minutes, seconds):
        await self.send_command(f'W{minutes},{seconds},')

    async def set_target_temp_to(self, temperature):
        await self.send_command(f'${temperature},')

    async def edit_controller_stored_temp_and_time(self, stage_num, new_time, new_temperature):
        await self.send_command(f'A{stage_num},{new_time},{new_temperature},')

    async def set_sparge_progress_to(self, progress):
        await self.send_command(f'B${progress},')

    async def skip_to_interaction(self, code):
        await self.send_command(f'C{code},')
