#!/usr/bin/env bash
# Script to run static analysis checks on Python sources
# usage to check files:
# ./check


SOURCES="**/*.py"

command_exists() {
    type "$1" &>/dev/null ;
}

execute() {
    if command_exists $1 ; then
        echo "Executing $1..."
        $1 $SOURCES
    else
        echo "Skipping $1 (not installed)."
    fi
}

execute vulture
execute pyflakes
execute pep8
execute pylint