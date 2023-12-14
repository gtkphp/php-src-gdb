# php-src-gdb
Debugging Helpers for QtCreator

![zval of zend_string display](https://github.com/gtkphp/php-src-gdb/blob/main/zval.png "QtCreator debuger")

Debugging Helpers for GDB

```console
$ gdb -ix php-src/.gdbinit php-install/bin/php
(gdb) break php-src/ext/ftp/ftp.c:711
(gdb) run -f test.php
Breakpoint 1,
  ...
(gdb) print zstr
$1 = (zend_string *) 0x7ffff6882960
(gdb) print_zstr zstr
string(9) "Hello GDB"
(gdb) print $1->len
$2 = 9
(gdb) print $1->val
$3 = "H"
(gdb) print $1->gc
$4 = {refcount = 1, u = {type_info = 22}}
```

## Using Debugging Helpers

To show complex structures, such as HashTable* or zval, in a clear and concise manner, Qt Creator uses Python scripts that are called debugging helpers.
