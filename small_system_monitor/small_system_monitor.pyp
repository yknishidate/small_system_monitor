"""
Small System Monitor in C4D

Copyright (c) 2020 Nishiki

Released under the MIT license
https://opensource.org/licenses/mit-license.php
"""

import c4d
import os
import psutil

PLUGIN_ID = 1054769

CPU_COLOR = c4d.Vector(0.3, 0.64, 1)
MEMORY_COLOR = c4d.Vector(1, 0.9, 0.3)
C4D_MEMORY_COLOR = c4d.Vector(1, 0.64, 0.3)
BACKGROUND_COLOR = c4d.Vector(50/255.0)

BAR_HEIGHT = 3
INTERVAL_TIME_MS = 1000

class CPUArea(c4d.gui.GeUserArea):
    def Init(self):
        self.Update()
        return

    def DrawMsg(self, x1, y1, x2, y2, msg_ref):
        # ダブルバッファリングを有効にする
        self.OffScreenOn()
        # クリッピング設定
        self.SetClippingRegion(x1, y1, x2, y2)

        # 背景描画
        self.DrawSetPen(BACKGROUND_COLOR)
        self.DrawRectangle(x1, y1, x2, y2)

        # CPU使用状況からxを計算
        cpu = psutil.cpu_percent(0.1)
        x = (x2 - x1) * (cpu / 100.0)

        # 四角描画
        self.DrawSetPen(CPU_COLOR)
        self.DrawRectangle(x1, y1, x, y2)
        return

    def Update(self):
        self.Redraw()
        return

class MemoryArea(c4d.gui.GeUserArea):
    def Init(self):
        self.Update()
        return

    def DrawMsg(self, x1, y1, x2, y2, msg_ref):
        # ダブルバッファリングを有効にする
        self.OffScreenOn()
        # クリッピング設定
        self.SetClippingRegion(x1, y1, x2, y2)

        # 背景描画
        self.DrawSetPen(BACKGROUND_COLOR)
        self.DrawRectangle(x1, y1, x2, y2)

        # PC全体のメモリ使用状況からxを計算
        memory = psutil.virtual_memory() 
        x = (x2 - x1) * (float(memory.used) / memory.total)

        # 四角描画
        self.DrawSetPen(MEMORY_COLOR)
        self.DrawRectangle(x1, y1, x, y2)

        # C4Dのメモリ使用状況からxを計算
        c4d_memory = c4d.storage.GeGetMemoryStat()
        x = (x2 - x1) * (float(c4d_memory[c4d.C4D_MEMORY_STAT_MEMORY_INUSE]) / memory.total)

        # 四角描画
        self.DrawSetPen(C4D_MEMORY_COLOR)
        self.DrawRectangle(x1, y1, x, y2)

        return

    def Update(self):
        self.Redraw()
        return

class SystemMonitor(c4d.gui.GeDialog):
    def __init__(self):
        self.cpu_info = CPUArea()
        self.mem_info = MemoryArea()

        # Disables Menu Bar
        self.AddGadget(c4d.DIALOG_NOMENUBAR, 0)

    def CreateLayout(self):
        self.SetTitle("Small System Monitor")

        if self.GroupBegin(id=0, flags=c4d.BFH_SCALEFIT, rows=1, title="", cols=1, groupflags=c4d.BORDER_GROUP_IN):
            self.AddGadget(c4d.DIALOG_PIN, 0)
        self.GroupEnd()

        # CPU
        if self.GroupBegin(id=1, flags=c4d.BFH_SCALEFIT, rows=1, title="", cols=2, groupflags=c4d.BORDER_GROUP_IN):
            self.GroupBorderSpace(5, 0, 5, 0)

            self.cpu_text = self.AddStaticText(id=3, initw=80, inith=0, name="CPU", borderstyle=0, flags=c4d.BFH_LEFT)

            cpu_area = self.AddUserArea(id=1001, flags=c4d.BFH_SCALEFIT, inith=BAR_HEIGHT)
            self.AttachUserArea(self.cpu_info, cpu_area)
        self.GroupEnd()

        # Memory
        if self.GroupBegin(id=2, flags=c4d.BFH_SCALEFIT, rows=1, title="", cols=2, groupflags=c4d.BORDER_GROUP_IN):
            self.GroupBorderSpace(5, 0, 5, 0)

            self.mem_text = self.AddStaticText(id=2, initw=80, inith=0, name="Memory", borderstyle=0, flags=c4d.BFH_LEFT)

            memory_area = self.AddUserArea(id=1002, flags=c4d.BFH_SCALEFIT, inith=BAR_HEIGHT)
            self.AttachUserArea(self.mem_info, memory_area)
        self.GroupEnd()

        return True

    def InitValues(self):
        # C4Dが呼び出す間隔を設定する
        self.SetTimer(INTERVAL_TIME_MS)
        return True

    def Timer(self, msg):
        self.cpu_info.Update()
        self.mem_info.Update()


class SystemMonitorCommandData(c4d.plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = SystemMonitor()

        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaulth=400, defaultw=400)

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = SystemMonitor()

        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)


if __name__ == "__main__":
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "small_system_monitor.tif")

    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                      str="SmallSystemMonitor",
                                      help="Show the current memory and cpu usage.",
                                      info=0,
                                      dat=SystemMonitorCommandData(),
                                      icon=bmp)
