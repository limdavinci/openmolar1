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

'''
This module provides a function 'run' which will move data
to schema 2_4
'''
from __future__ import division

import logging
import os
import sys

from openmolar.settings import localsettings
from openmolar.schema_upgrades.database_updater_thread import DatabaseUpdaterThread

LOGGER = logging.getLogger("openmolar")

SQLSTRINGS = [
    'drop table if exists daybook_link',

    '''
create table daybook_link (
  ix         int(11) unsigned not null auto_increment ,
  daybook_id     int(11),
  tx_hash    char(40) NOT NULL,
PRIMARY KEY (ix),
INDEX (daybook_id)
)''',

    'create index daybook_id_index on daybook_link(tx_hash)',
]

CLEANUPSTRINGS = [
    'drop table if exists est_link',  # obsolete since schema 2.2
    'alter table est_link2 drop column daybook_id'
]


class DatabaseUpdater(DatabaseUpdaterThread):

    def run(self):
        LOGGER.info("running script to convert from schema 2.3 to 2.4")
        try:
            self.connect()
            #- execute the SQL commands
            self.progressSig(50, _("creating est_link2 table"))
            self.execute_statements(SQLSTRINGS)

            self.progressSig(95, _("executing cleanup statements"))
            self.execute_statements(CLEANUPSTRINGS)

            self.progressSig(97, _('updating settings'))
            LOGGER.info("updating stored database version in settings table")

            self.update_schema_version(("2.4",), "2_3 to 2_4 script")

            self.progressSig(100, _("updating stored schema version"))
            self.commit()
            self.completeSig(_("Successfully moved db to")+ " 2.4")
            return True
        except Exception as exc:
            LOGGER.exception("error transfering data")
            self.rollback()
            raise self.UpdateError(exc)

if __name__ == "__main__":
    dbu = DatabaseUpdater()
    if dbu.run():
        LOGGER.info("ALL DONE, conversion successful")
    else:
        LOGGER.warning("conversion failed")
