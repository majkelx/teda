from enum import Enum

from PySide6.QtCore import QCommandLineParser, QCommandLineOption, QStringListModel, QCoreApplication
from PySide6.QtWidgets import QApplication


class CommandLineParseResult(Enum):
    CommandLineOk = 0
    CommandLineError = 1
    CommandLineVersionRequested = 2
    CommandLineHelpRequested = 3

class ParseResult(object):
    def __init__(self, result, message):
        self.result = result
        self.errorMessage = message

class TedaCommandLine(object):
    def __init__(self):
        self.openFile = None
        self.openDirectory = None  # Directory to open in file explorer
        self.ignoreSettings = False
        self.resetLayout = False  # Phase 6.1
        self.resetConfig = False  # Phase 6.2
        self.installDesktop = False  # Install desktop entry (Linux only)
        self.uninstallDesktop = False  # Uninstall desktop entry (Linux only)

    def parseCommandLine(self, parser):    # QCommandLineParser

        parser.setApplicationDescription("TeDa - Telescope Data viewer for FITS astronomical images")
        parser.setSingleDashWordOptionMode(QCommandLineParser.ParseAsLongOptions)

        # Options
        model = QStringListModel(["i", "ignore-settings"])
        ignoreSettingsOption = QCommandLineOption(model.stringList(),
            "Ignore all saved settings (layout, config, last file)")
        parser.addOption(ignoreSettingsOption)

        model = QStringListModel(["reset-layout"])
        resetLayoutOption = QCommandLineOption(model.stringList(),
            "Reset window layout and dock positions to defaults")
        parser.addOption(resetLayoutOption)

        model = QStringListModel(["reset-config"])
        resetConfigOption = QCommandLineOption(model.stringList(),
            "Reset all configuration (includes layout, sliders, pins, last file)")
        parser.addOption(resetConfigOption)

        model = QStringListModel(["install-desktop"])
        installDesktopOption = QCommandLineOption(model.stringList(),
            "Install desktop entry and icon (Linux only)")
        parser.addOption(installDesktopOption)

        model = QStringListModel(["uninstall-desktop"])
        uninstallDesktopOption = QCommandLineOption(model.stringList(),
            "Uninstall desktop entry and icon (Linux only)")
        parser.addOption(uninstallDesktopOption)

        # Legacy --file option (kept for backward compatibility)
        model = QStringListModel(["f", "file"])
        openFileOption = QCommandLineOption(model.stringList(), "Open FITS file (legacy, use positional argument instead)", "file")
        parser.addOption(openFileOption)

        # Positional argument for file or directory
        parser.addPositionalArgument("path", "FITS file to open or directory to browse", "[path]")

        helpOption = parser.addHelpOption()
        versionOption = parser.addVersionOption()

        if not parser.parse(QCoreApplication.arguments()):
            return ParseResult(CommandLineParseResult.CommandLineError, parser.errorText())
        if (parser.isSet(versionOption)):
            return ParseResult(CommandLineParseResult.CommandLineVersionRequested, None)
        if (parser.isSet(helpOption)):
            return ParseResult(CommandLineParseResult.CommandLineHelpRequested, None)

        # Handle reset options (Phase 6.1, 6.2)
        if parser.isSet(resetLayoutOption):
            self.resetLayout = True

        if parser.isSet(resetConfigOption):
            self.resetConfig = True
            self.resetLayout = True  # resetConfig includes resetLayout

        # Handle path argument (positional takes precedence over --file option)
        # Can be either a file or directory
        import os
        positionalArgs = parser.positionalArguments()
        if len(positionalArgs) > 0:
            path = positionalArgs[0]
            if os.path.isdir(path):
                self.openDirectory = path
            elif os.path.isfile(path):
                self.openFile = path
            else:
                # Path doesn't exist - treat as file (will error when trying to open)
                self.openFile = path
        elif parser.isSet(openFileOption):
            file = parser.value(openFileOption)
            if file is None or len(file) == 0:
                return ParseResult(CommandLineParseResult.CommandLineError, "No file to open specified")
            self.openFile = file

        if parser.isSet(ignoreSettingsOption):
            self.ignoreSettings = True

        if parser.isSet(installDesktopOption):
            self.installDesktop = True

        if parser.isSet(uninstallDesktopOption):
            self.uninstallDesktop = True

        return ParseResult(CommandLineParseResult.CommandLineOk, None)
