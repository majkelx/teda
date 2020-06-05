from enum import Enum

from PySide2.QtCore import QCommandLineParser, QCommandLineOption, QStringListModel, QCoreApplication
from PySide2.QtWidgets import QApplication


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
        self.ignoreSettings = False

    def parseCommandLine(self, parser):    # QCommandLineParser

        parser.setApplicationDescription(QApplication.applicationName())
        parser.setSingleDashWordOptionMode(QCommandLineParser.ParseAsLongOptions)

        model = QStringListModel(["i", "ignore-settings"])
        ignoreSettingsOption = QCommandLineOption (model.stringList(), "Ingnore settings file")
        parser.addOption(ignoreSettingsOption)

        model = QStringListModel(["f", "file"])
        openFileOption = QCommandLineOption(model.stringList(), "Open file", "file")
        parser.addOption(openFileOption)

        helpOption = parser.addHelpOption()
        versionOption = parser.addVersionOption()

        if not parser.parse(QCoreApplication.arguments()):
            return ParseResult(CommandLineParseResult.CommandLineError, parser.errorText())
        if (parser.isSet(versionOption)):
            return ParseResult(CommandLineParseResult.CommandLineVersionRequested, None)
        if (parser.isSet(helpOption)):
            return ParseResult(CommandLineParseResult.CommandLineHelpRequested, None)

        if (parser.isSet(openFileOption)):
            file = parser.value(openFileOption)
            if file is None or len(file) == 0 :
                return ParseResult(CommandLineParseResult.CommandLineError, "No file to open spefified ")
            self.openFile = file

        if parser.isSet(ignoreSettingsOption):
            self.ignoreSettings = True

        return ParseResult(CommandLineParseResult.CommandLineOk, None)
