If You try to create logical partitions with this tool, probably You are 
going to encounter errors. It's not because of the tool itself but a bug 
within the UDisks system, which is used by the tool.

Error still present in udisks 1.0.4-2.

For further information, please follow the links below:

http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=652993
  udisks: Device or resource busy when creating logical partition

https://bugs.freedesktop.org/show_bug.cgi?id=44080
  Device or resource busy when creating logical partition

https://bugs.launchpad.net/ubuntu/+source/gnome-disk-utility/+bug/666038
  error while creating logical partition

http://ftp.osuosl.org/pub/linux/utils/util-linux/libblkid-docs/libblkid-Partitions-probing.html
  blkid_partition_get_size ()
  [...]
  WARNING: be very careful when you work with MS-DOS extended 
  partitions. The library always returns full size of the partition. If 
  you want add the partition to the Linux system (BLKPG_ADD_PARTITION 
  ioctl) you need to reduce   the size of the  partition to 1 or 
  2 blocks. The rest of the partition has to be unaccessible for mkfs or 
  mkswap programs, we need a small space for boot loaders only.
