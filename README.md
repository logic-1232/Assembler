# Assembler

An assembler for the 32-bit RISC-V instruction set.

In order to adapt to the optional extension features of RISC-V, the assembler can configure the supported extensions in the variable `cmd_set` in `main.py`. The currently supported extensions include **I, M, F, D, and C**. When selecting the C extension, the assembler will automatically compress the compressible instructions.

The assembler supports parsing aliases for general registers, comment statements (starting with `#`), and jump markers (on a separate line and ending with `:`).

Remaining issues:

- For the convenience of parsing, there are some differences between the assembly program of this project and the standard assembly syntax. In the assembly statement of this project, each part is separated by any number of spaces, and the syntax of `offset(rs1)` has been changed to `rs1 offset`.
- There is still a bug with the compression instruction, which has been explained in the program and will not be repeated here.
