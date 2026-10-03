-- Bitrot lp look and feel. A phosphor terminal whose memory decays; the
-- only glitch a window can carry is its border: the focused one runs along a
-- gradient of structure-green stops with one amber stop at 0deg (Hyprland
-- spaces the stops evenly, so the amber reads as a soft band at 75% of the
-- width on the top and bottom edges). Square corners, 2px borders, opaque
-- windows, no blur. tty gives the focused window a phosphor bloom (a shadow in
-- the structure colour); lp has no shadow at all (paper has no bloom).
-- Loaded after futuwwa.lua so these values win; behaviour and binds stay
-- there. The popups and helpers are shared by both Bitrot variants (bitrot-*).

local C = {
    ground    = "F4F1E6",
    hairline  = "A9C3A4",
    structure = "2A6334",
    attention = "8A5200",
}

hl.config({
    general = {
        gaps_in     = 4,
        gaps_out    = 8,
        border_size = 2,
        col = {
            active_border   = {
                colors = { "rgb(" .. C.structure .. ")", "rgb(" .. C.structure .. ")", "rgb(" .. C.structure .. ")",
                           "rgb(" .. C.attention .. ")", "rgb(" .. C.structure .. ")" },
                angle  = 0,
            },
            inactive_border = "rgb(" .. C.hairline .. ")",
        },
    },

    decoration = {
        rounding       = 0,
        rounding_power = 1.0,

        active_opacity   = 1.0,
        inactive_opacity = 1.0,

        blur = {
            enabled = false,
        },

        glow = {
            enabled = false,
        },

        -- tty: the phosphor bloom behind the focused window only; lp: off.
        shadow = {
            enabled        = false,
            range          = 18,
            render_power   = 3,
            offset         = { 0, 0 },
            color          = "rgba(" .. C.structure .. "88)",
            color_inactive = "rgba(00000000)",
        },
    },

    group = {
        col = {
            border_active   = "rgb(" .. C.structure .. ")",
            border_inactive = "rgb(" .. C.hairline .. ")",
        },
    },

    misc = {
        disable_hyprland_logo    = true,
        disable_splash_rendering = true,
        background_color         = "rgb(" .. C.ground .. ")",
    },
})

-- Cursor: BitrotLpCell (~/.local/share/icons/BitrotLpCell, hyprcursor + XCursor).
-- On a live theme switch restore.sh runs `hyprctl setcursor` from gsettings.txt.
hl.env("HYPRCURSOR_THEME", "BitrotLpCell")
hl.env("HYPRCURSOR_SIZE", "24")
hl.env("XCURSOR_THEME", "BitrotLpCell")
hl.env("XCURSOR_SIZE", "24")

-- A config reload resets the cursor to the default theme; set it again.
local function bitrot_cursor()
    hl.exec_cmd("hyprctl setcursor BitrotLpCell 24")
end
hl.on("hyprland.start", bitrot_cursor)
hl.on("config.reloaded", bitrot_cursor)

-- Launcher bind points at the Bitrot launcher; futuwwa.lua binds the Girih one.
hl.unbind("SUPER + D")
hl.bind("SUPER + D",
    hl.dsp.exec_cmd(os.getenv("HOME") .. "/.local/bin/bitrot-launcher"),
    { description = "Application launcher" })

-- Terminals are opaque themselves (alpha 1.0); keep them so.
hl.window_rule({
    name    = "bitrot-terminal-opaque",
    match   = { class = "^(foot|footclient|Alacritty|com.mitchellh.ghostty)$" },
    opacity = "1.0 override 1.0 override",
})

-- Launcher: floating foot + fzf (~/.local/bin/bitrot-launcher).
hl.window_rule({
    name     = "bitrot-launcher",
    match    = { class = "^bitrot-launcher$" },
    float    = true,
    size     = "780 470",
    center   = true,
    pin      = true,
    opacity  = "1.0 override 1.0 override",
})

-- Taskwarrior popups from the waybar "yawm" module (~/.local/bin/bitrot-yawm).
hl.window_rule({
    name     = "bitrot-yawm",
    match    = { class = "^bitrot-yawm$" },
    float    = true,
    size     = "820 600",
    center   = true,
    pin      = true,
    opacity  = "1.0 override 1.0 override",
})

hl.window_rule({
    name     = "bitrot-yawm-add",
    match    = { class = "^bitrot-yawm-add$" },
    float    = true,
    size     = "720 240",
    center   = true,
    pin      = true,
    opacity  = "1.0 override 1.0 override",
})

local bitrot_popups = { "bitrot-launcher", "bitrot-yawm", "bitrot-yawm-add" }

-- Close every popup window except those of class `keep`.
-- hl.get_windows matches `class` exactly (no regex), so pass the plain name.
function bitrot_close_popups(keep)
    for _, class in ipairs(bitrot_popups) do
        if class ~= keep then
            for _, w in ipairs(hl.get_windows({ class = class })) do
                hl.dispatch(hl.dsp.window.close({ window = "address:" .. w.address }))
            end
        end
    end
end

function bitrot_close_launcher()
    bitrot_close_popups()
end

-- Close popups as soon as focus moves elsewhere.
hl.on("window.active", function(win)
    bitrot_close_popups(win and win.class)
end)

-- The popups' frame: 1px in the structure colour instead of the 2px gradient. Kept apart in a
-- pcall so that, should this Hyprland not know the two rule keys, the rest of the file still loads.
pcall(hl.window_rule, {
    name         = "bitrot-popup-frame",
    match        = { class = "^bitrot-(launcher|yawm|yawm-add)$" },
    border_size  = 1,
    border_color = "rgb(" .. C.structure .. ")",
})
