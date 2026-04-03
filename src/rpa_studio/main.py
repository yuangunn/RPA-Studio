import sys
import tempfile
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from rpa_studio.gui.main_window import MainWindow

LOCK_NAME = "RPA_Studio_SingleInstance"


def is_already_running() -> bool:
    """Check if another instance is running via QLocalSocket."""
    socket = QLocalSocket()
    socket.connectToServer(LOCK_NAME)
    if socket.waitForConnected(500):
        # Another instance responded — send "show" command
        socket.write(b"show")
        socket.waitForBytesWritten(500)
        socket.disconnectFromServer()
        return True
    return False


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RPA Studio")

    # 중복 실행 방지
    if is_already_running():
        QMessageBox.information(
            None, "RPA Studio",
            "RPA Studio가 이미 실행 중입니다.\n시스템 트레이를 확인해주세요."
        )
        sys.exit(0)

    # Local server for single instance detection
    server = QLocalServer()
    # Clean up stale socket if previous crash
    QLocalServer.removeServer(LOCK_NAME)
    server.listen(LOCK_NAME)

    window = MainWindow()
    window.show()

    # When another instance tries to connect, bring window to front
    def on_new_connection():
        client = server.nextPendingConnection()
        if client:
            client.waitForReadyRead(500)
            window.show()
            window.raise_()
            window.activateWindow()
            client.disconnectFromServer()

    server.newConnection.connect(on_new_connection)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
