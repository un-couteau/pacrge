# -*- coding: utf-8 -*-

'''
Presents Un Couteau build packages with makepkg settings

Page shell scripts containing the information needed to build an Arch Linux package.
Takes PKGBUILD and starts a MAKEPKG build script specifying custom makepkg(for building with clang, lto, gcc, etc.)
'''

import argparse
import configparser
import os
import subprocess
import typing

import distro

__author__ = "Software Un Couteau"
__copyright__ = "Copyright (C) 2022-2023 Un Couteau"
__license__ = "GNU GPLv3"
__version__ = "1.0"


def distro_check() -> bool:
    if distro.name() == "Arch Linux":
        return True
    return False


def config_generate() -> typing.NoReturn:
    if not os.path.exists("./config/pacrge.conf"):
        config = configparser.ConfigParser()
        config["general"] = {"Folder-For-Assembly": "",
                             "Clang-Packages": "",
                             "Clang-Packages-LTO": "",
                             "Gcc-Packages-LTO": "",
                             "#list package names with ','": "example: Clang-Packages-LTO: mesa,firefox"}
        with open("./config/pacrge.conf", "w+") as config_file:
            config.write(config_file)


def config_parse() -> typing.NoReturn:
    global config
    config = configparser.ConfigParser()
    config.read("./config/pacrge.conf")
    global package_clang_lto
    global package_gcc_lto
    global package_clang

    package_clang_lto = config["general"]["clang-packages-lto"].split(',')
    package_gcc_lto = config["general"]["gcc-packages-lto"].split(',')
    package_clang = config["general"]["clang-packages"].split(',')


def key_verification():
    parser = argparse.ArgumentParser(description="Turning Arch Linux into Gentoo")
    parser.add_argument("-a", "--all",
                        help="compiling packages that are already installed on the system and for which updates are available",
                        action="store_true")
    parser.add_argument("-u", "--upgrade", help="compiling only those packages that are available for upgrade(default)",
                        action="store_true",
                        default=True)
    # parser.add_argument('--src',
    #                     help="change the package build directory",
    #                     action="store_true")
    global args
    args = parser.parse_args()


def dependency_check() -> bool:
    if not os.path.exists("/usr/bin/asp"):
        print("You do not have ASP (Arch Build System) installed")

        asp_install: str = input("You want to install it? [\033[32mY\033[0m/\033[31mn\033[0m] ").upper()
        try:
            if asp_install == 'Y' or asp_install == '':
                if os.system("sudo pacman -Sy asp") == 0:
                    return True
        finally:
            return False
    return True


def source_directory() -> typing.NoReturn:
    if config["general"]["folder-for-assembly"] == '':
        print(f"The default directory for the build is src")

        asp_dir_ask: str = input("Do you want to change? [\033[32mN\033[0m/\033[31my\033[0m]: ").lower()
        global script_dir
        script_dir = os.getcwd()
        if asp_dir_ask == 'y':
            asp_dir_src: str = input("Enter the directory for the build: ")
            try:
                if asp_dir_src.find('~') != -1:
                    asp_dir_src = f"{os.getenv('HOME')}{asp_dir_src[1::]}"
                    os.makedirs(asp_dir_src, exist_ok=True)
                    os.chdir(asp_dir_src)
                    config.set("general", "folder-for-assembly", asp_dir_src)
                    return True
            finally:
                return False
        else:
            os.makedirs("src", exist_ok=True)
            config.set("general", "folder-for-assembly", f"{script_dir}/src")

            with open("config/pacrge.conf", "w+") as config_file:
                config.write(config_file)
            os.chdir(f"{script_dir}/src")
            return True
    else:
        os.chdir(config["general"]["folder-for-assembly"])
        return True


def get_package() -> bool:
    os.system("sudo pacman -Sy")

    global upgrade_package
    if getattr(args, "all"):
        upgrade_package = subprocess.getoutput("pacman -Qnq").split()
        return True
    elif getattr(args, "upgrade"):
        upgrade_package = subprocess.getoutput("pacman -Quq").split()
        return True
    return False


def get_makepkg() -> typing.NoReturn:
    if not len(upgrade_package):
        return False
    for i in upgrade_package:
        if not os.path.exists(i):
            os.system(f"asp checkout {i}")
        else:
            os.chdir(i)
            os.system("git pull")
            # # git.Remote.pull(self=)
            os.chdir("../")
    return True


def get_complining() -> typing.NoReturn:
    global failed_package_gcc
    global failed_package_gcc_lto
    global failed_package_clang
    global failed_package_clang_lto
    failed_package_gcc = list()
    failed_package_gcc_lto = list()
    failed_package_clang = list()
    failed_package_clang_lto = list()

    for i in upgrade_package:
        os.chdir(f"{i}/trunk")
        if i in package_clang_lto:
            if os.system(f"yes | makepkg -sric --config {script_dir}/makepkg-clang-lto.conf") != 0:
                failed_package_clang_lto.append(i)
            os.chdir("../../")
        elif i in failed_package_gcc_lto:
            if os.system(f"yes | makepkg -sric --config {script_dir}/makepkg-gcc-lto.conf") != 0:
                failed_package_gcc_lto.append(i)
            os.chdir("../../")
        elif i in failed_package_clang:
            if os.system(f"yes | makepkg -sric --config {script_dir}/makepkg-clang.conf") != 0:
                failed_package_clang.append(i)
            os.chdir("../../")
        else:
            if os.system(f"yes | makepkg -sric --config {script_dir}/makepkg-gcc.conf") != 0:
                failed_package_gcc.append(i)
            os.chdir("../../")


def get_failed() -> typing.NoReturn:
    if len(failed_package_gcc) + len(failed_package_gcc_lto) + len(failed_package_clang) + len(
            failed_package_clang_lto) != 0:
        print("the following packages were assembled unsuccessfully:")

        if failed_package_clang_lto:
            print("Clang LTO: \033[1;31m", '\033[0m,\033[1;31m '.join(str(x) for x in failed_package_clang_lto))
        if failed_package_clang:
            print("Clang: \033[1;31m", '\033[0m,\033[1;31m '.join(str(x) for x in failed_package_clang))
        if failed_package_gcc_lto:
            print("GCC LTO: \033[1;31m", '\033[0m,\033[1;31m '.join(str(x) for x in failed_package_gcc_lto))
        if failed_package_gcc:
            print("GCC: \033[1;31m", '\033[0m,\033[1;31m '.join(str(x) for x in failed_package_gcc))


def main():
    if distro_check():
        config_generate()
        config_parse()
        key_verification()
        if dependency_check():
            if source_directory():
                if get_package():
                    if get_makepkg():
                        get_complining()
                        get_failed()
                    else:
                        print("Nothing to update")
                else:
                    print("The wrong argument was entered")
            else:
                print("Wrong path indicated")
        else:
            print("Without ASP, the script can not continue to work")
    else:
        print("This script is only intended for Arch Linux")


if __name__ == '__main__':
    main()
