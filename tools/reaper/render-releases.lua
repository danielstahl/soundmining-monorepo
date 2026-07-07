--[[
render_release_formats.lua

Renders the current Reaper project to every audio format needed for release,
in one script run:
  - Full -> FLAC, 32-bit, 96kHz
  - SoundCloud  -> FLAC, 24-bit, 48kHz
  - CD Baby     -> WAV,  16-bit, 44.1kHz  (CD-quality delivery)
  - Bandcamp    -> FLAC, 24-bit, 48kHz    (NEVER 32-bit -- Bandcamp rejects it)

REQUIRES: Ultraschall API for Reaper (install via ReaPack):
  https://github.com/Ultraschall/ultraschall-lua-api-for-reaper

WHY an extension is needed:
  Reaper's native ReaScript API does not expose a simple "set format, render"
  call -- the render format is stored internally as an undocumented binary
  blob. The Ultraschall API exposes CreateRenderCFG_* / RenderProject_RenderTable
  functions that handle this properly, so we don't have to hand-craft that blob.

ONE-TIME SETUP:
  1. Open File > Render... in Reaper.
  2. Configure the format/samplerate/bit-depth for one target (see list above).
  3. Click the "Add render preset" / Preset dropdown and save it using one of
     the exact names in `preset_names` below (e.g. "release-soundcloud").
  4. Repeat for each of the three targets.
  5. Close the render dialog (no need to actually render from it).

Then just run this script whenever you want to export all three at once.

NOTE ON FIELD NAMES:
  The exact key names inside a RenderTable (e.g. for output directory /
  filename pattern) aren't fully published by Ultraschall and can vary
  slightly between API versions. The `DEBUG_DUMP_KEYS` block below will
  print every key/value in a fetched RenderTable to the console the first
  time you run this -- use that to confirm/adjust the two lines marked
  "ADJUST IF NEEDED" further down if your render doesn't land where expected.
--]]

if not reaper.APIExists("ultraschall.GetApiVersion") then
  reaper.MB(
    "This script needs the Ultraschall API for Reaper.\n\n"
      .. "Install it via ReaPack:\n"
      .. "https://github.com/Ultraschall/ultraschall-lua-api-for-reaper",
    "Ultraschall API missing",
    0
  )
  return
end

-- Set to true once, to inspect the actual field names available on your
-- installed Ultraschall version, then set back to false.
local DEBUG_DUMP_KEYS = false

local preset_names = {
  "Full Render"
  "Render Soundcloud",
  "Render CD Baby",
  "Render Bandcamp",
}

local _, project_name = reaper.GetProjectName(0, "")
project_name = project_name:gsub("%.[Rr][Pp][Pp]$", "")
if project_name == "" then
  project_name = "untitled"
end

local output_dir = reaper.GetProjectPath("") .. "/renders"
reaper.RecursiveCreateDirectory(output_dir, 0)

local function dump_keys(render_table, label)
  reaper.ShowConsoleMsg(string.format("--- RenderTable keys for %s ---\n", label))
  for k, v in pairs(render_table) do
    reaper.ShowConsoleMsg(string.format("  %s = %s\n", tostring(k), tostring(v)))
  end
  reaper.ShowConsoleMsg("--- end ---\n\n")
end

reaper.Undo_BeginBlock()
reaper.ShowConsoleMsg("") -- clear/open console

for _, preset_name in ipairs(preset_names) do
  local render_table = ultraschall.GetRenderPreset_RenderTable(preset_name)

  if render_table == nil then
    reaper.ShowConsoleMsg(string.format(
      "SKIPPED  %-20s -- no render preset with this name found.\n"
        .. "         Save one from File > Render... first (see header comment).\n",
      preset_name
    ))
  else
    if DEBUG_DUMP_KEYS then
      dump_keys(render_table, preset_name)
    end

    -- ADJUST IF NEEDED: field names for output directory / filename pattern.
    -- Print the table (DEBUG_DUMP_KEYS = true) once to confirm these on your
    -- installed Ultraschall version if renders don't land where expected.
    render_table["Directory"] = output_dir
    render_table["Filename"] = project_name .. "_" .. preset_name

    local retval, count = ultraschall.RenderProject_RenderTable(
      nil, -- nil = current open project
      render_table,
      true, -- overwrite without asking
      true -- auto-close render progress window
    )

    if retval == 0 then
      reaper.ShowConsoleMsg(string.format("OK       %-20s -- %d file(s) -> %s\n", preset_name, count or 0, output_dir))
    else
      reaper.ShowConsoleMsg(string.format("FAILED   %-20s -- retval=%s\n", preset_name, tostring(retval)))
    end
  end
end

reaper.Undo_EndBlock("Render all release formats", -1)