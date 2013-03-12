#!/usr/bin/python
#
# Copyright (C) 2009 Martin Owens
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
Test crontab enumerations.
"""

import os
import sys

sys.path.insert(0, '../')

import unittest
from crontab import CronTab
try:
    from test import test_support
except ImportError:
    from test import support as test_support

INITAL_TAB = """
* * * JAN     SAT          enums
* * * APR-MAR *            ranges
* * * *       MON,FRI,WED  multiples
* * * *       *            com1 # Comment One
* * * *       *            com2 # Comment One
"""

COMMANDS = [
    'enums',
    'ranges',
    'multiples',
    'com1', 'com2',
]

RESULT_TAB = """
* * * JAN SAT enums
* * * MAR-APR * ranges
* * * * MON,WED,FRI multiples
* * * * * com1 # Comment One
* * * * * com2 # Comment One
"""

class BasicTestCase(unittest.TestCase):
    """Test basic functionality of crontab."""
    def setUp(self):
        self.crontab = CronTab(tab=INITAL_TAB)

    def test_01_presevation(self):
        """All Entries Re-Rendered Correctly"""
        self.crontab.write()
        results = RESULT_TAB.split('\n')
        line_no = 0
        for line in self.crontab.intab.split('\n'):
            self.assertEqual(line, results[line_no])
            line_no += 1

    def test_02_simple_enum(self):
        """Simple Enumerations"""
        e = self.crontab.find_command('enums')[0]
        self.assertEqual(e.month, 'JAN')
        self.assertEqual(e.month.render(True), '1')
        self.assertEqual(e.dow, 'SAT')
        self.assertEqual(e.dow.render(True), '6')

    def test_03_enum_range(self):
        """Enumeration Ranges"""
        e = self.crontab.find_command('ranges')[0]
        self.assertEqual(e.month, 'MAR-APR')
        self.assertEqual(e.month.render(True), '3-4' )
 
    def test_04_sets(self):
        """Enumeration Sets"""
        e = self.crontab.find_command('multiples')[0]
        self.assertEqual(e.dow, 'MON,WED,FRI')
        self.assertEqual(e.dow.render(True), '1,3,5' )

    def test_05_create(self):
        """Create by Enumeration"""
        job = self.crontab.new(command='new')
        job.month.on('JAN')
        job.dow.on('SUN')
        self.assertEqual(job, '* * * JAN SUN new')

    def test_06_create_range(self):
        """Created Enum Range"""
        job = self.crontab.new(command='new2')
        job.month.during('APR', 'NOV').every(2)
        self.assertEqual(job, '* * * APR-NOV/2 * new2')

    def test_07_create_set(self):
        """Created Enum Set"""
        job = self.crontab.new(command='new3')
        job.month.on('APR')
        job.month.on('NOV','JAN')
        self.assertEqual(job, '* * * JAN,APR,NOV * new3')

    def test_08_find_comment(self):
        """Comment Set"""
        jobs = self.crontab.find_comment('Comment One')
        self.assertEqual(len(jobs), 2)
        for job in jobs:
            self.assertEqual(job.meta(), 'Comment One')

if __name__ == '__main__':
    test_support.run_unittest(
       BasicTestCase,
    )
