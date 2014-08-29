notify-that
===========

Simple notification system for when your batch jobs are done.

## Dependencies
* Python 2.7

## Installation
1. Clone repo
2. Install dependencies: `$ pip install -r requirements.txt`
2. Modify notify-that.py to reflect your phone number, yo username, etc.
3. Build executable file: `$ ./build.sh`
4. Add executable to your path (in Ubuntu): `$ ln -s <path-to-git-repo>/dist/notify-that ~/bin/notify-that`
5. Probably have to restart terminal

## Usage
notify-that will send you a yo/text/email when your scripts are finished. It also sends the output of your scripts if you choose to send via email.
	$ ./some_long_running_script | notify-that <yo|text|email>
