#!/bin/bash
set -euo pipefail

# Claude Code Starter Kit — Setup Script
# Phase 1: Install minimal config to ~/.claude/ (rules, hooks, guard)
# Phase 2: Bootstrap ~/claude-assistant/ workspace (knowledge, skills, tasks, agents)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "=== Claude Code Starter Kit ==="
echo ""

# -----------------------------------------------
# Step 1: Detect OS and package manager
# -----------------------------------------------

OS="unknown"
PKG_INSTALL=""

if [[ "$(uname)" == "Darwin" ]]; then
    OS="macos"
    if command -v brew >/dev/null 2>&1; then
        PKG_INSTALL="brew install"
    fi
elif [[ "$(uname)" == "Linux" ]]; then
    OS="linux"
    if command -v apt-get >/dev/null 2>&1; then
        PKG_INSTALL="sudo apt-get install -y"
    elif command -v dnf >/dev/null 2>&1; then
        PKG_INSTALL="sudo dnf install -y"
    elif command -v pacman >/dev/null 2>&1; then
        PKG_INSTALL="sudo pacman -S --noconfirm"
    fi
fi

echo "Detected: $OS"
echo ""

install_with_prompt() {
    local name="$1"
    local pkg="${2:-$1}"
    local install_cmd="${3:-}"

    if [[ -z "$install_cmd" && -z "$PKG_INSTALL" ]]; then
        echo "  x $name — not found. Install it manually and re-run setup."
        return 1
    fi

    local cmd="${install_cmd:-$PKG_INSTALL $pkg}"
    read -p "  Install $name? ($cmd) [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        eval "$cmd"
        return $?
    else
        echo "  Skipped $name."
        return 1
    fi
}

# -----------------------------------------------
# Step 2: Check and install dependencies
# -----------------------------------------------

echo "Checking dependencies..."
echo ""
MISSING=0

