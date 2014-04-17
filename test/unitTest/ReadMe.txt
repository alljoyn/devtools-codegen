==================
Copyright (c) 2013, 2014 AllSeen Alliance. All rights reserved.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
==================

Unit tests can only be run after the code generator has been installed!

To run all unit tests on Windows use this command:

    python -m unittest discover . *_test.py

To run all unit tests on Linux use this command:

    python -m unittest discover . '*_test.py'

To run a single file of tests use this command:

    python -m unittest <file>

Where <file> does NOT include the ".py". For example:

    python -m unittest parse_test

To run a single class of tests in a file use this command:

    python -m unittest parse_test <file>.<class>

For example:

    python -m unittest parse_test.TestParse

To run a single test use this command:

    python -m unittest <file>.<class>.<test>

For example:

    python -m unittest parse_test.TestParse.test_invalid_filename

==================
Thin Client Unit tests (tc_test.py) under Windows 
==================
If the enviroment variable ALLJOYN_THINCLIENT_HOME is set to the root directory
of your Thin Client source installation then the thin client unit tests will
compile 

=C:\Workspace\core\ajtcl
