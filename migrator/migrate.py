#!/usr/bin/env python

"""This script migrates Inboard beta library to Inboard App Store version
library."""

import sqlite3
import os
from os.path import expanduser
import subprocess
import shutil

COLOR = "\033[1;32m"
RED = '\033[1;31m'
NOCOLOR = "\033[0m"

GROUP_CONTAINER = expanduser("~/Library/Group Containers/")
MAS_CONTAINER_DIRNAME = "AN5MJ93DEM.com.ideabits"
MAS_CONTAINER = os.path.join(GROUP_CONTAINER, MAS_CONTAINER_DIRNAME)
MAS_DB = os.path.join(MAS_CONTAINER, "Inboard/Inboard.sqlite")
FILES_TO_BACKUP = (
    (os.path.join(MAS_CONTAINER, "Inboard/Inboard.sqlite"), os.path.join(MAS_CONTAINER, "Inboard/InboardBackup.sqlite")),
    (os.path.join(MAS_CONTAINER, "Inboard/Inboard.sqlite-shm"), os.path.join(MAS_CONTAINER, "Inboard/InboardBackup.sqlite-shm")),
    (os.path.join(MAS_CONTAINER, "Inboard/Inboard.sqlite-wal"), os.path.join(MAS_CONTAINER, "Inboard/InboardBackup.sqlite-wal")),
)
BETA_CONTAINER_DIRNAME = "V7X89GG36Z.com.ideabits"
BETA_CONTAINER = os.path.join(GROUP_CONTAINER, BETA_CONTAINER_DIRNAME)


class MigrationError(Exception):
    pass


class NothingToMigrate(Exception):
    pass


def backup():
    if os.path.exists(BETA_CONTAINER):
        if subprocess.call(
                ["zip", "-r",
                 expanduser("~/Desktop/inboard_beta_library_backup.zip"),
                 BETA_CONTAINER],
                stdout=open(os.devnull, "wb")):
            raise MigrationError
    else:
        raise NothingToMigrate

    if os.path.exists(MAS_CONTAINER):
        if subprocess.call(
                ["zip", "-r",
                 expanduser("~/Desktop/inboard_app_store_library_backup.zip"),
                 MAS_CONTAINER],
                stdout=open(os.devnull, "wb")):
            raise MigrationError


def move_dir():
    if os.path.exists(MAS_CONTAINER):
        shutil.rmtree(MAS_CONTAINER)
    os.rename(BETA_CONTAINER, MAS_CONTAINER)


def backup_db():
    for backup in FILES_TO_BACKUP:
        original_file, backup_file = backup
        shutil.copyfile(original_file, backup_file)


def migrate_db():
    conn = sqlite3.connect(MAS_DB)
    c = conn.cursor()
    c.execute('UPDATE ZITEM SET ZPATH = REPLACE(ZPATH, "{}", "{}")'.format(
        BETA_CONTAINER_DIRNAME, MAS_CONTAINER_DIRNAME))
    conn.commit()
    conn.close()


def main():
    if subprocess.call(["pgrep", "Inboard"], stdout=open(os.devnull, "wb")) == 0:
        print RED + "[!] Please quit Inboard before migration." + NOCOLOR
        return

    try:
        print "{}[1/3]{} Creating backup file...".format(COLOR, NOCOLOR)
        backup()
        print "      Backup file is created at Desktop"

        print "{}[2/3]{} Moving library directory...".format(COLOR, NOCOLOR)
        move_dir()
        print "      Done"

        print "{}[3/3]{} Migrating database file...".format(COLOR, NOCOLOR)
        backup_db()
        migrate_db()
        print "      Done"
    except MigrationError:
        print "      Failed. Please contact us for help."
    except NothingToMigrate:
        print "      Nothing to migrate."
    else:
        print("Finished! You can open Inboard now. If everything is fine, you "
              "can remove the backup file at Desktop. If you encounter trouble,"
              " please email support@inboardapp.com")


if __name__ == "__main__":
    main()
