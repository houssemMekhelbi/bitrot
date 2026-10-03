# ~/.config/zsh/bitrot-tty.zsh-theme
# Bitrot tty prompt: a segment chain, standalone (no framework). Segments are
# reverse-video blocks that close with a ▓▒░ smear in the segment's own colour,
# the prompt's form of the slice; no arrows.
#   status   error fill, only on failure / root / background jobs
#   context  selection fill, only over SSH or as another user
#   dir      structure fill with ground text, the last two components
#   git      selection fill: ▒ branch, and ±n in amber when the tree is dirty
# Line 2 is `$ ` in the primary colour; the clock sits at the right in dim.
# The block elements are written as $'\u....' escapes, so this file is plain
# ASCII apart from its comments. Hex colours need zsh 5.7+ and a true-colour terminal.

setopt prompt_subst

BITROT_DEFAULT_USER=${BITROT_DEFAULT_USER:-$USER}   # hide context on your own box

B_GROUND='#050806' B_SEL='#16301C'   B_DIM='#62A66E'   B_SEC='#6FBF7C'   B_PRI='#9CF0A6'
B_STRUCT='#33CC55' B_ATT='#FFB000'   B_ERRFILL='#8C1A12' B_ERRINK='#E6F7E3'

B_SMEAR=$'▓▒░'   # the smear that closes a segment
B_BRANCH=$'▒'              # the branch mark

# a reverse block: fill $1, text $2, content $3, then the smear in the fill colour
b_seg() {
  print -n "%{%K{$1}%F{$2}%} $3 %{%k%F{$1}%}$B_SMEAR%{%f%}"
}

b_status() {
  local -a s
  (( B_RETVAL != 0 )) && s+="$B_RETVAL"
  (( UID == 0 )) && s+='#'
  [[ -n ${jobstates} ]] && s+="&${#jobstates}"
  (( ${#s} )) && b_seg $B_ERRFILL $B_ERRINK "${(j: :)s}"
}

b_context() {
  [[ $USER != $BITROT_DEFAULT_USER || -n $SSH_CONNECTION ]] &&
    b_seg $B_SEL $B_SEC '%n@%m'
}

b_dir() {
  b_seg $B_STRUCT $B_GROUND '%2~'
}

b_git() {
  command git rev-parse --is-inside-work-tree &>/dev/null || return
  local ref n
  ref=$(command git symbolic-ref --short HEAD 2>/dev/null) ||
    ref=$(command git rev-parse --short HEAD 2>/dev/null)
  ref=${ref//\%/%%}
  n=$(command git status --porcelain --ignore-submodules=dirty 2>/dev/null | wc -l)
  n=${n// /}
  if (( n > 0 )); then
    b_seg $B_SEL $B_SEC "$B_BRANCH $ref %{%F{$B_ATT}%}±$n"
  else
    b_seg $B_SEL $B_SEC "$B_BRANCH $ref"
  fi
}

b_build_prompt() {
  b_status
  b_context
  b_dir
  b_git
}

b_precmd() { B_RETVAL=$? }
autoload -Uz add-zsh-hook
add-zsh-hook precmd b_precmd

PROMPT='%{%f%b%k%}$(b_build_prompt)'$'\n''%{%F{'$B_PRI'}%}$ %{%f%}'
RPROMPT="%F{$B_DIM}%D{%H:%M}%f"

# ---- completion ------------------------------------------------------
autoload -Uz compinit && compinit
zstyle ':completion:*' menu select
zstyle ':completion:*' list-colors 'di=38;2;51;204;85' 'ex=38;2;125;255;143' 'ln=38;2;111;191;124' 'ma=48;2;22;48;28;38;2;156;240;166'

# ls (eza): permission bits r data, w secondary, x structure; directories
# in structure, executables in the up colour
export EZA_COLORS="ur=38;2;207;227;204:gr=38;2;207;227;204:tr=38;2;207;227;204:uw=38;2;111;191;124:gw=38;2;111;191;124:tw=38;2;111;191;124:ux=38;2;51;204;85:ue=38;2;51;204;85:gx=38;2;51;204;85:tx=38;2;51;204;85:di=38;2;51;204;85:ex=38;2;125;255;143"

# ---- plugins ---------------------------------------------------------
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=$B_DIM"
[[ -r /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh ]] &&
  source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh

# zsh-syntax-highlighting must be sourced last, then styled.
if [[ -r /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]]; then
  source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
  ZSH_HIGHLIGHT_STYLES[command]='fg=#7DFF8F'
  ZSH_HIGHLIGHT_STYLES[builtin]='fg=#7DFF8F'
  ZSH_HIGHLIGHT_STYLES[alias]='fg=#7DFF8F'
  ZSH_HIGHLIGHT_STYLES[function]='fg=#7DFF8F'
  ZSH_HIGHLIGHT_STYLES[precommand]='fg=#7DFF8F,underline'
  ZSH_HIGHLIGHT_STYLES[reserved-word]='fg=#33CC55'
  ZSH_HIGHLIGHT_STYLES[path]='fg=#CFE3CC,underline'
  ZSH_HIGHLIGHT_STYLES[single-hyphen-option]='fg=#6FBF7C'
  ZSH_HIGHLIGHT_STYLES[double-hyphen-option]='fg=#6FBF7C'
  ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg=#6FBF7C'
  ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg=#6FBF7C'
  ZSH_HIGHLIGHT_STYLES[comment]='fg=#62A66E'
  ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=#FF6A55'
fi

export FZF_DEFAULT_OPTS="--color=bg:#050806,bg+:#16301C,fg:#9CF0A6,fg+:#9CF0A6,hl:#33CC55,hl+:#33CC55,info:#62A66E,prompt:#33CC55,pointer:#FFB000,marker:#FFB000,spinner:#FFB000,header:#62A66E,border:#33CC55 --pointer='▶' --marker='█' --no-scrollbar --layout=reverse --border=sharp"
