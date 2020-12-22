# !/usr/bin/python
# -*- coding: UTF-8 -*-
'Copyright 2020 Mota Lee'
''' This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.'''

# MindTank global variable;
MT_VER='0.0.1'
MT_UPDATE=20201120
PY_VER_MIN='3.8.0'
PY_VER_MAX='3.8.7'
PY_RELIABILITIES=['numpy','interval','pillow','paramiko',
    'python-nmap','opencv-python','wxpython','v4l2']
if __name__ == "__main__":
    import sys,os
    sys.path.append(os.getcwd())
    import core as c

    if 'MCT'in sys.argv:
        from app import MCT
        mct=MCT.MCT()
        mct.terminalMain()
    elif 'MCTX' in sys.argv:
        from app import MCT
        wxmw=MCT.MCTX()
        MCT.WXAPP.MainLoop()
    elif 'MET' in sys.argv:
        from app import MET
        met=MET.MET()
        met.METMain()
