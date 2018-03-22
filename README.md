# Full-stack-Nanodegree
## Project 5: Build an Item Catalog Application
**Project Description** (from Udacity):
>You will develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

### Usage
#### Environment Set up
Make sure you have Git installed. If not, download [here](https://git-scm.com/downloads) <br>
Download and install the correct version of [Vagrant](https://www.vagrantup.com/downloads.html) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads) for your operating system <br>
Fork this [directory](ttps://github.com/udacity/fullstack-nanodegree-vm) and copy the newly forked repository path with clone <br>
From terminal:
```
bash-3.2$ git clone PASTE_COPIED_REPO_LINK_HERE fullstack
```
Download application.py, database_populate.py, database_setup.py, static, and templates from this repository <br>
Copy these 3 files to the fullstack/catalog directory created from the git clone command
#### Run Program
Open terminal and change directory to the cloned fullstack directory:
```
bash-3.2$ cd FULL_PATH_TO_NEWLY_CLONED_DIRECTORY
```
Use the ls command to see 2 files and 1 directory: CODEOWNERS, README.md, vagrant. Change directory to the catalog directory in the vagrant folder:
```
bash-3.2$ ls
CODEOWNERS    README.md     vagrant
bash-3.2$ cd vagrant/catalog
```
Launch virtual machine:
```
bash-3.2$ vagrant up
```
Log in the virtual machine:
```
bash-3.2$ vagrant sh
vagrant@vagrant:~$
```
Change directory to correct folder
```
vagrant@vagrant:~$ cd ../../vagrant/catalog
```
Install external python library required for script
```
vagrant@vagrant:~$ sudo pip install flask_oauth
```
Setup & populate database
```
vagrant@vagrant:~$ python database_setup.py
vagrant@vagrant:~$ python database_populate.py
```
Run program
```
vagrant@vagrant:~$ python application.py
```
