Title: Event driven programming with the reactor pattern
Date: 2016-10-22 15:00
Category: Programming
Tags: tutorial, linux, software architecture

I want to show in this article an example of bad practice and give an elegant
solution with the reactor pattern that helped me and my team writing more
efficient code.

If you use frameworks like QT, SDL, Java Swing, gtklib, ... this article will
give you a rough idea about what is happening behind the scene and from where
come from some limitations. I will write [the source](https://github.com/
r4nd0m6uy/reactor_example) in CPP as it is a language I know well enough and is
not too difficult to understand if you come from the OO world.

[TOC]

# The example application
Let's say that for this example you are waiting for data to coming from a named
pipe and want to print its content to stdout. Once the application is started, 
we wil generate some output by writing in a named pipe:
> echo "Hello app" > /tmp/test_pipe

That will print the following on the console
> Hello app

Don't forget to quit gracefully the app on CTRL+C and that's all we need!

# The bad code
Here is how would look the naive implementation of this program:

    :::cpp
    bool isRunning = false;

    //--------------------------------------------------------------------------
    void onSignal(int signum)
    {
        isRunning = false;
    }

    //--------------------------------------------------------------------------
    int main(int argc, char* argv[])
    {
        /**
         * Skipped initialization
         */
        int fifoFd = open("/tmp/test_pipe",  O_RDONLY | O_NONBLOCK);
        if(fifoFd < 0)
            return -1;

        isRunning = true;
        while(isRunning)
        {
            int buffSize = 256;
            char buffer[buffSize];
            ssize_t readSize;

            readSize = read(fifoFd, buffer, buffSize);
            if(readSize < 0)
            {
                if(errno == EAGAIN || errno == EWOULDBLOCK)
                    continue;
                else
                    return -1;
            }

            if(write(1, buffer, readSize) < 0)
                return -1;
        }

        /**
         * Skipped cleanup
         */

        return 0;
    }

If you don't see what is wrong here, try run the application and check the CPU
usage, it should be 100% as the loop runs continuously despite nothing has to be
read from the pipe. Using sleep should help to spare some resources but this is
not good enough because the answer time will be in the worst case, the time you
sleep. If you have real time constraints, game over!

Another bad point is extending this code, in the case you have more
I/Os to read I'll let you imagine how this can get very messy... Using multi
threading would not help and will bring more complexity when synchronizing them,
don't do that for this specific problem!

# The Reactor pattern
The reactor pattern gives a simple solution to do what we want using a single
thread. The following diagram explains very nicely its mechanism:

![Reactor sequence][reactor_image]
[reactor_image]: ../images/reactor/sequence.png 
"source: http://www.cs.wustl.edu/~schmidt/PDF/reactor-siemens.pdf"


Don't worry if you don't understand each detail for now, I will try to explain
them while implementing the pattern.

# Our IO handler
We will define first a small interface that reflects the *Event_Handler*. This
object will be implemented by the user and be in charge of reading data from the
*handle* when requested by the *Dispatcher*.

In the Linux world, when we speak about *Handle* we refer to a file descriptor,
that's why we will use an int and call it *IoHandle*:

    :::cpp
    typedef int IoHandle;

Then we declare an interface:

    :::cpp
    class IIoHandler
    {
    public:
        IIoHandler();
        virtual ~IIoHandler();

We will need a function to pass the handler's *IoHandle* to the *Dispatcher*:

    :::cpp
        virtual IoHandle getIoHandle() = 0;

And a callback function that will be called when data is ready to be read from
the given *IoHandle*:

    :::cpp
        virtual void readReady() = 0;
    };

That's it for the interface but we still need a concrete implementation. For
this example we will create a class that will be called *NamedPipeToStdout*.
Yes, in programming the biggest difficulty is finding good names:

    :::cpp
    class NamedPipeToStdout:
            public IIoHandler
    {

We will declare two private fields, one containing the *IoHandle* and one the
path to the pipe:

    :::cpp
    private:
        std::string m_pipePath;
        IoHandle m_pipeIoHandle;

Let's start with a constructor from which we will inject the path to the pipe
and initialize the *IoHandle* to an invalid value:

    :::cpp
    public:
        NamedPipeToStdout(const std::string& name):
                m_pipePath(name),
                m_pipeIoHandle(-1)
        {
        }

As usual the destructor will perform some cleanup:

    :::cpp
        ~NamedPipeToStdout()
        {
            close(m_pipeIoHandle);
            unlink(m_pipePath.c_str());
        }

An init function will be useful to create and open the pipe:

    :::cpp
        int init()
        {
            if(mkfifo(m_pipePath.c_str(), S_IRWXU) < 0)
            {
                if(errno != EEXIST)
                {
                    perror("mkfifo");
                    return -1;
                }
            }

            m_pipeIoHandle = open(m_pipePath.c_str(), O_RDWR | O_NONBLOCK);
            if(m_pipeIoHandle < 0)
            {
                perror("Open fifo");
                return -1;
            }

            return 0;
        }

We still need to implement the functions from the interface, first the
*getIoHandle* function that simply returns the file descriptor of the pipe:

    :::cpp
        IoHandle getIoHandle() override
        {
            return m_pipeIoHandle;
        }

And the callback when data in the pipe are available, we will just print the
content to stdout as described by the class name:

    :::cpp
        void readReady() override
        {
            int buffSize = 64;
            char buffer[buffSize];
            ssize_t readSize;

            readSize = read(m_pipeIoandle, buffer, buffSize);
            if(readSize < 0)
            {
                perror("Read from pipe");
                return;
            }

            if(write(1, buffer, readSize) < 0)
                perror("Write to stdout");
        }
    };

