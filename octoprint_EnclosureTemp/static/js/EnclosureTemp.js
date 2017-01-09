$(function() {
    function EnclosureTempViewModel(parameters) {
	var self = this;
	
	
	self.settings = parameters[0];
	self.connection = parameters[1];

	//This is the variable which is seen in the html/jinja2 file in the data-bind
	self.enclosureTemp = ko.observable();

	//I have to update the self.enclosureTemp with the new value of
	//enclosureTemp measured by the python plugin object
	self.onDataUpdaterPluginMessage = function(plugin, data) {
	    if (plugin != "EnclosureTemp") {
		return;
	    }
	    self.enclosureTemp(data.enclosureTemp);
	};

    }

    //Don't know what this does, but it seems to work. based on other plugins
    ADDITIONAL_VIEWMODELS.push([
	EnclosureTempViewModel,
	["settingsViewModel","connectionViewModel"],
	["#navbar_plugin_EnclosureTemp", "settings_plugin_EnclosureTemp"]
    ]);
});


