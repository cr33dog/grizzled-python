# $Id$

"""
This module contains file- and path-related methods and classes.
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import os
import sys

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def unlinkQuietly(path):
    """
    Like the standard C{os.unlink()} function, this function attempts to
    delete a file. However, it swallows any exceptions that occur during the
    unlink operation, making it more suitable for certain uses (e.g.,
    in C{atexit} handlers).

    @type path:  string
    @param path: path to unlink
    """
    try:
        os.unlink(path)
    except:
        pass

def recursivelyRemove(dir):
    """
    Recursively remove all files and directories below and including a specified
    directory.

    @type dir:  string
    @param dir: path to directory to remove
    """
    if not os.path.exists(dir):
        return

    for dir, subdirs, files in os.walk(dir, topdown=False):
        if files:
            for f in files:
                try:
                    os.unlink(os.path.join(dir, f))
                except OSError, e:
                    raise
                except:
                    raise OSError, 'Failed to delete file "%s" in "%s: %s' %\
                                   (f, dir, sys.exc_info()[1])
        os.rmdir(dir)

def copy(files, targetDir, createTarget=False):
    """
    Copy one or more files to a target directory.

    @type files:  string or list
    @param files: a single file path or a list of file paths to be copied

    @type targetDir:  string
    @param targetDir: path to target directory

    @type createTarget:  boolean
    @param createTarget: If C{True}, C{copy()} will attempt to create the
                         target directory if it does not exist. If C{False},
                         C{copy()} will throw an exception if the target
                         directory does not exist.
    """
    if type(files) == str:
        files = [files]

    if not os.path.exists(targetDir):
        if createTarget:
            os.mkdir(targetDir)

    if os.path.exists(targetDir) and (not os.path.isdir(targetDir)):
        raise OSError, 'Cannot copy files to non-directory "%s"' % targetDir

    import shutil

    for f in files:
        targetFile = os.path.join(targetDir, os.path.basename(f))
        o = open(targetFile, 'wb')
        i = open(f, 'rb')

def touch(files, times=None):
    """
    Similar to the Unix I{touch}(1) command, this function:

     - updates the access and modification times for any existing files
       in a list of files
     - creates any non-existent files in the list of files

    If any file in the list is a directory, this function will throw an
    exception.

    @type files:  list or string
    @param files: pathname or list of pathnames of files to be created or
                  updated

    @type times:  tuple
    @param times: tuple of the form (I{atime}, I{mtime}), identical to
                  what is passed to the standard C{os.utime()} function.
                  If this tuple is C{None}, then the current time is used.
    """
    if type(files) == str:
        files = [files]

    for f in files:
        if os.path.exists(f):
            if not os.path.isfile(f):
                raise OSError, "Can't touch non-file \"%s\"" % f
            os.utime(f, times)

        else:
            # Doesn't exist. Create it.

            open(f, 'wb').close()