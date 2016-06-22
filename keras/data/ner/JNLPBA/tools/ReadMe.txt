- evalIOB2.pl

It is a general command to evaluate the result of object
identification by comparing a provided answer file containing a result
of object identification with a provided reference file containing the
correct answer.  Just executing the command without any argument will
show the usage of the command.


- SharedTaskEval.pl

It is a script to perform the evaluation especially for the JNLPBA
shared task.  Use this script to get the evaluation equivalent to that
of the shared task.

e.g) SharedTaskEval.pl your_answer_file


- Genia4EReval.ref

This file contains the correct answer of the shared task


- *.lst

These files contain UIDs pertaining to each era.


(*) Note that the configuration of the test file should be kept to use
this script. In other words, arbitrary empty lines should not be added
or deleted and the "###MEDLINE:..." lines should not be deleted from
the result file.
