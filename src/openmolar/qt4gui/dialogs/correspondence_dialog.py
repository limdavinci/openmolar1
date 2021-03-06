#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

import logging
import re

from PyQt4 import QtGui, QtCore

from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.dbtools import standard_letter

LOGGER = logging.getLogger("openmolar")


class CorrespondenceDialog(BaseDialog):
    LETTERS = None

    def __init__(self, html, patient=None, preformatted=True, parent=None):
        BaseDialog.__init__(self, parent, remove_stretch=True)

        self.pt = patient
        self.text_edit = QtGui.QTextEdit()
        self.orig_html = html
        self.text_edit.setHtml(html)
        self.orig_qhtml = self.text
        self.insertWidget(self.text_edit)

        if preformatted:
            self.combo_box = QtGui.QComboBox()
            self.combo_box.addItem(_("Blank Letter"))
            QtCore.QTimer.singleShot(100, self.load_preformats)
            self.insertWidget(self.combo_box)

        self.enableApply()

    def advise(self, message):
        QtGui.QMessageBox.information(self, _("message"), message)

    def sizeHint(self):
        return QtCore.QSize(600, 600)

    def showEvent(self, event):
        self.text_edit.setFocus()

    def replace_placeholders(self, text):
        try:
            text = text.replace("{{NAME}}", self.pt.name)
            text = text.replace("{{SERIALNO}}", str(self.pt.serialno))
        except AttributeError:
            LOGGER.warning("couldn't replace placeholders")
            pass
        return text

    def load_preformats(self):
        if self.LETTERS is None:
            blank_letter = standard_letter.StandardLetter(
                _("Blank Letter"),
                "<br />" * 9,
                "")

            LOGGER.info("loading preformatted letters")
            CorrespondenceDialog.LETTERS = {
                blank_letter.description: blank_letter}

            for letter in standard_letter.get_standard_letters():
                CorrespondenceDialog.LETTERS[letter.description] = letter

        for key, letter in self.LETTERS.iteritems():
            if key != _("Blank Letter"):
                self.combo_box.addItem(letter.description)
        self.combo_box.currentIndexChanged.connect(
            self.preformed_letter_selected)

    def preformed_letter_selected(self, i):
        LOGGER.debug("selecting preformed letter %s", i)
        selected = unicode(self.combo_box.currentText())
        if self.has_edits and QtGui.QMessageBox.question(
                self,
                _("Confirm"),
                "%s %s" % (
                    _("Abandon changes and convert to letter type"),
                    selected),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        ) == QtGui.QMessageBox.No:
                return

        letter = self.LETTERS[selected]
        new_body = "<!-- letter body -->\n%s\n<!-- end of letter body -->" % \
            letter.text
        new_footer = "<!-- footer -->\n%s\n<!-- end of footer -->" % \
            letter.footer

        compiled = re.compile(
            r"<!-- letter body -->(.*)<!-- end of letter body -->", re.DOTALL)
        new_text = re.sub(compiled, new_body, self.orig_html)

        compiled = re.compile(
            r"<!-- footer -->(.*)<!-- end of footer -->", re.DOTALL)
        new_text = re.sub(compiled, new_footer, new_text)

        new_text = self.replace_placeholders(new_text)

        self.text_edit.setHtml(new_text)
        self.orig_qhtml = self.text

    @property
    def has_edits(self):
        return self.text != self.orig_qhtml

    @property
    def text(self):
        return unicode(self.text_edit.toHtml())

    @property
    def letter_description(self):
        return unicode(self.combo_box.currentText())

if __name__ == "__main__":
    app = QtGui.QApplication([])
    LOGGER.setLevel(logging.DEBUG)
    dl = CorrespondenceDialog(standard_letter._test())
    dl.exec_()
