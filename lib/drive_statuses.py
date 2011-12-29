#    Copyright 2011  Marcin Szewczyk <Marcin.Szewczyk@wodny.org>
#
#    This file is part of pendrive-frenzy.
#
#    Pendrive-frenzy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Pendrive-frenzy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pendrive-frenzy.  If not, see <http://www.gnu.org/licenses/>.



class DriveStatus:
    DRIVE_NEW = 0x00
    DRIVE_HASPT = 0x01
    DRIVE_INPROGRESS = 0x02
    DRIVE_DONE = 0x03
    DRIVE_PARTERROR = 0x84

    DRIVE_WAITFORPT = 0x45
    DRIVE_PTERROR = 0xC7

    DRIVE_ERROR = 0x80
    DRIVE_PT = 0x40
