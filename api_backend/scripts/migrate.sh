#!/bin/bash
# Database migration helper script
# Usage: ./scripts/migrate.sh [command]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# Check if supabase CLI is installed
check_supabase_cli() {
    if ! command -v supabase &> /dev/null; then
        error "Supabase CLI not found. Install it first:

macOS:   brew install supabase/tap/supabase
npm:     npm install -g supabase
Linux:   curl -fsSL https://raw.githubusercontent.com/supabase/cli/main/install.sh | sh"
    fi
    info "Supabase CLI found: $(supabase --version)"
}

# Show usage
usage() {
    cat << EOF
Database Migration Helper

Usage: ./scripts/migrate.sh [command]

Commands:
  install       Install Supabase CLI
  link          Link to your Supabase project
  new           Create a new migration
  push          Push migrations to remote
  pull          Pull remote schema
  reset         Reset local database
  status        Show migration status
  help          Show this help message

Examples:
  ./scripts/migrate.sh new add_user_preferences
  ./scripts/migrate.sh push
  ./scripts/migrate.sh status

EOF
}

# Install Supabase CLI
install_cli() {
    info "Installing Supabase CLI..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install supabase/tap/supabase
        else
            error "Homebrew not found. Install from: https://brew.sh"
        fi
    elif command -v npm &> /dev/null; then
        npm install -g supabase
    else
        curl -fsSL https://raw.githubusercontent.com/supabase/cli/main/install.sh | sh
    fi

    info "Supabase CLI installed successfully!"
}

# Link to Supabase project
link_project() {
    check_supabase_cli

    info "Linking to Supabase project..."
    warn "You'll need your project ref from: https://app.supabase.com/project/_/settings/general"

    cd "$PROJECT_ROOT"
    supabase login
    supabase link --project-ref "${1:-}"

    info "Project linked successfully!"
}

# Create new migration
new_migration() {
    check_supabase_cli

    if [ -z "$1" ]; then
        error "Migration name required. Usage: ./scripts/migrate.sh new <name>"
    fi

    cd "$PROJECT_ROOT"
    supabase migration new "$1"

    info "Migration created! Edit the file in supabase/migrations/"
}

# Push migrations to remote
push_migrations() {
    check_supabase_cli

    cd "$PROJECT_ROOT"

    warn "This will apply migrations to your REMOTE Supabase database."
    read -p "Continue? (y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        supabase db push
        info "Migrations pushed successfully!"
    else
        warn "Cancelled."
    fi
}

# Pull remote schema
pull_schema() {
    check_supabase_cli

    cd "$PROJECT_ROOT"
    supabase db pull

    info "Schema pulled from remote!"
}

# Reset local database
reset_local() {
    check_supabase_cli

    cd "$PROJECT_ROOT"

    warn "This will reset your LOCAL database and reapply all migrations."
    read -p "Continue? (y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        supabase db reset
        info "Local database reset!"
    else
        warn "Cancelled."
    fi
}

# Show migration status
show_status() {
    check_supabase_cli

    cd "$PROJECT_ROOT"

    info "Migration status:"
    supabase migration list
}

# Main command router
case "${1:-help}" in
    install)
        install_cli
        ;;
    link)
        link_project "$2"
        ;;
    new)
        new_migration "$2"
        ;;
    push)
        push_migrations
        ;;
    pull)
        pull_schema
        ;;
    reset)
        reset_local
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        error "Unknown command: $1\n$(usage)"
        ;;
esac
