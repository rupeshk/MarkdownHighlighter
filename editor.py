#!/usr/bin/python
# -*- coding: utf-8 -*-

# MarkdownHighlighter test application. Adapted from ReText.
# Copyright 2011 Dmitry Shachnev, 2012 Rupesh Kumar

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import sys
import os
import subprocess
import json
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from markdownhighlighter import MarkdownHighlighter

'''
Test editor for MarkdownSyntaxHighlighter
'''

app_name = "MarkdownHighlighter"
app_version = "0.1.0"
icon_path = "icons/"

monofont = QFont()
monofont.setFamily('monospace')

class MarkdownWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.resize(800, 600)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        self.setWindowTitle(self.tr('New document') + '[*] ')
        self.setWindowIcon(QIcon.fromTheme('accessories-text-editor'))

        self.tedit = QTextEdit(self)
        self.tedit.setFont(monofont)
        self.setCentralWidget(self.tedit)

        self.fileName = None
        self.highlighter = MarkdownHighlighter(self.tedit)

        self.toolBar = QToolBar(self.tr('File toolbar'), self)
        self.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.editBar = QToolBar(self.tr('Edit toolbar'), self)
        self.addToolBar(Qt.TopToolBarArea, self.editBar)

        self.actionNew = QAction(self.actIcon('document-new'), self.tr('New'), self)
        self.actionNew.setShortcut(QKeySequence.New)
        self.actionNew.setPriority(QAction.LowPriority)
        self.connect(self.actionNew, SIGNAL('triggered()'), self.createNew)

        self.actionOpen = QAction(self.actIcon('document-open'), self.tr('Open'), self)
        self.actionOpen.setShortcut(QKeySequence.Open)
        self.actionOpen.setPriority(QAction.LowPriority)
        self.connect(self.actionOpen, SIGNAL('triggered()'), self.openFile)

        self.actionSave = QAction(self.actIcon('document-save'), self.tr('Save'), self)
        self.actionSave.setEnabled(False)
        self.actionSave.setShortcut(QKeySequence.Save)
        self.actionSave.setPriority(QAction.LowPriority)
        self.connect(self.actionSave, SIGNAL('triggered()'), self.saveFile)

        self.actionSaveAs = QAction(self.actIcon('document-save-as'), self.tr('Save as'), self)
        self.actionSaveAs.setShortcut(QKeySequence.SaveAs)
        self.connect(self.actionSaveAs, SIGNAL('triggered()'), self.saveFileAs)

        self.actionQuit = QAction(self.actIcon('application-exit'), self.tr('Quit'), self)
        self.actionQuit.setShortcut(QKeySequence.Quit)
        self.actionQuit.setMenuRole(QAction.QuitRole)
        self.connect(self.actionQuit, SIGNAL('triggered()'), qApp, SLOT('quit()'))

        self.actionUndo = QAction(self.actIcon('edit-undo'), self.tr('Undo'), self)
        self.actionUndo.setShortcut(QKeySequence.Undo)
        self.actionUndo.setEnabled(False)

        self.actionRedo = QAction(self.actIcon('edit-redo'), self.tr('Redo'), self)
        self.actionRedo.setShortcut(QKeySequence.Redo)
        self.actionRedo.setEnabled(False)

        self.actionCopy = QAction(self.actIcon('edit-copy'), self.tr('Copy'), self)
        self.actionCopy.setShortcut(QKeySequence.Copy)
        self.actionCopy.setEnabled(False)

        self.actionCut = QAction(self.actIcon('edit-cut'), self.tr('Cut'), self)
        self.actionCut.setShortcut(QKeySequence.Cut)
        self.actionCut.setEnabled(False)

        self.actionPaste = QAction(self.actIcon('edit-paste'), self.tr('Paste'), self)
        self.actionPaste.setShortcut(QKeySequence.Paste)

        self.connect(self.actionUndo, SIGNAL('triggered()'), \
        lambda: self.tedit.undo())
        self.connect(self.actionRedo, SIGNAL('triggered()'), \
        lambda: self.tedit.redo())
        self.connect(self.actionCut, SIGNAL('triggered()'), \
        lambda: self.tedit.cut())
        self.connect(self.actionCopy, SIGNAL('triggered()'), \
        lambda: self.tedit.copy())
        self.connect(self.actionPaste, SIGNAL('triggered()'), \
        lambda: self.tedit.paste())

        self.connect(self.tedit, SIGNAL('undoAvailable(bool)'), self.actionUndo, SLOT('setEnabled(bool)'))
        self.connect(self.tedit, SIGNAL('redoAvailable(bool)'), self.actionRedo, SLOT('setEnabled(bool)'))
        self.connect(self.tedit, SIGNAL('copyAvailable(bool)'), self.enableCopy)
        self.connect(self.tedit.document(), SIGNAL('modificationChanged(bool)'), self.modificationChanged)
        self.connect(qApp.clipboard(), SIGNAL('dataChanged()'), self.clipboardDataChanged)
        self.clipboardDataChanged()

        self.actionAbout = QAction(self.actIcon('help-about'), self.tr('About %1').arg(app_name), self)
        self.actionAbout.setMenuRole(QAction.AboutRole)
        self.connect(self.actionAbout, SIGNAL('triggered()'), self.aboutDialog)

        self.actionAboutQt = QAction(self.tr('About Qt'), self)
        self.actionAboutQt.setMenuRole(QAction.AboutQtRole)
        self.connect(self.actionAboutQt, SIGNAL('triggered()'), qApp, SLOT('aboutQt()'))

        self.themeBox = QComboBox(self.editBar)
        themestr = open('theme.json','r').read()
        self.themes = json.loads(themestr)
        self.themes["default"] = self.highlighter.defaultTheme
        self.themeBox.addItems(self.themes.keys())
        self.connect(self.themeBox, SIGNAL('currentIndexChanged(QString)'), self.changeTheme)

        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 800, 25))
        self.setMenuBar(self.menubar)

        self.menuFile = self.menubar.addMenu(self.tr('File'))
        self.menuEdit = self.menubar.addMenu(self.tr('Edit'))
        self.menuHelp = self.menubar.addMenu(self.tr('Help'))

        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()

        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addSeparator()

        self.menuFile.addAction(self.actionQuit)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()

        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addSeparator()

        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAboutQt)

        self.menubar.addMenu(self.menuFile)
        self.menubar.addMenu(self.menuEdit)
        self.menubar.addMenu(self.menuHelp)

        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolBar.addAction(self.actionNew)

        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addSeparator()

        self.editBar.addAction(self.actionUndo)
        self.editBar.addAction(self.actionRedo)
        self.editBar.addSeparator()

        self.editBar.addAction(self.actionCut)
        self.editBar.addAction(self.actionCopy)
        self.editBar.addAction(self.actionPaste)
        self.editBar.addSeparator()

        self.editBar.addWidget(QLabel(self.tr('Select theme ')))
        self.editBar.addWidget(self.themeBox)

    def actIcon(self, name):
        return QIcon.fromTheme(name, QIcon(icon_path+name+'.png'))

    def enableCopy(self, copymode):
        self.actionCopy.setEnabled(copymode)
        self.actionCut.setEnabled(copymode)

    def enableFullScreen(self, yes):
        if yes:
            self.showFullScreen()
        else:
            self.showNormal()

    def keyPressEvent(self, e):
        v = not self.menubar.isVisible()
        if e.key() == Qt.Key_F12 and e.modifiers() & Qt.ShiftModifier:
            self.menubar.setVisible(v)
            self.toolBar.setVisible(v)
            self.editBar.setVisible(v)
        elif e.key() == Qt.Key_F11:
            if v:
                n = not self.actionFullScreen.isChecked()
                self.actionFullScreen.setChecked(n)
                self.enableFullScreen(n)

    def setCurrentFile(self):
        self.setWindowTitle(self.getDocumentTitle(baseName=True))
        self.setWindowFilePath(self.fileName)
        QDir.setCurrent(QFileInfo(self.fileName).dir().path())

    def createNew(self):
        if self.maybeSave():
            self.setWindowTitle(self.tr('New document') + '[*] ')
            self.tedit.clear()

    def openFile(self):
        fileName = QFileDialog.getOpenFileName(self, self.tr("Select one or several files to open"), "", \
        self.tr("Supported files")+" (*.re *.md *.markdown *.mdown *.mkd *.mkdn *.rst *.rest *.txt *.html *.htm);;"+self.tr("All files (*)"))
        self.openFileWrapper(fileName)

    def openFileWrapper(self, fileName):
        if fileName:
            if self.fileName != fileName:
                self.fileName = fileName
                self.openFileMain()

    def openFileMain(self):
        if QFile.exists(self.fileName):
            openfile = QFile(self.fileName)
            openfile.open(QIODevice.ReadOnly)
            html = QTextStream(openfile).readAll()
            openfile.close()
            self.tedit.setPlainText(html)
            suffix = QFileInfo(self.fileName).suffix()
            self.setCurrentFile()
            self.setWindowModified(False)

    def saveFile(self):
        self.saveFileMain(dlg=False)

    def saveFileAs(self):
        self.saveFileMain(dlg=True)

    def saveFileMain(self, dlg):
        if (not self.fileName) or dlg:
            defaultExt = self.tr("Markdown files")+" (*.re *.md *.markdown *.mdown *.mkd *.mkdn *.txt)"
            ext = ".mkd"
            if QSettings().contains('defaultExt'):
                ext = QSettings().value('defaultExt').toString()
            self.fileName = QFileDialog.getSaveFileName(self, self.tr("Save file"), "", defaultExt)
            if self.fileName and QFileInfo(self.fileName).suffix().isEmpty():
                self.fileName.append(ext)
        if self.fileName:
            self.setCurrentFile()
        if QFileInfo(self.fileName).isWritable() or not QFile.exists(self.fileName):
            if self.fileName:
                self.saveFileWrapper(self.fileName)
                self.tedit.document().setModified(False)
                self.setWindowModified(False)
        else:
            self.setWindowModified(self.isWindowModified())
            QMessageBox.warning(self, app_name, self.tr("Cannot save to file since it is read-only!"))

    def saveFileWrapper(self, fn):
        savefile = QFile(fn)
        savefile.open(QIODevice.WriteOnly)
        savestream = QTextStream(savefile)
        savestream << self.tedit.toPlainText()
        savefile.close()

    def getDocumentTitle(self, baseName=False):
        if self.fileName:
            return QFileInfo(self.fileName).completeBaseName()
        else:
            return self.tr("New document")

    def autoSaveActive(self):
        return self.fileName and QFileInfo(self.fileName).isWritable()

    def modificationChanged(self, changed):
        if self.autoSaveActive():
            changed = False
        self.actionSave.setEnabled(changed)
        self.setWindowModified(changed)

    def clipboardDataChanged(self):
        self.actionPaste.setEnabled(qApp.clipboard().mimeData().hasText())

    def changeTheme(self, theme):
        themen = str(theme)
        self.highlighter.setTheme(self.themes[themen])

    def maybeSave(self):
        if self.autoSaveActive():
            self.saveFileWrapper(self.fileName)
            return True
        if not self.tedit.document().isModified():
            return True
        ret = QMessageBox.warning(self, app_name, self.tr("The document has been modified.\nDo you want to save your changes?"), \
        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if ret == QMessageBox.Save:
            self.saveFileMain(False)
            return True
        elif ret == QMessageBox.Cancel:
            return False
        return True

    def closeEvent(self, closeevent):
        accept = True
        if not self.maybeSave():
            accept = False
        if accept:
            closeevent.accept()
        else:
            closeevent.ignore()

    def aboutDialog(self):
        QMessageBox.about(self, self.tr('About %1').arg(app_name), \
        '<p><b>'+app_name+' '+app_version+'</b><br>'+self.tr('Example editor for MarkdownHighlighter') \
        +'</p><p>'+self.tr('Author: Dmitry Shachnev, 2011; Rupesh Kumar, 2012') \
        +'<br><a href="http://daringfireball.net/projects/markdown/syntax">' + self.tr('Markdown syntax') + '</a> ')

def main(fileNames):
    app = QApplication(sys.argv)
    app.setOrganizationName("MarkdownHighlighter")
    app.setApplicationName("MarkdownHighlighter")
    window = MarkdownWindow()
    for fileName in fileNames:
        if QFile.exists(QString.fromUtf8(fileName)):
            window.openFileWrapper(QString.fromUtf8(fileName))
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        main("")
