# coding=utf-8
from __future__ import absolute_import

import os
import re

import octoprint.plugin
from octoprint.util import RepeatedTimer

class EnclosuretempPlugin(octoprint.plugin.StartupPlugin,
                          octoprint.plugin.SettingsPlugin,
                          octoprint.plugin.AssetPlugin,
                          octoprint.plugin.TemplatePlugin):


        def __init__(self):
                self.display_navbar = True
                self._checkTempTimer = None
                self.update_interval = 5.0
        
        def on_after_startup(self):
                self._logger.info("Enclosure Temperature plugin startup")
                self._logger.info("Sensor name/directory = {}".format(self._settings.get(["sensor_name"])))
                self._logger.info("Starting Timer with {}s interval".format(self.update_interval))
                self.startTimer(self.update_interval)
        


        # Template Plugin
        #def get_template_vars(self):
        #        return dict(sensor_name=self._settings.get(["sensor_name"]))

        def get_template_configs(self):
                """For the settings template I want to use the default bindings (not sure what they
                are binding... But basically, I want octoprint to handle the display.
                For the navbar portion, I want to set that display up myself, so I don't include it here
                and it default to cutom_bindings=True (I think)
                """
                return [
                        #dict(type="navbar", custom_bindings=False),
                        dict(type="settings", custom_bindings=False)
                        ]
                
        # My functions
        def startTimer(self, interval):
                self._checkTempTimer = RepeatedTimer(interval, self.get_temp, None, None, True)
                self._checkTempTimer.start()
                self._logger.info("Started timer with {}s interval".format(interval))

                
        def get_temp(self):
                """Reads temperature from 1-wire probe at address taken from the settings tab.
                returns the value, and sends a "plugin_message" which will trigger the javascript
                code to update the value on the webpage.
                """
                self._logger.info("Reading temperture...")

                def temp_raw(filename):
                        with open(filename,'r') as f:
                                lines=f.readlines()
                        return(lines)

                def read_temp(device_name):
                        max_attempts = 10
                        attempt = 0
                        filename = os.path.join('/sys/bus/w1/devices',device_name,'w1_slave')
                        try:
                                lines = temp_raw(filename)
                        except IOError:
                                temp = -99
                        else:
                                while lines[0].strip()[-3:] != 'YES' and attempt < max_attempts:
                                        time.sleep(0.5)
                                        lines = temp_raw(filename)
                                        attempt += 1
                                match_obj=re.match('.*t=([0-9]*)',lines[1])
                                if match_obj is not None and attempt < max_attempts:
                                        temp = float(match_obj.group(1))/1000.0
                                else:
                                        temp = -99
                        return(temp)

                self._logger.info("self._identifier = {}".format(self._identifier))
                device_name = self._settings.get(["sensor_name"])
                self._logger.info("sensor_name = {}".format(device_name))
                temp = read_temp(device_name)
                self._logger.info("enclosure temp = {}oC".format(temp))
                self.current_temp = temp
                self._plugin_manager.send_plugin_message(self._identifier, dict(enclosureTemp=self.current_temp))


        def get_settings_defaults(self):
                """default Settings. Can be overridden in the settings tab I think"""
		return dict(
                        sensor_name = '28-031455b66cff'
		)
                        
	##~~ AssetPlugin mixin

	def get_assets(self):
                """Define your plugin's asset files to automatically include in the
		core UI here."""
		return dict(
			js=["js/EnclosureTemp.js"],
			#css=["css/EnclosureTemp.css"],
			#less=["less/EnclosureTemp.less"]
		)

	##~~ Softwareupdate hook
	def get_update_information(self):
                """Define the configuration for your plugin to use with the Software Update
		Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		for details. This is the default setup"""
		return dict(
			EnclosureTemp=dict(
				displayName="Enclosuretemp Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="mcgodfrey",
				repo="OctoPrint-Enclosuretemp",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/mcgodfrey/OctoPrint-Enclosuretemp/archive/{target_version}.zip"
			)
		)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Enclosuretemp Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = EnclosuretempPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

