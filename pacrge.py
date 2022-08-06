import os
import subprocess
import argparse
import distro
import wget

pargeDir = f"{os.getenv('HOME')}/.cache/parge"
breakWay = 0


def keyVerification():
    parser = argparse.ArgumentParser(description="Turning Arch Linux into Gentoo")
    parser.add_argument("-a", "--all",
                        help="Compiling packages that are already installed on the system and for which updates are available",
                        action="store_true")
    parser.add_argument("-u", "--upgrade", help="Compiling only those packages that are available for upgrade(default)",
                        action="store_true")
    global args
    args = parser.parse_args()


def dependencyCheck():
    if distro.name() != "Arch Linux":
        print("This script is only intended for Arch Linux")
        breakWay = 1
    elif not os.path.exists("/usr/bin/asp"):
        print("You do not have ASP (Arch Build System) installed")
        global aspInst
        aspInst = input("You want to install it? [Y/n] ").upper()
        if aspInst == 'Y':
            os.system("sudo pacman -Sy asp")
            return 0
        else:
            return 1


# def sourceDirectory():
#     print(f"The default directory will be {os.getenv('HOME')}/Tools/pacrge")
#     aspDirAsk = input("Do you want to change? [Y/n]").upper()
#     if aspDirAsk == 'Y':
#         aspDir == input("Enter the full path to the new directory")
#         os.makedirs(f"")


def directory():
    os.makedirs(pargeDir, exist_ok=True)
    os.chdir(pargeDir)


def getPackage():
    if not dependencyCheck():
        os.system("sudo pacman -Sy")
    global uPackage
    if getattr(args, "all"):
        uPackage = subprocess.getoutput("pacman -Qnq").split()
    else:
        uPackage = subprocess.getoutput("pacman -Quq").split()
    return uPackage



def getClang():
    if not os.path.exists(f"{pargeDir}/makepkg-clang.conf"):
        wget.download("https://pastebin.com/raw/qBx1xc0x")
        os.rename(f"{pargeDir}/qBx1xc0x", f"{pargeDir}/makepkg-clang.conf")
    if not os.path.exists(f"{pargeDir}/package-clang"):
        global packageClang
        packageClang = open("package-clang", "w+")
        packageClang.close()
    packageClang = open("package-clang")
    return packageClang.read().split()


def getMakepkg():
    for i in uPackage:
        if not os.path.exists(i):
            os.system(f"asp checkout {i}")


def getComplining():
    global fPackage
    fPackage = list()
    for i in uPackage:
        os.chdir(f"{i}/trunk")
        if i in getClang():
            if not os.system(f"yes | makepkg -sric --config {pargeDir}/makepkg-clang.conf"):
                fPackage.append(f"{i}(clang)")
        if not os.system("yes | makepkg -sric"):
            fPackage.append(i)
        os.chdir("../..")


def getFailed():
    if len(fPackage) != 0:
        print("failed to build the following packages:\033[1;31m", '\033[0m,\033[1;31m '.join(str(x) for x in fPackage))
    elif not len(uPackage):
        print("\033[1;31mNo upgrade packages are available")


def main():
    keyVerification()
    dependencyCheck()
    if not breakWay:
        directory()
        getPackage()
        getClang()
        getMakepkg()
        getComplining()
        getFailed()


main()
