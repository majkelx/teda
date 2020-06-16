# from qtconsole.qt import QtGui
# from qtconsole.rich_jupyter_widget import RichJupyterWidget
# from qtconsole.inprocess import QtInProcessKernelManager


def show(**kwargs):
    # from qtconsole.qt import QtGui
    from qtconsole.rich_jupyter_widget import RichJupyterWidget
    from qtconsole.inprocess import QtInProcessKernelManager

    class Console(RichJupyterWidget):

        def __init__(self, *args, **kwargs):
            super(Console, self).__init__(*args, **kwargs)

            self.font_size = 6
            self.kernel_manager = kernel_manager = QtInProcessKernelManager()
            kernel_manager.start_kernel(show_banner=False)
            kernel_manager.kernel.gui = 'qt'
            self.kernel_client = kernel_client = self._kernel_manager.client()
            kernel_client.start_channels()

            def stop():
                kernel_client.stop_channels()
                kernel_manager.shutdown_kernel()

            self.exit_requested.connect(stop)

        def push_vars(self, variableDict):
            """
            Given a dictionary containing name / value pairs, push those variables
            to the Jupyter console widget
            """
            self.kernel_manager.kernel.shell.push(variableDict)

        def clear(self):
            """
            Clears the terminal
            """
            self._control.clear()

            # self.kernel_manager

        def print_text(self, text):
            """
            Prints some plain text to the console
            """
            self._append_plain_text(text)

        def execute_command(self, command):
            """
            Execute a command in the frame of the console widget
            """
            self._execute(command, False)

    widget = Console()
    widget.push_vars(kwargs)
    widget.print_text('The following variables from TeDa FITS Viewer are available:')
    widget.print_text(' '.join(kwargs.keys()))
    widget.show()
