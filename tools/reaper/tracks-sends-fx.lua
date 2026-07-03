--[[
 * List All FX, Parameters and Sends
 *
 * Walks every track in the project (including the Master track),
 * lists every FX in each track's FX chain along with its current
 * parameter values, and lists every send/receive with volume, pan,
 * mute state and pre/post-fader mode. Writes the report to a text
 * file next to the project.
 *
 * Install:
 *   Actions > Show action list > New action > Load ReaScript...
 *   then run it, or bind it to a shortcut/toolbar button.
]]

local SEND_MODE_LABEL = {
    [0] = "post-fader",
    [1] = "pre-fx",
    [3] = "post-fx/pre-fader",
}

local function lin_to_db(value)
    if value <= 0 then
        return -150.0
    end
    return 20.0 * math.log(value, 10)
end

-- Airwindows Consolidated (and similar multi-engine plugins) doesn't
-- report a preset name through the host API, so TrackFX_GetPreset comes
-- back empty regardless of which internal engine is selected. Each
-- engine does have its own small, distinctive set of parameter names
-- though, so we can identify it deterministically from those instead.
-- Extend this table as you run the script on new plugins/tracks -- the
-- signature is just the ordered, pipe-joined list of the plugin-specific
-- (non-generic) parameter names.
local KNOWN_PARAM_SIGNATURES = {
    ["Replace|Brightns|Detune|Derez|Bigness|Dry/Wet"] = "Galactic3",
    ["RmSize|Sustain|Mulch|Wetness"] = "Verbity2",
}

-- Parameter names that show up on every Airwindows AU regardless of
-- which internal engine is active, so they're excluded when building
-- a signature.
local GENERIC_PARAM_NAMES = {
    ["Bypass"] = true,
    ["Input Level"] = true,
    ["Output Level"] = true,
    ["Mono Behaviour"] = true,
    ["Wet"] = true,
    ["Delta"] = true,
    ["-"] = true,
    [""] = true,
}

