# ~/.config/zsh/bitrot-lp.zsh-theme
# Bitrot lp prompt: a segment chain, standalone (no framework). Segments are
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

B_GROUND='#F4F1E6' B_SEL='#CFE3C6'   B_DIM='#44614A'   B_SEC='#2F5233'   B_PRI='#1A1F1A'
B_STRUCT='#2A6334' B_ATT='#8A5200'   B_ERRFILL='#B8281B' B_ERRINK='#F4F1E6'

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
zstyle ':completion:*' list-colors 'di=38;2;42;99;52' 'ex=38;2;26;112;48' 'ln=38;2;47;82;51' 'ma=48;2;207;227;198;38;2;26;31;26'

# ls (eza): permission bits r data, w secondary, x structure; directories
# in structure, executables in the up colour
export EZA_COLORS="ur=38;2;43;58;45:gr=38;2;43;58;45:tr=38;2;43;58;45:uw=38;2;47;82;51:gw=38;2;47;82;51:tw=38;2;47;82;51:ux=38;2;42;99;52:ue=38;2;42;99;52:gx=38;2;42;99;52:tx=38;2;42;99;52:di=38;2;42;99;52:ex=38;2;26;112;48"

# ---- plugins ---------------------------------------------------------
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=$B_DIM"
[[ -r /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh ]] &&
  source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh

# zsh-syntax-highlighting must be sourced last, then styled.
if [[ -r /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]]; then
  source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
  ZSH_HIGHLIGHT_STYLES[command]='fg=#1A7030'
  ZSH_HIGHLIGHT_STYLES[builtin]='fg=#1A7030'
  ZSH_HIGHLIGHT_STYLES[alias]='fg=#1A7030'
  ZSH_HIGHLIGHT_STYLES[function]='fg=#1A7030'
  ZSH_HIGHLIGHT_STYLES[precommand]='fg=#1A7030,underline'
  ZSH_HIGHLIGHT_STYLES[reserved-word]='fg=#2A6334'
  ZSH_HIGHLIGHT_STYLES[path]='fg=#2B3A2D,underline'
  ZSH_HIGHLIGHT_STYLES[single-hyphen-option]='fg=#2F5233'
  ZSH_HIGHLIGHT_STYLES[double-hyphen-option]='fg=#2F5233'
  ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg=#2F5233'
  ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg=#2F5233'
  ZSH_HIGHLIGHT_STYLES[comment]='fg=#44614A'
  ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=#A3180F'
fi

export FZF_DEFAULT_OPTS="--color=bg:#F4F1E6,bg+:#CFE3C6,fg:#1A1F1A,fg+:#1A1F1A,hl:#2A6334,hl+:#2A6334,info:#44614A,prompt:#2A6334,pointer:#8A5200,marker:#8A5200,spinner:#8A5200,header:#44614A,border:#2A6334 --pointer='▶' --marker='█' --no-scrollbar --layout=reverse --border=sharp"