That's should be it for our *IoHandler*, now we need a *Dispatcher* where all
the magic will occur!

# Our event dispatcher
We will write first the interface for our *Dispatcher*. An interface is always
wise as it is easier to mock for unit testing. Moreover, under Linux, there are
different flavor of the *select* call ([select](http://man7.org/linux/man-pages/
man2/select.2.html), [poll](http://man7.org/linux/man-pages/man2/poll.2.html),
[epoll](http://man7.org/linux/man-pages/man7/epoll.7.html), ...). If one day you
want to change, you just need to write another implementation of this interface.
As we want to perform operations on I/Os, we will explicitly call it 
*IIoDispatcher*:

    :::cpp
    class IIoDispatcher
    {
    public:
        IIoDispatcher();
        virtual ~IIoDispatcher();

As previously, we will define first an init function:

    :::cpp
        virtual int init() = 0;

The dispatch function that will block as long as the application runs:

    :::cpp
        virtual int dispatch() = 0;

A function to register an *IIoHandler*:

    :::cpp
        virtual int registerIoHandler(IIoHandler& handler) = 0;

Finally a function to break the loop in case we want to exit:

    :::cpp
        virtual int breakLoop() = 0;
    };

Again, we need a concrete implementation. It is not the purpose of this article
to describe all possible system call to peform a *select*, [there are other
great articles](http://www.ulduzsoft.com/2014/01/select-poll-epoll-practical-
difference-for-system-architects/) about this topic. Just be aware of the pro
and contra of each of them to help you decide which one suits you the best.

Despite it is known for being slow, I will stick with the actual *select* call
that is implemented in most decent modern OS. Let's give it an explicit name:

    :::cpp
    class IoDispatcherSelect:
            public IIoDispatcher
    {

We will store the registered *IoHandlers* in a list, a field to remember the
highest file descriptor value, that is specific to *select* and also a running
flag in order to break the loop:

    :::cpp
    private:
        IoHandle m_maxIoHandle;
        bool m_isRunning;
        std::list<IIoHandler*> m_ioHandlers;

First the constructor that initializes everything:

    :::cpp
        IoDispatcherSelect():
                m_maxIoHandle(-1),
                m_isRunning(false)
        {
        }

A destructor that doesn't do much in this implementation:

    :::cpp
        ~IoDispatcherSelect()
        {
        }

Despite the init function might be useful for other calls such as *epoll*, the
select doesn't need to be initialized, so we don't do anything here:

    :::cpp
        int init() override
        {
            return 0;
        }

Finally where things get interesting is in the *dispatch* function. This
implementation is specific to *select* but the main idea is the same for the
other calls despite the API differs. I will try to explain step by step what
should be done.

First the main loop and variables declaration:

    :::cpp
        int dispatch() override
        {
            int ret = 0;

            m_isRunning = true;
            while(m_isRunning)
            {
                fd_set read_fds;
                int selectRes;
                struct timeval timeout;

For each call to select, we need to clear the set of file descriptor that is
stored in a *fd_set* with the *FD_ZERO* macro:

    :::cpp
                FD_ZERO(&read_fds);

This is where *select* is not efficient, we have to loop through our registered
*IIoHandlers* and add their file descriptor in the set with *FD_SET*:

    :::cpp
            for(auto& it: m_readIoHandlers)
                FD_SET(it->getIoHandle(), &read_fds);

I will explain later why using a timeout here is not a good idea but for
simplicity, we will use this solution. We don't want to block in the select call
forever if nothing has to be read, we want to check the running flag status as
well, that's why we prepare a timeout of 1 second:

    :::cpp
                timeout.tv_usec = 0;
                timeout.tv_sec = 1;

Finally the call to select. The first argument is the amount of file descriptors
to watch, the second the set of file descriptor to watch for read, then come the
set for write and exception that we don't use in this example. The last argument
is the *timeval* struct containing the timeout:

    :::cpp
                selectRes = select(m_maxIoHandle + 1, 
                                    &read_fds,
                                    NULL,
                                    NULL,
                                    &timeout);

Once the call returns, we check the return code in case of error. We accept
*EINTR* and perform the select again otherwise exit with an error:

    :::cpp
                if(selectRes < 0)
                {
                    if(errno == EINTR)
                        continue;
                    else
                    {
                        perror("select");
                        ret = -1;
                        break;
                    }
                }

If *select* returns 0, no file descriptor was ready, this means the timeout was
reached, we perform the select again or exit the loop in case the running flag
changed to false:

    :::cpp
                else if(selectRes == 0)
                    continue;

Finally we have to loop again throught the list of regsitered handlers to check
if the file descriptor is ready and call the callback function. Again, this is
where *select* is inefficient:

    :::cpp
                for(auto& it: m_readIoHandlers)
                {
                    if(FD_ISSET(it->getIoHandle(), &read_fds))
                        it->readReady();
                }
            }   // while(m_isRunning)

The loop broke, exit the function with a return code:

    :::cpp
            return ret;
        }

That's it for the dispatch function using select!

Now in the *registerIoHandler* we will store the maximum file descriptor value
for the select call, we also want to make sure that the *IIoHandler* gives a
valid value!

    :::cpp
        int registerIoHandler(IIoHandler& handler) override
        {
            IoHandle handle = handler.getIoHandle();

            assert(handle >= 0);

            if(handle > m_maxFd)
                m_maxIoHandle = handle;

            m_readIoHandlers.push_back(&handler);

            return 0;
        }

To break the loop, it is just a matter of setting the running flag to false:

    :::cpp
    int IoDispatcherSelect::breakLoop() override
    {
        m_isRunning = false;
        return 0;
    }

Now we have all the components we need to write a nice and elegant solution for
our problem, the final step would be writing a main function!

# Wiring all the thing
Now let's write a main.cpp file where all the wiring will be done. We will make
the dispatcher local to access it from other functions:

    :::cpp
    IoDispatcherSelect ioDispatcher;

We also want to catch signals to break the loop, we define here a signal
callback:

    :::cpp
    void onSignal(int signum, siginfo_t *info, void *ptr)
    {
        std::cout << "Reived signal " << signum << " breaking loop!" << 
            std::endl;
        ioDispatcher.breakLoop();
    }

A small function to register to signals:

    :::cpp
    int signalInit()
    {
        struct sigaction act;

        memset(&act, 0, sizeof(act));
        act.sa_sigaction = onSignal;
        act.sa_flags = SA_SIGINFO;

        if(sigaction(SIGTERM, &act, NULL) ||
            sigaction(SIGINT, &act, NULL))
        {
            perror("sigaction");
            return -1;
        }

        return 0;
    }

And finally our main function. We will use two handlers because this is fun and
to show the flexibility of the pattern:

    :::cpp
    int main(int argc, char* argv[])
    {
        NamedPipeToStdout pipe1("/tmp/test_pipe1");
        NamedPipeToStdout pipe2("/tmp/test_pipe2");

        if(signalInit())
            return -1;
        if(ioDispatcher.init())
            return -1;
        if(pipe1.init())
            return -1;
        if(pipe2.init())
            return -1;

        ioDispatcher.registerIoHandler(pipe1);
        ioDispatcher.registerIoHandler(pipe2);

        return mainLoop.dispatch();
    }

# The new status
When running the program, you will notice that 0% of CPU use used while nothing
has to be done. If you do a stress test like this:

> cat /dev/urandom > /tmp/test_pipe1

You will see that a lot of CPU will be used but most time will be spent in other
tasks, our application will use only few resource and reacts directly when
something has to be done. Moreover, you can register a big amount of
*IoHandlers* that will be very responsive!

# What can be improved
I wanted to stay simple and show the mechanism of the pattern but there are few
things missing in this implementation to use it in a production code.

* **Timeout in select**

Due to the timeout in the *select* call, we are still doing some kind of polling
to check the running flag.

To remedy this problem we could use [*signalfd*](http://man7.org/linux/
man-pages/man2/signalfd.2.html) system call in Linux. This allows registering a
file descriptor to watch for signal. Just know that this system call was 
criticized by many people and keep in mind the consequence of using it.

If you don't have this system call, a more portable way would be using the *self
pipe trick*. It consists of creating a pipe, registering the read end in the 
select and write something from the signal handler. The self pipe trick is also
very useful if you want to wake up the main loop from a worker thread.

A nice article about *signalfd* and the *self pipe trick* [is available here](
https://ldpreload.com/blog/signalfd-is-useless).

* **Deregistering handlers**

In a normal application, it often happens that an *IoHandler* wants to
deregister itself from the *Dispatcher*. Especially when writing network 
applications, imagine that a client client disconnects!

I skipped this functionality because this is not so trivial as it might sound.
Make sure this doesn't invalidate your *IoHandler* iterator and that you are not
performing a call on a handler that was already destroyed! The dirty flag might
be helpful here.

* **Other than read events**

You probably noticed that two arguments are set to *NULL* in the *select* call.
This is because it supports other than *read* event. A misconception in this
implementation is that the write can potentially be blocking, that will block
the main thread. It would be wiser to use non blocking write and register to
write event on *EWOULDBLOCK* error. When writing is possible again, you will be
informed by the *Dispatcher*.

* **Signals and timers handlers**

I tried to name my things with the *IO* keyword because I only wanted to handle
I/Os. However a decent main loop would be able to register handlers to catch
signals and timeouts on timers.

How to handle signal was explained previously but how to handle timers? Again
here the self pipe trick can be useful to wake up an object in charge of
managing different timers in the main thread. Another possible implementaiton on
Linux is the *timerfd_create* system call that, as the *signalfd* flavor, it
permits watching timers through a file descriptor.

# Going further with the reactor pattern
I tried to explicitly name my things with the *I/O* keyword because thanks to
the "*Everything is a file*" Unix philosphy, there are a lot of I/Os you can
monitor:

* Mouse, keyboard, joystick from /dev/inputx
* Unix socket
* Serial ports
* GPIOs
* Message queues
* inotify subsystem
* ...

Moreover, you can write a specific *IoHandler* to interprete events coming from
the underlying hardware and generate other than I/Os event:

* Key pressed/released event from a keyboard, GPIO, ...
* Mouse moved, button clicked event from mouse
* New connection event from a server socket (accept)
* Modem event if you are reading AT commands coming from a serial port
* File modified, opened, closed, … from inotify
* ...

Possibilites are infinite!

# Don't write it yourself
This example is purely academic to help understanding what is behind the scene
of many frameworks! If you write an application from scratch, don’t write
the main loop yourself, because it is difficult to do it right and
portable the first time. There are smart people who wrote libraries to solve
specific problem, I specially recommend the [*libevent*](http://libevent.org/)
library, it can handle signals, timers, is fast, portable and the bother of
choosing the right select flavor is transparent.

However writing a generic interface is always a good idea for unit testing. It
should be possible to encapsulate *libevent* instead of the *select*
implementation we wrote together.

# Pro
After going through this small example, I hope you will agree with the following
advantages of the reactor pattern

* It is not very difficult to understand
* It spares resources by using the CPU only when required
* Well defined separation of concerns with different handlers
* Avoid all the thread synchronization headaches

# Contra
There are some limitations but if you are aware of them, there are some
solutions:

* *IoHandler* tasks should be small and fast

If you take too much time to process data, it will block the main thread and all
other registered *IoHandler* consequently. The solution for that is, using a
worker thread and well defined synchronization mechanisms. This is why also in
many frameworks such as QT or Java Swing, you should not perform long task in
callbacks and is even a good practice implementing worker threads in that case.

* It brings more complexity in the code

That's also the drawback of flexibility... This is why you should define
separations of concerns clearly while doing your architecture.

* It doesn't scale well on multi processor architecture

This is true if you are using a single thread but if you doing background job,
your OS will run them on the different cores! If you have a lot of connections
to handle, you can improve performances by using more than one select call in
different threads but do this only if you have good reasons and you did some
benchmarks that showed big benefits!

# Further reading
Some interesting reading that are not linked in the article:

* [A very nice paper about the reactor pattern](http://www.cs.wustl.edu/
~schmidt/PDF/reactor-siemens.pdf)
* [The c10k problem](http://www.kegel.com/c10k.html)
* [Well explained self pipe trick](https://www.sitepoint.com/
the-self-pipe-trick-explained/)

# Conclusion
I hope this small introduction to the reactor pattern showed its flexibility and
what can be achieved! Now you understand why in Java you should write small
handlers when a button is clicked and understand what is behind 
[*QApplication::exec()*](http://doc.qt.io/qt-5/qapplication.html#exec) in QT.

The sources I used to write this article are [available on github](https://
github.com/r4nd0m6uy/reactor_example), feel free to
play and extend it to have a better feeling with the different flavor of select!
