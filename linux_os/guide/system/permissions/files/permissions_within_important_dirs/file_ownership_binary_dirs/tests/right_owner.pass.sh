#!/bin/bash

{{% if 'ubuntu' in product %}}
find /bin/ /usr/bin/ /usr/local/bin/ /sbin/ /usr/sbin/ /usr/local/sbin/ \! -uid -{{{ uid_min }}} -execdir chown root {} \;
{{% else %}}
find /bin/ /usr/bin/ /usr/local/bin/ /sbin/ /usr/sbin/ /usr/local/sbin/ /usr/libexec \! -user root -execdir chown root {} \;
{{% endif %}}