local function guess_by_param_signature(track, fx_index)
    local param_count = reaper.TrackFX_GetNumParams(track, fx_index)
    local distinctive_names = {}
    for param_index = 0, param_count - 1 do
        local _, param_name = reaper.TrackFX_GetParamName(track, fx_index, param_index, "")
        if not GENERIC_PARAM_NAMES[param_name] then
            distinctive_names[#distinctive_names + 1] = param_name
        end
    end
    local signature = table.concat(distinctive_names, "|")
    return KNOWN_PARAM_SIGNATURES[signature], signature
end

local function get_track_label(track)
    if track == reaper.GetMasterTrack(0) then
        return "Master"
    end
    local _, name = reaper.GetTrackName(track, "")
    if name == "" then
        local track_number = math.floor(reaper.GetMediaTrackInfo_Value(track, "IP_TRACKNUMBER"))
        name = string.format("Track %d", track_number)
    end
    return name
end

local function append_fx_param_lines(track, fx_index, lines)
    local param_count = reaper.TrackFX_GetNumParams(track, fx_index)
    for param_index = 0, param_count - 1 do
        local _, param_name = reaper.TrackFX_GetParamName(track, fx_index, param_index, "")
        local _, formatted_value = reaper.TrackFX_GetFormattedParamValue(track, fx_index, param_index, "")
        lines[#lines + 1] = string.format("        %s: %s", param_name, formatted_value)
    end
end

local function append_fx_lines(track, lines)
    local fx_count = reaper.TrackFX_GetCount(track)
    if fx_count == 0 then
        lines[#lines + 1] = "  FX: (none)"
        return
    end
    lines[#lines + 1] = "  FX:"
    for fx_index = 0, fx_count - 1 do
        local _, fx_name = reaper.TrackFX_GetFXName(track, fx_index, "")
        local enabled = reaper.TrackFX_GetEnabled(track, fx_index)
        local status = enabled and "" or " [BYPASSED]"
        lines[#lines + 1] = string.format("    [%d] %s%s", fx_index, fx_name, status)

        local preset_ok, preset_name = reaper.TrackFX_GetPreset(track, fx_index, "")
        if preset_ok and preset_name ~= "" then
            lines[#lines + 1] = string.format("      Preset: %s", preset_name)
        else
            -- Fallback: some plugins (Airwindows Consolidated in
            -- particular) never report a preset name through the host
            -- API, so identify the specific engine from its distinctive
            -- parameter names instead.
            local identity, signature = guess_by_param_signature(track, fx_index)
            if identity then
                lines[#lines + 1] = string.format("      Identified from parameters: %s", identity)
            elseif signature ~= "" then
                -- Unknown signature -- print it so it can be added to
                -- KNOWN_PARAM_SIGNATURES once you know the plugin name.
                lines[#lines + 1] = string.format("      Unknown plugin, parameter signature: %s", signature)
            end
        end

        append_fx_param_lines(track, fx_index, lines)
    end
end

local function append_send_lines(track, lines)
    -- category: 0 = sends (this track -> another), -1 = receives (another -> this track)
    local send_count = reaper.GetTrackNumSends(track, 0)
    local receive_count = reaper.GetTrackNumSends(track, -1)

    if send_count == 0 then
        lines[#lines + 1] = "  Sends: (none)"
    else
        lines[#lines + 1] = "  Sends:"
        for send_index = 0, send_count - 1 do
            local dest_track = reaper.BR_GetMediaTrackSendInfo_Track(track, 0, send_index, 1)
            local dest_label = dest_track and get_track_label(dest_track) or "(unknown)"
            local vol = reaper.GetTrackSendInfo_Value(track, 0, send_index, "D_VOL")
            local pan = reaper.GetTrackSendInfo_Value(track, 0, send_index, "D_PAN")
            local mute = reaper.GetTrackSendInfo_Value(track, 0, send_index, "B_MUTE")
            local mode = reaper.GetTrackSendInfo_Value(track, 0, send_index, "I_SENDMODE")
            local mode_label = SEND_MODE_LABEL[math.floor(mode)] or "unknown"
            local mute_label = mute == 1 and " [MUTED]" or ""
            lines[#lines + 1] = string.format(
                "    -> %s | vol: %.1f dB | pan: %.2f | %s%s",
                dest_label, lin_to_db(vol), pan, mode_label, mute_label
            )
        end
    end

    if receive_count == 0 then
        lines[#lines + 1] = "  Receives: (none)"
    else
        lines[#lines + 1] = "  Receives:"
        for receive_index = 0, receive_count - 1 do
            local src_track = reaper.BR_GetMediaTrackSendInfo_Track(track, -1, receive_index, 0)
            local src_label = src_track and get_track_label(src_track) or "(unknown)"
            local vol = reaper.GetTrackSendInfo_Value(track, -1, receive_index, "D_VOL")
            local pan = reaper.GetTrackSendInfo_Value(track, -1, receive_index, "D_PAN")
            local mute = reaper.GetTrackSendInfo_Value(track, -1, receive_index, "B_MUTE")
            local mode = reaper.GetTrackSendInfo_Value(track, -1, receive_index, "I_SENDMODE")
            local mode_label = SEND_MODE_LABEL[math.floor(mode)] or "unknown"
            local mute_label = mute == 1 and " [MUTED]" or ""
            lines[#lines + 1] = string.format(
                "    <- %s | vol: %.1f dB | pan: %.2f | %s%s",
                src_label, lin_to_db(vol), pan, mode_label, mute_label
            )
        end
    end
end

local function resolve_output_path()
    local project_path = reaper.GetProjectPath("")
    local out_dir = project_path
    if out_dir == "" then
        out_dir = reaper.GetResourcePath()
    end
    local sep = package.config:sub(1, 1) == "\\" and "\\" or "/"
    return out_dir .. sep .. "fx_list.txt"
end

local function append_track_report(track, lines)
    lines[#lines + 1] = get_track_label(track)
    append_fx_lines(track, lines)
    append_send_lines(track, lines)
    lines[#lines + 1] = ""
end

local function main()
    local lines = {}

    -- Master track first
    append_track_report(reaper.GetMasterTrack(0), lines)

    -- Regular tracks, in track order
    local track_count = reaper.CountTracks(0)
    for i = 0, track_count - 1 do
        append_track_report(reaper.GetTrack(0, i), lines)
    end

    local out_path = resolve_output_path()
    local file = io.open(out_path, "w")
    if not file then
        reaper.ShowMessageBox("Could not open file for writing:\n" .. out_path, "List All FX", 0)
        return
    end
    file:write(table.concat(lines, "\n"))
    file:close()

    reaper.ShowMessageBox("FX list written to:\n" .. out_path, "List All FX", 0)
end

reaper.Undo_BeginBlock()
main()
reaper.Undo_EndBlock("List all FX, params and sends to file", -1)