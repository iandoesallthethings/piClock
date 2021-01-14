#!/bin/bash
#
# Setup a work space called `work` with two windows
# first window has 3 panes. 
# The first pane set at 65%, split horizontally, set to api root and running vim
# pane 2 is split at 25% and running redis-server 
# pane 3 is set to api root and bash prompt.
# note: `api` aliased to `cd ~/path/to/work`
#

sudo systemctl kill start-clock.service
session="work"

cd piClock
# set up tmux
tmux start-server

# create a new tmux session, starting vim from a saved session in the new window
tmux new-session -d -s $session

# Select pane 1, set dir to api, run vim
tmux send-keys "vim clock.py" C-m 

# Split pane 1 horizontal by 65%, start nodemon
tmux splitw -p 5
tmux send-keys "nodemon clock.py" C-m 

tmux selectp -1 1
tmux splitw -h -p 50

# Select pane 0 
tmux selectp -t 0

# Finished setup, attach to the tmux session!
tmux attach-session -t $session
