Title: Fishing shells
Date: 2016-12-26 15:00
Category: Shell
Tags: shell, tutorial, linux

I have been used to bash for years and always thought it was very good but after
trying other alternatives I found out that there are more efficient ways to use
the command line.

I would like to present here one of my favorite interpreter that is the [fish
shell](https://fishshell.com/). *Fish* stands for **F**riendly **I**nteractive
**Sh**ell and is yet another command line interpreter. Its goal is to be user
friendly while being fast. 

The major difference with other standards command line interpreters, is that
fish is not POSIX and has some subtle differences. People behind fish think
POSIX is not adapted for modern usage and decided to not follow it to invent a
better, less error prone and more user friendly syntax.

To make the switch less painful, I will try to show the majors difference
between the well known bash and give some tips on how to customize it.

# Installation
You can install fish shell from the source but it is recommended to use your
favorite package manager:

    :::sh
    # .deb
    apt-get install fish

    # .rpm
    yum install fish

    # Arch
    pacman -S fish

    # Gentoo
    emerge fish

    # Void
    xbps-install fish-shell

    # Other I forgot
    # Read the fine manual :)

# Starting fish
On your usual shell prompt, you can simply type:

    :::sh
    fish

If after some tries your are happy with it, you can set it as default by editing
the */etc/passwd* manually or by using the *chsh* command:

    :::sh
    chsh -s /usr/bin/fish <your-username>

# Common usages
Here is a list useful daily tasks but using the fish syntax.

* **Return code**

$? doesn't exist, the *status* variable is what you are looking for:

    ::::fish
    fish$ true ; echo $status 
    0
    fish$ false ; echo $status 
    1

* **;and, ;or**

People from fish uses the *and/or* keyword instead of &&/||

    ::::fish
    fish$ true ; and echo sucess!
    sucess!
    fish$ false ; or echo failed!
    failed!

* **Variables**

When you want to export variables with bash, you would use the *export* and *=*
sign. Don't add any space in between otherwise it will not work! Lists are not
well supported either.

With fish shell, the *set* built-in is used to declare variables command. With
the *-x* parameter, the variabled is exported. fish supports lists very well and
can be declared by using space between each element:

    ::::fish
    fish$ set -x PATH $PATH $HOME/bin /opt/toolchain/bin
    fish$ echo $PATH
    /usr/local/bin /bin /usr/bin /home/random/bin/ /opt/toolchain/bin
    fish$ set -x ARCH arm
    fish$ make menuconfig

More information about list can be found further.

* **Command substitution**

Under bash, my favorite flavor is using *$(...)* but think fish guys think that
the *$* character is confusing as it is already used for variable expansion, and
is consequently not used:

    ::::fish
    $ echo My usernmae is (whoami)
    My usernmae is random

* **Flow control**

With fish, you have to use the *end* keyword that is common for every flow
control mechanism unlike *done*, *fi*, *esac* with other shells. Also where fish
adds a touch of user friendliness is that it takes care of all the indentation
and coloring:

    ::::fish
    fish$ while true
              uptime
              sleep 1
          end

Another if statement example:

    ::::fish
    $fish if true
              echo All good
          end
    All good


* **Functions**

When using a function, parameters are stored in the *argv* list:

    ::::fish
    fish$ function hello
              echo Hello $argv[1]
          end
    fish$ hello
    Hello

    fish$ hello world
    Hello world

I love the [index range expansion](
https://fishshell.com/docs/current/index.html#expand-index-range) feature!

    ::::fish
    fish$ function hello
              echo Hello $argv[1..-1]
          end
    fish$ hello tux world everyone
    Hello tux world everyone

Or if you want to say hello to everyone more personnaly:

    ::::fish
    fish$ function hello
              for who in $argv[1..-1]
                  echo Hello $who
              end
          end
    fish$ hello tux world everyone
    Hello tux
    Hello world
    Hello everyone

* **time command**

It is sometime interesting to know how long it takes to run a command and *time*
built-in bash implementation does the trick very well. In fish, there is no
*time* command but the duration is stored in a variable:

    ::::sh
    fish$ sleep 1
    fish$ echo $CMD_DURATION 
    1006

You could implement the time function yourself but you can also use some fish
scripts from the communauty. [fish_command_timer](
https://github.com/jichu4n/fish-command-timer) is my favoriyte, simply clone the
repository and source the required file:

    ::::fish
    fish$ git clone https://github.com/jichu4n/fish-command-timer.git
    fish$ . ./fish-command-timer/fish_command_timer.fish
    fish$ ls
    fish-command-timer/
                                                      [ 0s101 | Dec 09 04:19PM ]

To make this permanent, you can add this your the fish configuration as
explained later.

# Customization
Of course, fish is highly configurable but again, differs a bit from other
shells.

* **.bashrc**

If you are looking for something similar to the .bashrc file, you can edit or
create the *.config/fish/config.fish*. Here is for example how mine looks like:

    ::::fish
    set fish_greeting (uptime)
    . /home/random/sources/fish-command-timer/fish_command_timer.fish

* **Prompt**

Unlike the *PS1* variable, the fish prompt is defined in the *fish_prompt*
function:

    ::::fish
    fish$ function fish_prompt
              echo -n (whoami)@(cat /etc/hostname)\$" "
          end
    random@random-notebook$

* **GIT prompt**

Fish is able to show the git branch and repository status on the prompt.
Just enable some built-in configurations by adding this in the fish
configuration:

    ::::fish
    set __fish_git_prompt_showdirtystate 'yes'
    set __fish_git_prompt_showstashstate 'yes'
    set __fish_git_prompt_showuntrackedfiles 'yes'
    set __fish_git_prompt_showupstream 'yes'
    set __fish_git_prompt_color_branch yellow
    set __fish_git_prompt_color_upstream_ahead green
    set __fish_git_prompt_color_upstream_behind red

This will change your prompt as follow when inside a git repository:

    ::::fish
    fish (master) ➞


* **Oh my fish**

*omf* is a repository containing different skins for fish. Everyone is welcome
to use it and share his themes. Make sure you have a decent version of fish to
have a better user exeprience, unfortunately it doesn't work well on older LTS
distriubtions.

Here is how you can install it and user my favorite theme:

    ::::fish
    fish$ curl -L http://get.oh-my.fish | fish
    # ...
    fish$ omf install fisk
    Installing theme fisk
    ✔ theme fisk successfully installed.
    [0] random@random-notebook ~ ➞

For forther information check the [official git repository](
https://github.com/oh-my-fish/oh-my-fish) and the list of [available themes](
https://github.com/oh-my-fish/oh-my-fish/blob/master/docs/Themes.md)

This would probably remind [oh my zsh](http://ohmyz.sh/) for the zsh*ish*!

# Common shortcuts
Luckily some shortcuts you learned from bash are also available within fish.
Here is the list of the one I use the most frequently:

* **TAB**: Enable autocompletion for almost everything :p
* **CTRL+f**: Accept **f**ish autosuggestion
* **CTRL+e**: Go to the **e**nd of the command
* **CTRL+a**: Go to the beginning of the command (**A**nfang in German?)
* **CTRL+p | up arrow **: Go to the **p**revious in history
* **CTRL+n | down arrow**: Go to the **n**ext in history 
* ** < pattern > CTRL+p|CTRL+n**: Look for *< pattern >* in hostory

# Conclusion
Fish has a very nice out of the box configuration and most people will be very
happy with it! If you like it and think it could improve your productivity, do
not hesitate to have a deeper look at the [introduction page](
https://fishshell.com/docs/current/tutorial.html) and at the [documentation](
https://fishshell.com/docs/current/index.html) for advanced usage. 

It has the huge drawback that it is not POSIX but this is OK when using it only
in interactive mode. Unfortunately I haven't written many *fischripts* and would
be interesting to see if it really brings much performance improvement.

[zsh](http://www.zsh.org/) is a nice alternative, it is very user friendly while
respecting the standards. Those who spent a lot of time customizing their zsh
will prefer sticking with it but fish worth having a look for your own culture!
