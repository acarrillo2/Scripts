# Simple shell script to create an apple notification
# Useful while running terminal commands with long runtimes so you can be notified when command is complete
# Ex. python3 my_long_running_python_script.py && ./ping.sh
osascript -e 'display notification "ping" with title "bot"'