# --- Homebrew (macOS only) ---
if [[ "$OS" == "macos" ]] && ! command -v brew >/dev/null 2>&1; then
    echo "  x Homebrew — not found (needed to install other tools on macOS)"
    read -p "  Install Homebrew? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        # Add to PATH for this session
        if [[ -f /opt/homebrew/bin/brew ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        PKG_INSTALL="brew install"
    else
        echo "  Without Homebrew, you'll need to install dependencies manually."
    fi
fi

# --- Git ---
if command -v git >/dev/null 2>&1; then
    echo "  ok git ($(git --version | head -c 20))"
else
    echo "  x git — not found"
    install_with_prompt "git" || MISSING=1
fi

# --- Python 3 ---
if command -v python3 >/dev/null 2>&1; then
    PY_VER=$(python3 --version 2>&1)
    echo "  ok python3 ($PY_VER)"
else
    echo "  x python3 — not found (needed for security guard and task database)"
    install_with_prompt "python3" "python3" || MISSING=1
fi

# --- jq ---
if command -v jq >/dev/null 2>&1; then
    echo "  ok jq ($(jq --version 2>&1))"
else
    echo "  x jq — not found (needed for statusline and hooks)"
    install_with_prompt "jq" || MISSING=1
fi

# --- trash (safe rm replacement) ---
if command -v trash >/dev/null 2>&1; then
    echo "  ok trash"
elif [[ "$OS" == "macos" ]]; then
    echo "  x trash — not found (safe alternative to rm -rf, moves to Trash)"
    install_with_prompt "trash" "trash" || true
elif [[ "$OS" == "linux" ]]; then
    echo "  x trash-cli — not found (safe alternative to rm -rf)"
    install_with_prompt "trash-cli" "trash-cli" || true
fi

# --- Claude Code CLI ---
if command -v claude >/dev/null 2>&1; then
    echo "  ok claude CLI"
else
    echo "  x Claude Code CLI — not found"
    if command -v npm >/dev/null 2>&1; then
        install_with_prompt "claude" "" "npm install -g @anthropic-ai/claude-code" || MISSING=1
    elif command -v brew >/dev/null 2>&1; then
        install_with_prompt "claude" "" "brew install claude-code" || MISSING=1
    else
        echo "    Install Node.js first, then: npm install -g @anthropic-ai/claude-code"
        echo "    Or see: https://docs.anthropic.com/en/docs/claude-code"
        MISSING=1
    fi
fi

echo ""

if [[ $MISSING -eq 1 ]]; then
    echo "Some required tools are missing. Install them and re-run ./setup.sh"
    exit 1
fi

echo "All dependencies OK."
echo ""

# -----------------------------------------------
# Step 3: Personalize
# -----------------------------------------------

echo "Let's personalize your assistant."
echo ""
read -p "Your first name: " USER_NAME
read -p "One-line bio (e.g., 'Python dev, building SaaS tools'): " USER_BIO

if [[ -z "$USER_NAME" || ${#USER_NAME} -lt 2 ]]; then
    echo "Error: name is required (at least 2 characters)"
    exit 1
fi

# --- Workspace directory ---
echo ""
read -p "Workspace directory [~/claude-assistant]: " WORKSPACE_INPUT
WORKSPACE_NAME="${WORKSPACE_INPUT:-claude-assistant}"
# Strip leading ~/
WORKSPACE_NAME="${WORKSPACE_NAME#\~/}"
WORKSPACE_DIR="$HOME/$WORKSPACE_NAME"

echo ""

# -----------------------------------------------
# Step 4: Check for existing config
# -----------------------------------------------

if [[ -f "$CLAUDE_DIR/settings.json" ]]; then
    echo "Warning: ~/.claude/settings.json already exists."
    read -p "Overwrite? This will replace your current config. (y/N) " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }
fi

if [[ -d "$WORKSPACE_DIR" ]]; then
    echo "Warning: $WORKSPACE_DIR already exists."
    read -p "Overwrite? This will replace your workspace files. (y/N) " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }
fi

echo "Setting up..."
echo ""

# ===============================================
# PHASE 1: Install minimal config to ~/.claude/
# ===============================================

echo "Phase 1: Installing global config to ~/.claude/ ..."

# Create directory structure
mkdir -p "$CLAUDE_DIR"/{rules,scripts,state}

# --- Copy scripts (hook scripts only) ---
cp "$SCRIPT_DIR/scripts/global-guard.py" "$CLAUDE_DIR/scripts/"
cp "$SCRIPT_DIR/scripts/pre-compact.sh" "$CLAUDE_DIR/scripts/"
cp "$SCRIPT_DIR/scripts/session-save-reminder.sh" "$CLAUDE_DIR/scripts/"
cp "$SCRIPT_DIR/scripts/post-compact-reinject.sh" "$CLAUDE_DIR/scripts/"
chmod +x "$CLAUDE_DIR/scripts/"*.sh "$CLAUDE_DIR/scripts/"*.py

# --- Copy rules ---
for rule in "$SCRIPT_DIR"/rules/*.md; do
    cp "$rule" "$CLAUDE_DIR/rules/"
done

# --- Copy settings.json ---
cp "$SCRIPT_DIR/templates/settings.json" "$CLAUDE_DIR/settings.json"

# --- Copy .gitignore ---
cp "$SCRIPT_DIR/templates/gitignore" "$CLAUDE_DIR/.gitignore"

# --- Copy statusline ---
cp "$SCRIPT_DIR/statusline.sh" "$CLAUDE_DIR/"
chmod +x "$CLAUDE_DIR/statusline.sh"

# --- Generate global CLAUDE.md ---
sed -e "s/{{USER_NAME}}/$USER_NAME/g" \
    -e "s|{{USER_BIO}}|$USER_BIO|g" \
    "$SCRIPT_DIR/templates/global-CLAUDE.md" > "$CLAUDE_DIR/CLAUDE.md"

# --- Write workspace.conf ---
echo "$WORKSPACE_DIR" > "$CLAUDE_DIR/workspace.conf"

# --- Substitute workspace path in rules (replace ~/claude-assistant with actual) ---
if [[ "$WORKSPACE_NAME" != "claude-assistant" ]]; then
    for f in "$CLAUDE_DIR/rules/"*.md; do
        sed -i '' "s|~/claude-assistant/|~/$WORKSPACE_NAME/|g" "$f" 2>/dev/null || \
        sed -i "s|~/claude-assistant/|~/$WORKSPACE_NAME/|g" "$f"
    done
    # Also update global CLAUDE.md
    sed -i '' "s|~/claude-assistant/|~/$WORKSPACE_NAME/|g" "$CLAUDE_DIR/CLAUDE.md" 2>/dev/null || \
    sed -i "s|~/claude-assistant/|~/$WORKSPACE_NAME/|g" "$CLAUDE_DIR/CLAUDE.md"
fi

echo "  Global config installed."
echo ""

# ===============================================
# PHASE 2: Bootstrap workspace
# ===============================================

echo "Phase 2: Bootstrapping workspace at $WORKSPACE_DIR ..."

# Create directory structure
mkdir -p "$WORKSPACE_DIR"/{.claude/skills/onboard,.claude/skills/tasks,.claude/skills/plan-and-implement,.claude/skills/reflect,.claude/skills/bootstrap,.claude/skills/create-skill/scripts,knowledge/self,knowledge/user,knowledge/problems,knowledge/projects,agents,scripts,state/sessions}

# --- Generate workspace CLAUDE.md ---
sed -e "s/{{USER_NAME}}/$USER_NAME/g" \
    -e "s|{{USER_BIO}}|$USER_BIO|g" \
    "$SCRIPT_DIR/templates/workspace-CLAUDE.md" > "$WORKSPACE_DIR/.claude/CLAUDE.md"

# --- Copy agents ---
for agent in "$SCRIPT_DIR"/agents/*.md; do
    cp "$agent" "$WORKSPACE_DIR/agents/"
done

# --- Copy workspace scripts ---
cp "$SCRIPT_DIR/scripts/db.py" "$WORKSPACE_DIR/scripts/"
cp "$SCRIPT_DIR/scripts/extract-learnings.py" "$WORKSPACE_DIR/scripts/"
chmod +x "$WORKSPACE_DIR/scripts/"*.py

# --- Copy skills ---
cp "$SCRIPT_DIR/skills/onboard/SKILL.md" "$WORKSPACE_DIR/.claude/skills/onboard/"
cp "$SCRIPT_DIR/skills/tasks/SKILL.md" "$WORKSPACE_DIR/.claude/skills/tasks/"
cp "$SCRIPT_DIR/skills/tasks/LEARNINGS.md" "$WORKSPACE_DIR/.claude/skills/tasks/"
cp "$SCRIPT_DIR/skills/plan-and-implement/SKILL.md" "$WORKSPACE_DIR/.claude/skills/plan-and-implement/"
cp "$SCRIPT_DIR/skills/plan-and-implement/LEARNINGS.md" "$WORKSPACE_DIR/.claude/skills/plan-and-implement/"
cp "$SCRIPT_DIR/skills/reflect/SKILL.md" "$WORKSPACE_DIR/.claude/skills/reflect/"
cp "$SCRIPT_DIR/skills/reflect/LEARNINGS.md" "$WORKSPACE_DIR/.claude/skills/reflect/"
cp "$SCRIPT_DIR/skills/bootstrap/SKILL.md" "$WORKSPACE_DIR/.claude/skills/bootstrap/"
cp "$SCRIPT_DIR/skills/bootstrap/LEARNINGS.md" "$WORKSPACE_DIR/.claude/skills/bootstrap/"
cp "$SCRIPT_DIR/skills/create-skill/SKILL.md" "$WORKSPACE_DIR/.claude/skills/create-skill/"
cp "$SCRIPT_DIR/skills/create-skill/LEARNINGS.md" "$WORKSPACE_DIR/.claude/skills/create-skill/"
cp "$SCRIPT_DIR/skills/create-skill/scripts/init_skill.py" "$WORKSPACE_DIR/.claude/skills/create-skill/scripts/"
cp "$SCRIPT_DIR/skills/create-skill/scripts/validate_skill.py" "$WORKSPACE_DIR/.claude/skills/create-skill/scripts/"
chmod +x "$WORKSPACE_DIR/.claude/skills/create-skill/scripts/"*.py

# --- Copy workspace .gitignore ---
cp "$SCRIPT_DIR/templates/workspace-gitignore" "$WORKSPACE_DIR/.gitignore"

# --- Substitute workspace path in skills (if non-default) ---
if [[ "$WORKSPACE_NAME" != "claude-assistant" ]]; then
    find "$WORKSPACE_DIR/.claude/skills" -name "SKILL.md" -exec \
        sed -i '' "s|~/claude-assistant/|~/$WORKSPACE_NAME/|g" {} \; 2>/dev/null || \
    find "$WORKSPACE_DIR/.claude/skills" -name "SKILL.md" -exec \
        sed -i "s|~/claude-assistant/|~/$WORKSPACE_NAME/|g" {} \;
fi

# --- Initialize task database and export backlog ---
python3 "$WORKSPACE_DIR/scripts/db.py" init
python3 "$WORKSPACE_DIR/scripts/db.py" export

# --- Create starter MEMORY.md ---
cat > "$WORKSPACE_DIR/MEMORY.md" << 'MEMEOF'
# Auto-Memory

## Active Tasks

(Run `/tasks` or `/onboard` to populate)

## Active Projects

(Will grow as you work on projects)

## Next Up

1. Run `/onboard` to set up your profile, problems, goals, and tasks

## File Map

| Path | Content |
|---|---|
| `knowledge/user/profile.md` | Your profile (created by /onboard) |
| `knowledge/user/goals.md` | Goals and subgoals (created by /onboard) |
| `knowledge/problems/00-overview.md` | 12 problems overview (created by /onboard) |
| `knowledge/self/identity.md` | AI self-knowledge (created by /onboard) |
MEMEOF

echo "  Workspace created."
echo ""

# -----------------------------------------------
# Step 5: Initialize git repos
# -----------------------------------------------

# --- Global ~/.claude/ git ---
if [[ ! -d "$CLAUDE_DIR/.git" ]]; then
    cd "$CLAUDE_DIR"
    git init
    git add \
        CLAUDE.md settings.json statusline.sh .gitignore workspace.conf \
        rules/ scripts/
    git commit -m "initial setup from claude-starter-kit"
    echo ""
    echo "Git repo initialized at ~/.claude/"
fi

# --- Workspace git ---
if [[ ! -d "$WORKSPACE_DIR/.git" ]]; then
    cd "$WORKSPACE_DIR"
    git init
    git add \
        .claude/ .gitignore MEMORY.md \
        agents/ scripts/ state/backlog.md \
        knowledge/
    git commit -m "initial setup from claude-starter-kit"
    echo ""
    echo "Git repo initialized at $WORKSPACE_DIR"
    echo "To back up your workspace, create a private repo and run:"
    echo "  cd $WORKSPACE_DIR && git remote add origin git@github.com:YOUR_USERNAME/claude-assistant.git && git push -u origin main"
fi

# -----------------------------------------------
# Done
# -----------------------------------------------

echo ""
echo "=== Setup complete ==="
echo ""
echo "Global config (~/.claude/):"
echo "  CLAUDE.md          — global instructions (points to workspace)"
echo "  settings.json      — hooks + security"
echo "  rules/             — communication, security, sessions, tasks, delegation, development, research"
echo "  scripts/           — security guard, pre-compact, post-compact, session reminder"
echo "  statusline.sh      — context/cost display"
echo ""
echo "Workspace ($WORKSPACE_DIR):"
echo "  .claude/CLAUDE.md  — workspace instructions"
echo "  .claude/skills/    — onboard, tasks, plan, reflect, bootstrap, create-skill"
echo "  knowledge/         — your assistant's growing brain"
echo "  agents/            — code-reviewer, bug-fixer, implementer, researcher"
echo "  scripts/           — task database, learning extractor"
echo "  state/             — sessions, backlog"
echo "  MEMORY.md          — cross-session index"
echo ""
echo "=== Next: Start your first session ==="
echo ""
echo "  cd ~/$WORKSPACE_NAME"
echo "  claude"
echo ""
echo "Then type:"
echo "  /onboard"
echo ""
echo "This will walk you through a 20-30 minute guided setup:"
echo "  1. Build your user profile"
echo "  2. Define your 12 Favorite Problems (Feynman method)"
echo "  3. Set your end goal and subgoals"
echo "  4. Create initial tasks"
echo "  5. Set up the AI's self-knowledge"
echo ""
echo "You can pause anytime and resume later with: /onboard resume"
echo ""
