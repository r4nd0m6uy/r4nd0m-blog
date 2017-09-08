Title: Interrupt driven user space application with the uio driver
Date: 2017-07-09 20:00
Category: Programming
Tags: linux, tutorial

I would like to present here a simple solution to write an interrupt driven user
space application with the help of the generic user IO kernel driver. It permits
sharing a part of the memory to the user space and catch a given interrupt
without the need of programming a specific kernel driver.

We will go through an example on a zynq platform and a programmable logic that
raises an interrupt after filling some memory area with a counter.

# The programmable logic
Unfortunately, the programmable logic was not written by myself because this is
not my domain of action and I have colleagues who are good at writing VHDL. I
just had to make sure that the FPGA is programmed correctly.

On the zynq there are different flavors of doing this, but it's not the purpose
of this article to explain this, you can refer to the
[Xilinx documentation](http://www.wiki.xilinx.com/Programming+the+Programmable+Logic)
 instead.

# Kernel configuration
Here is how you can enable the uio driver in the kernel configuration menu:

```txt
Device Drivers  --->
  <*> Userspace I/O drivers  --->
    <*>   Userspace I/O platform driver with generic IRQ handling
    <*>   Userspace platform driver with generic irq and dynamic memory
```

This should activate the following options in your .config:

```txt
CONFIG_UIO=y
CONFIG_UIO_PDRV_GENIRQ=y
CONFIG_UIO_DMEM_GENIRQ=y
```

# Device tree
To activate the driver, you have to update the device tree with the IRQ
information and memory space that you want to share. In our example, the FPGA
will write at address *0x100000* and use the IRQ *61*.

An common mistake is not defining the right address size, **it must be aligned
with the page size**. On the zynq, it must be a multiple of *0x1000* (4Kb).

On zynq platform, computing the IRQ number is a bit special ... For more details
please read [this excellent article](http://billauer.co.il/blog/2012/08/irq-zynq-dts-cortex-a9/).
Basically what we need to do here is *61 - 32* that gives use the interrupt
*29*.

```txt
&amba {
	counters@100000 {
		compatible = "fpga-counter";
		reg = < 0x100000 0x1000 >;
		interrupts = < 0 29 1 >;
		interrupt-parent = <&intc>;
	};
};
```

# Command line arguments
The uio driver need some command line argument in order to know on which
compatible driver is our generic uio driver mapped (*compatible*). In our case,
this is what need to be added:

```txt
uio_pdrv_genirq.of_id="fpga-counter"
```

# Verifying
Once we have uploaded the new kernel, device tree and updated the command line
arguments, we can verify that the kernel implementation works as expected.

The first thing to check is if the command line argument was given correctly:
```txt
# cat /proc/cmdline
console=ttyPS0,115200 quiet uio_pdrv_genirq.of_id=fpga-counter root=/dev/mmcblk0p2 rw rootwait rootfstype=ext4
```

A new uio char device should be available in */dev* and */sys/class/uio*

```txt
# ls /sys/class/uio/
uio0
# cat /sys/class/uio/uio0/name
counters
# ls -l /dev/uio0
crw-------    1 root     root      245,   0 Sep  7 14:17 /dev/uio0
```

Also make sure that the correct interrupt is registered:

```txt
# cat /proc/interrupts
           CPU0       CPU1
...
167:          0          0     GIC-0  61 Edge      counters
...
```

If ereything look good, we can now write the user space application to catch
interrupts raised by the FPGA.

# uio user space interface
Once the char device is available, you can access it with the standard C library
calls.

**open(...)**

To open the char device and get a file descriptor.

**read(...)**

Blocking read until an interrupt is raised. The result will contain the amount
of interrupts that occured. **It is important to read 32 bits**, otherwise you
will get an error from the driver.

If you don't want to block on the read and do something else in background, a
*select* call can be used as well.

**write(...)**

The interrupt must be acknowledged with a write. Also here, **make sure that you
write a 32 bits value**, to avoid an error from the driver. The written value
must be bigger or equal to 1, otherwise the interrupt will not be acknowledged
and not be raised again.

**mmap(...)**

To map the memory region to the user space. As in the device tree, the **length
argument must be aligned to the page size**, otherwise you will get an error
from the driver.

# Example application
Once we know everything we need to start coding, we can write a small user space
application:

```c
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>

#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <stdio.h>

#define UIO_DEVICE    "/dev/uio0"
#define MMAP_SIZE     0x1000

int main(int argc, char* argvp[])
{
  int retCode = 0;
  int uioFd;
  volatile uint32_t* counters;

  // Open uio device
  uioFd = open(UIO_DEVICE, O_RDWR);
  if(uioFd < 0)
  {
    fprintf(stderr, "Cannot open %s: %s\n", UIO_DEVICE, strerror(errno));
    return -1;
  }

  // Mmap memory region containing counters value
  counters = mmap(NULL, MMAP_SIZE, PROT_READ, MAP_SHARED, uioFd, 0);
  if(counters == MAP_FAILED)
  {
    fprintf(stderr, "Cannot mmap: %s\n", strerror(errno));
    close(uioFd);
    return -1;
  }

  // Interrupt loop
  while(1)
  {
    uint32_t intInfo;
    ssize_t readSize;

    // Acknowldege interrupt
    intInfo = 1;
    if(write(uioFd, &intInfo, sizeof(intInfo)) < 0)
    {
      fprintf(stderr, "Cannot acknowledge uio device interrupt: %s\n",
        strerror(errno));
      retCode = -1;
      break;
    }

    // Wait for interrupt
    readSize = read(uioFd, &intInfo, sizeof(intInfo));
    if(readSize < 0)
    {
      fprintf(stderr, "Cannot wait for uio device interrupt: %s\n",
        strerror(errno));
      retCode = -1;
      break;
    }

    // Display counter value
    printf("We got %lu interrupts, counter value: 0x%08x\n",
      intInfo, counters[0]);
  }

  // Should never reach
  munmap((void*)counters, MMAP_SIZE);
  close(uioFd);

  return retCode;
}
```

If everything works fine, you should get some event from the driver:

```txt
...
We got 63 interrupts, counter value: 0x9e9fffa6
We got 64 interrupts, counter value: 0x9e9fffa7
...
```

The amount of interrupts should correspond to what is in */proc/interrupts*

```txt
# cat /proc/interrupts
           CPU0       CPU1
167:         64          3     GIC-0  61 Edge      counters
```

# Further reading
* [Kernel documentation](https://www.kernel.org/doc/html/latest/driver-api/uio-howto.html)

# Conclusion
The uio driver is good for quick tests and prototyping. Unfortunately, it is not
as fast as a kernel space dedicated driver. If we have real time constraints,
the uio driver should not be used.
