import sublime
import sublime_plugin
import os
import shutil
import zipfile
import json


# _settings = sublime.load_settings('PackageSync.sublime-settings')

# def get_settings(name, default=None):
#     return _settings.get(name, default)

#: Path to folder where backups are stored
_backupLocation = os.path.join(os.path.expanduser('~'), 'Desktop')

#: Path of file to be used when backing up to or restoring from the sublime-settings file for Package Control
_packageControlSettingsBackup = os.path.join(
    _backupLocation, 'SublimePackagesList.txt')

#: Path of the installed '/packages/user/' folder to backup or restore
_userSettingsFolder = os.path.join(sublime.packages_path(), 'User')

#: Path to be used when backing up to or restoring from the '/packages/user' folder as a folder
_userSettingsBackupFolder = os.path.join(
    _backupLocation, 'SublimePackagesBackup')

#: Path to be used when backing up to or restoring from the '/packages/user' folder as a zip file
_userSettingsBackupZip = os.path.join(
    _backupLocation, 'SublimePackagesBackup.zip')


def _removeExistingBackup(backupPath):
    if os.path.isdir(backupPath):
        shutil.rmtree(backupPath, True)
    elif os.path.isfile(backupPath):
        os.remove(backupPath)


class BackupInstalledPackagesListCommand(sublime_plugin.WindowCommand):

    def run(self):
        """ Backup the sublime-settings file for Package Control.
        This file contains the list of installed packages.
        The backup is stored on the backup location with the name specified in the
        config file. """

        _packageControlSettings = sublime.load_settings(
            'Package Control.sublime-settings')
        _installed_packages = _packageControlSettings.get('installed_packages') or []

        with open(_packageControlSettingsBackup, 'w') as _backupFile:
            json.dump({'installed_packages': _installed_packages}, _backupFile)


class RestoreInstalledPackagesListCommand(sublime_plugin.WindowCommand):

    def run(self):
        """ Restore the sublime-settings file for Package Control.
        This file contains the list of installed packages.
        The backup file should be stored on the backup location with the name
        specified in the config file. """

        if os.path.isfile(_packageControlSettingsBackup):
            with open(_packageControlSettingsBackup, 'r') as _backupFile:
                _installed_packages = json.load(
                    _backupFile)['installed_packages']

                _packageControlSettings = sublime.load_settings(
                    'Package Control.sublime-settings')
                _packageControlSettings.set(
                    'installed_packages', _installed_packages)
                sublime.save_settings('Package Control.sublime-settings')

                sublime.message_dialog(
                    'Packages list has been updated. Please restart Sublime Text to download the missing packages.')
        else:
            sublime.error_message(
                'Could not find packages list backup file at location %s' % _packageControlSettingsBackup)


class BackupPackagesToFolderCommand(sublime_plugin.WindowCommand):

    def run(self):
        """ Backup the "/Packages/User" folder to the backup location.
        This backs up the sublime-settings file created by user settings.
        Package Control settings file is also inherently backed up. """

        _removeExistingBackup(_userSettingsBackupFolder)
        try:
            shutil.copytree(_userSettingsFolder, _userSettingsBackupFolder)
        except Exception as e:
            raise e


class RestorePackagesFromFolderCommand(sublime_plugin.WindowCommand):

    def run(self):
        """ Restore the "/Packages/User" folder from the backup location.
        This restores the sublime-settings file created by user settings.
        Package Control settings file is also inherently restored. """

        if os.path.isdir(_userSettingsBackupFolder):
            try:
                shutil.rmtree(_userSettingsFolder)
                shutil.copytree(_userSettingsBackupFolder, _userSettingsFolder)
                sublime.message_dialog(
                    'Packages list & settings have been updated. Please restart Sublime Text to download the missing packages.')
            except Exception as e:
                raise e
        else:
            sublime.error_message(
                'Could not find packages backup folder at location %s' % _userSettingsBackupFolder)


class BackupPackagesToZipCommand(sublime_plugin.WindowCommand):

    def run(self):
        """ Backup the "/Packages/User" folder to the backup location.
        This backs up the sublime-settings file created by user settings.
        Package Control settings file is also inherently backed up. """

        if os.path.isfile(_userSettingsBackupZip):
            os.remove(_userSettingsBackupZip)
        try:
            shutil.make_archive(
                _userSettingsBackupFolder, 'zip', _userSettingsFolder)
        except Exception as e:
            raise e


class RestorePackagesFromZipCommand(sublime_plugin.WindowCommand):

    def run(self):
        """ Restore the "/Packages/User" folder from the backup location.
        This restores the sublime-settings file created by user settings.
        Package Control settings file is also inherently restored. """

        if os.path.isfile(_userSettingsBackupZip):
            try:
                shutil.rmtree(_userSettingsFolder)
                with zipfile.ZipFile(_userSettingsBackupZip, 'r') as z:
                    z.extractall(_userSettingsFolder)
                sublime.message_dialog(
                    'Packages list & settings have been updated. Please restart Sublime Text to download the missing packages.')
            except Exception as e:
                raise e
        else:
            sublime.error_message(
                'Could not find packages backup zip at location %s' % _userSettingsBackupZip)
