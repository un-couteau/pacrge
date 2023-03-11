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
import sys
import typing

import distro

__author__ = "Software Un Couteau"
__copyright__ = "Copyright (C) 2022-2023 Un Couteau"
__license__ = "GNU GPLv3"
__version__ = "1.0"


def distro_check():
    if distro.name() != "Arch Linux":
        sys.exit("This script is only intended for Arch Linux")


def config_parse():
    config = configparser.ConfigParser()
    config["general"] = {"FolderForAssembly": "",
                         "ClangPackages": "",
                         "ClangPackagesLTO": "",
                         "GccPackagesLTO": ""}
    with open("pacrge.conf", "w+") as config_file:
        config.write(config_file)


def key_verification():
    parser = argparse.ArgumentParser(description="Turning Arch Linux into Gentoo")
    parser.add_argument("-a", "--all",
                        help="compiling packages that are already installed on the system and for which updates are available",
                        action="store_true")
    parser.add_argument("-u", "--upgrade", help="compiling only those packages that are available for upgrade(default)",
                        action="store_true")
    parser.add_argument('--src',
                        help="change the package build directory",
                        action="store_true")
    global args
    args = parser.parse_args()


def dependency_check() -> bool:
    if not os.path.exists("/usr/bin/asp"):
        print("You do not have ASP (Arch Build System) installed")

        asp_install: str = input("You want to install it? [Y/n] ").upper()
        if asp_install == 'Y' or asp_install == '':
            os.system("sudo pacman -Sy asp")
            return True
        return False


def source_directory() -> typing.NoReturn:
    if not os.path.exists(".config"):
        print(f"The default directory for the build is src")

        asp_dir_ask = input("Do you want to change? [Y/n]").upper()
        if asp_dir_ask == 'Y' or asp_dir_ask == '':
            asp_dir_src = input("Enter the directory for the build: ")
            try:
                if asp_dir_src.find('~') != -1:
                    os.makedirs(asp_dir_src, exist_ok=True)
                    os.chdir(
                        f"{os.getenv('HOME')}{asp_dir_src[1::]}")  # если функция вернет ошибку, то сработает except
                else:
                    os.makedirs(asp_dir_src, exist_ok=True)
                    os.chdir(asp_dir_src)  # если функция вернет ошибку, то сработает except

                with open(".config", "w") as file:
                    file.write(asp_dir_src)
            except:
                sys.exit("Wrong path indicated")


def get_package() -> list[str]:
    global upgrade_package
    if getattr(args, "all"):
        upgrade_package = subprocess.getoutput("pacman -Qnq").split()
        return upgrade_package
    upgrade_package = subprocess.getoutput("pacman -Quq").split()
    return upgrade_package


def get_clang():
    if not os.path.exists("package-clang"):
        global package_clang
        package_clang = open("package-clang", "w+")
        package_clang.close()
    package_clang = open("package-clang")
    return package_clang.read().split()


def get_makepkg():
    for i in upgrade_package:
        if not os.path.exists(i):
            os.system(f"asp checkout {i}")


def get_complining():
    global failed_package
    failed_package: list[str]

    for i in upgrade_package:
        os.chdir(f"{i}/trunk")
        if i in get_clang():
            if not os.system(f"yes | makepkg -sric --config {pargeDir}/makepkg-clang.conf"):
                failed_package.append(f"{i}(clang)")
        if not os.system("yes | makepkg -sric"):
            failed_package.append(i)
        os.chdir("../..")


def get_failed():
    if len(failed_package) != 0:
        print("failed to build the following packages:\033[1;31m",
              '\033[0m,\033[1;31m '.join(str(x) for x in failed_package))
    elif not len(upgrade_package):
        print("\033[1;31mNo upgrade packages are available\033[0;0m")


def main():
    distro_check()
    key_verification()
    dependency_check()
    source_directory()
    get_package()
    get_clang()
    get_makepkg()
    get_complining()
    get_failed()


if __name__ == '__main__':
    main()
