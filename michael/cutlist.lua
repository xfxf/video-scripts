-- cutlist.lua: Adds "cut list" functionality to OBS for Next Day Video AV
-- streaming stack (similar what is in dvswitch).
--
-- Copyright 2020 Michael Farrell <micolous+git@gmail.com>
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.
--
-- Setting up:
--
-- 1. In OBS, go to `Tools` menu -> `Scripts`.
-- 2. Press +
-- 3. Load this script.
-- 4. In `Output file`, press `Browse`, and select where to write the cut list
--    file to.
-- 5. Press `Close`.
-- 6. Open OBS `Settings`, and go to `Hotkeys`.
-- 7. Set a hotkey for `Log cut event`, and press `OK`.
-- 8. Exit OBS and restart it (this ensures that OBS properly saves the
--    settings, should it crash...)
--
-- This log file is new-line separated JSON; the format is in the documentation
-- for `log_event()` (below).

obs = obslua
hotkey_id = obs.OBS_INVALID_HOTKEY_ID
cutlist_fh = nil
unloading = false

-- Log event an event from this script.
-- Both the `event_type` and `data` parameters must be strings.
--
-- Each event is a JSON object, separated by a newline character (\n):
--
-- * `ts` (required): ISO 8601 timestamp (YYYY-mm-ddTHH:MM:SS) in local time
-- * `event` (required): type of event
-- * `data` (optional): parameters relating to the event
--
-- Event types:
--
-- * "LOAD": script loaded.
-- * "SCENE": scene changed; `data` contains the new scene name.
-- * "CUT": "cut" button pressed.
-- * "CLOSE": log file closed or script unloaded.
function log_event(event_type, data)
   now = os.date('%Y-%m-%dT%H:%M:%S')
   -- Lua's %q operator escapes strings, it looks enough like JSON for our needs.
   event_data = string.format('{"ts": %q, "event": %q', now, event_type)
   if data ~= nil then
      event_data = event_data .. string.format(', "data": %q', data)
   end
   event_data = event_data .. '}\n'

   if not unloading then
      -- OBS crashes if you call script_log() during script_unload()!
      obs.script_log(obs.LOG_INFO, 'event: ' .. event_data)
   end

   if cutlist_fh ~= nil then
      cutlist_fh:write(event_data)
      cutlist_fh:flush()
   elseif not unloading then
      -- OBS crashes if you call script_log() during script_unload()!
      obs.script_log(obs.LOG_ERROR, 'Cut list file not open, cannot log!')
   end
end

function log_scene()
   local scene = obs.obs_frontend_get_current_scene()
   local scene_name = obs.obs_source_get_name(scene)
   log_event('SCENE', scene_name)
   obs.obs_source_release(scene)
end

function close_log()
   if cutlist_fh ~= nil then
      -- Close existing file
      log_event('CLOSE')

      cutlist_fh:close()
      cutlist_fh = nil
   end
end

-- Called when the "cut" button is pressed.
function cut(pressed)
   if not pressed then
      return
   end

   log_event('CUT')
end

function on_event(event)
   if event == obs.OBS_FRONTEND_EVENT_SCENE_CHANGED then
      log_scene()
   end
end

-- Properties
function script_properties()
   local props = obs.obs_properties_create()
   obs.obs_properties_add_path(props, 'cutlist.path', 'Output file', obs.OBS_PATH_FILE_SAVE, 'Text file (*.txt);', nil)
   obs.obs_properties_add_button(props, 'cutlist.button', 'Log cut event', cut) 
   return props
end

-- Setup
function script_load(settings)
   -- Load hotkey settings from storage
   hotkey_id = obs.obs_hotkey_register_frontend('cutlist.trigger', 'Log cut event', cut)
   local hotkey_save_array = obs.obs_data_get_array(settings, 'cutlist.trigger')
   obs.obs_hotkey_load(hotkey_id, hotkey_save_array)
   obs.obs_data_array_release(hotkey_save_array)

   -- Event handler
   obs.obs_frontend_add_event_callback(on_event)
end

-- Settings serialization
function script_save(settings)
   local hotkey_save_array = obs.obs_hotkey_save(hotkey_id)
   obs.obs_data_set_array(settings, 'cutlist.trigger', hotkey_save_array)
   obs.obs_data_array_release(hotkey_save_array)
end

function script_update(settings)
   close_log()

   -- Open a new file
   local cutlist_file = obs.obs_data_get_string(settings, 'cutlist.path')
   if cutlist_file ~= nil then
      cutlist_fh = io.open(cutlist_file, 'a')
      
      if cutlist_fh == nil then
         obs.script_log(obs.LOG_ERROR, 'Cannot open cut log file: ' .. cutlist_file)
         return
      end
   else
      obs.script_log(obs.LOG_ERROR, 'Cut log file not specified')
      return
   end

   log_event('LOAD')
   log_scene()
end

function script_description()
   return 'When the "Log cut event" hotkey is triggered, saves the event and timestamp to a log file.\n\nAlso saves any scene changes to that log file.'
end

function script_unload()
   unloading = true
   close_log()
end
