import sys
import time
import random
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QTimer, Qt
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from hero import Hero
from data import data_scene
from data import data_levelup
from data import data_tips
from data import data_item
from common_func import *

class TimerType:
    EXP = 0
    DROP = 1

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        self.ui = loader.load("src/gg.ui", self)
        self.hero = Hero()
        self.initUI()
        self.updateLevelInfo()
        self.updateScene()
        self.updateBagItem()
        self.updateBaseInfo()
        self.updateEquip()

    def initUI(self):
        # 等级
        self._initLevelInfo()
        # 定时
        self._initTimer()
        # 顶部Tips
        self._initTopTips()
        # 系统消息
        self._initSystemInfo()
        # 场景
        self._initSceneBtns()
        # 背包
        self._initBagItemBtns()
        # 物品Tips
        self._initItemTips()
        # 装备Tips
        self._initEquipTips()
        # 人物基础信息
        self._initBaseInfo()
        # 装备
        self._initEquip()

    # 等级部分
    def updateLevelInfo(self):
        lv = self.hero.get_level()
        exp = self.hero.get_exp()
        self.ui.level_text.setText( str(lv) )
        self.ui.exp_text.setText( str(exp) )
        self.ui.needexp_text.setText( str( data_levelup.data[ lv + 1 ] ) )
        self.ui.levelup_Btn.setEnabled( exp >= data_levelup.data[ lv + 1 ] )
    
    def _initLevelInfo(self):
        self.ui.levelup_Btn.clicked.connect(self.on_levelup_Btn_Clicked)
    
    def on_levelup_Btn_Clicked(self):
        self.hero.levelup()
        self.addSystemInfo( data_tips.data["LEVEL_UP"] % self.hero.get_level() )
        self.updateLevelInfo()
        self.updateScene()
        self.updateBaseInfo()
    
    # 定时部分
    def _initTimer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.updateTimer)
        self.timer.start()
        self.timerLastTime = {
            TimerType.EXP : 0,
            TimerType.DROP : 0,
        }

    def updateTimer(self):
        t = int(time.time() * 1000)
        # 经验增长
        if t - self.timerLastTime[TimerType.EXP] > 1000:
            self.timerLastTime[TimerType.EXP] = t
            exp = self.hero.drop_exp()
            self.addTopTips( data_tips.data["GET_EXP"] % exp )
            self.updateLevelInfo()
        
        # 掉落
        if t - self.timerLastTime[TimerType.DROP] > 5000:
            self.timerLastTime[TimerType.DROP] = t
            itemId, _, sysInfo = self.hero.drop_item()
            if itemId is not None:
                self.addSystemInfo( sysInfo )
                self.updateBagItem(None)

    # 顶部Tips
    def _initTopTips(self):
        self.ui.top_tips.setText("")
        self.toptops_oripos = self.ui.top_tips.pos()
    
    def addTopTips(self, text):
        # 设置文字内容和样式（移除透明度控制，保持完全显示）
        self.ui.top_tips.setText(text)
        # 动画起始位置：在原始位置下方50像素（从下方弹起）
        start_pos = QPoint(self.toptops_oripos.x(), self.toptops_oripos.y() + 50)
        self.ui.top_tips.move(start_pos)  # 先移动到起始位置
        
        # 创建位置动画（控制y轴位置变化）
        self.toptipsAni = QPropertyAnimation(self.ui.top_tips, b"pos")
        self.toptipsAni.setDuration(1000)  # 动画持续1秒（足够展示弹跳效果）
        
        # 设置关键帧：模拟简谐振动（弹跳效果）
        # 关键帧时间点：0%（开始）→ 60%（第一次到达目标）→ 80%（轻微回弹）→ 100%（稳定）
        self.toptipsAni.setKeyValues([
            (0.0, start_pos),  # 起始位置（下方）
            (0.6, self.toptops_oripos),  # 第一次弹到目标位置
            (0.8, QPoint(self.toptops_oripos.x(), self.toptops_oripos.y() - 10)),  # 轻微向上回弹
            (1.0, self.toptops_oripos)   # 最终稳定在目标位置
        ])
        
        # 使用弹跳曲线增强简谐振动效果（模拟弹簧阻尼）
        self.toptipsAni.setEasingCurve(QEasingCurve.OutBounce)
        
        # 启动动画（先停止可能存在的旧动画）
        if hasattr(self, 'toptipsAni') and self.toptipsAni.state() == QPropertyAnimation.Running:
            self.toptipsAni.stop()
        self.toptipsAni.start()
    
    # 系统消息部分
    def _initSystemInfo(self):
        self.ui.system_TextEdit.setText("")
        self.ui.system_TextEdit.setReadOnly(True)
    
    def addSystemInfo(self, text):
        self.hero.add_sysInfo(text)
        self.ui.system_TextEdit.setText( '\n'.join(self.hero.get_sysInfo()) )
        scroll_bar = self.ui.system_TextEdit.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    # 场景部分
    def updateScene(self, visible=False):
        lv = self.hero.get_level()
        for i, btn in enumerate(self.sceneBtns):
            scene_d = data_scene.data.get(i, None)
            if scene_d and lv >= scene_d["unlock_level"]:
                btn.setText(scene_d["name"])
                btn.setEnabled(True)
            else:
                btn.setText("%d级解锁" % scene_d["unlock_level"])
                btn.setEnabled(False)
        self.ui.curScene_Text.setText( data_scene.data.get(self.hero.get_scene())["name"] )
        self.ui.sceneChange_Group.setVisible(visible)

    def _initSceneBtns(self):
        self.sceneBtns = []
        idx = 0
        while True:
            btn = getattr(self.ui, "sceneButton_%d"% idx, None)
            if btn is None:
                break
            btn.clicked.connect( lambda checked, num=idx:self.on_sceneBtn_Clicked(num) )
            self.sceneBtns.append(btn)
            idx += 1
        self.ui.sceneChange_Btn.clicked.connect(self.on_sceneChange_Btn_Clicked)

    def on_sceneChange_Btn_Clicked(self):
        self.ui.sceneChange_Group.setVisible( not self.ui.sceneChange_Group.isVisible())

    def on_sceneBtn_Clicked(self, idx):
        if self.hero.get_scene() != idx:
            self.hero.set_scene( idx )
            self.addSystemInfo( 
                data_tips.data.get("CHANGE_SCENE") % (data_scene.data.get(idx)["name"], data_scene.data.get(idx)["exp_multiple"]) )
        self.updateScene()

    # 背包部分
    def updateBagItem(self, visible=False):
        itemsCount = len(self.hero.get_bagItems())
        for i, btn in enumerate(self.bagItemBtns):
            v = i < itemsCount
            btn.setEnabled(v)
            if v:
                self.updateBagItemBtn(btn, self.hero.get_bagItems()[i])
            else:
                btn.setText("")
        if visible is not None:
            self.ui.bag_Group.setVisible(visible)
        self.ui.itemTips_Group.setVisible(False)
        self.ui.equipTips_Group.setVisible(False)
    
    def updateBagItemBtn(self, btn, item):
        name = data_item.data[ item["id"] ][ "name" ]
        if data_item.data[ item["id"] ]["max_count"] > 1:
            if item["cnt"] != 1:
                name += "(%d)" % item["cnt"]
        if item.get("equip", None) is not None:
            if item["equip"] == True:
                name += "(装)"
        btn.setText(name)

    def _initBagItemBtns(self):
        self.bagItemBtns = []
        idx = 0
        while True:
            btn = getattr(self.ui, "itemButton_%02d"% idx, None)
            if btn is None:
                break
            btn.clicked.connect( lambda checked, num=idx:self.on_bagItemBtn_Clicked(num) )
            self.bagItemBtns.append(btn)
            idx += 1
        self.ui.bagChange_Btn.clicked.connect(self.on_bagChange_Btn_Clicked)

    def on_bagChange_Btn_Clicked(self):
        self.ui.bag_Group.setVisible( not self.ui.bag_Group.isVisible() )
        self.ui.equipTips_Group.setVisible( False )
        self.ui.itemTips_Group.setVisible( False )
    
    # 物品 Tips 部分
    def on_bagItemBtn_Clicked(self, idx):
        items = self.hero.get_bagItems()
        if idx >= len(items):
            return
        self.updateTips(idx, items[idx])
    
    def updateTips(self, idx, item):
        iseq = isEquip(item["id"])
        item_d = data_item.data[ item["id"] ]
        self.ui.equipTips_Group.setVisible( iseq  )
        self.ui.itemTips_Group.setVisible(  not iseq )
        if iseq:
            self.ui.equipName_lb.setText( item_d["name"] )
            self.ui.equipPart_lb.setText( getEquipPartName( item_d["item_subtype"] ) )
            self.ui.xing_lb.setText( "☆" * (item_d["use_level"]//25+1) )
            self.ui.equipDesc_Text.setText( item_d["desc"] )
            self.ui.dw_lb.setText("")  # 预留
            itemprops = list(item_d["property_add"].items())
            for i, props in enumerate(self.equipTipsProps):
                if i < len(itemprops):
                    props.setVisible(True)
                    props.setText( "%s + %d" % (getPropertyName(itemprops[i][0]), itemprops[i][1]) )
                else:
                    props.setVisible(False)
            self.ui.itemEquipLevel_Text.setText( data_tips.data["ITEM_EQUIP_LEVEL"] % item_d["use_level"] )
            self.ui.equipUse_Btn.setText( "卸下" if item["equip"] else "装备" )
            self.ui.equipUse_Btn.clicked.disconnect()
            self.ui.equipUse_Btn.clicked.connect( lambda checked, num=idx:self.on_bagItemEquipBtn_Clicked(num) )

            self.ui.equipDel_Btn.clicked.disconnect()
            self.ui.equipDel_Btn.clicked.connect( lambda checked, num=idx:self.on_bagItemDelBtn_Clicked(num) )
        else:
            self.ui.itemTipsName_Text.setText( item_d["name"] )
            self.ui.itemDesc_Text.setText( item_d["desc"] % item_d["desc_arg"] )
            self.ui.itemUseLevel_Text.setText( data_tips.data["ITEM_USE_LEVEL"] % item_d["use_level"] )
            self.ui.itemUse_Btn.clicked.disconnect()
            self.ui.itemUse_Btn.clicked.connect( lambda checked, num=idx:self.on_bagItemUseBtn_Clicked(num) )

            self.ui.itemDel_Btn.clicked.disconnect()
            self.ui.itemDel_Btn.clicked.connect( lambda checked, num=idx:self.on_bagItemDelBtn_Clicked(num) )
    
    def on_bagItemEquipBtn_Clicked(self, idx):
        equipSucc, sysInfo = self.hero.try_equip_item(idx)
        self.addSystemInfo( sysInfo )
        if not equipSucc:
            return
        self.updateLevelInfo()
        self.updateBaseInfo()
        self.updateBagItem(True)
        self.updateEquip(None)
    
    def on_bagItemUseBtn_Clicked(self, idx):
        useSucc, sysInfo = self.hero.use_bagItems(idx)
        self.addSystemInfo( sysInfo )
        if not useSucc:
            return
        self.updateLevelInfo()
        self.updateBaseInfo()
        self.updateBagItem(True)
        self.updateEquip(None)
    
    def on_bagItemDelBtn_Clicked(self, idx):
        self.hero.del_bagItems(idx)
        self.updateBaseInfo()
        self.updateBagItem(True)
        self.updateEquip(None)

    # 物品Tips部分
    def _initItemTips(self):
        self.ui.itemTips_Group.setVisible(False)
    
    # 装备Tips部分
    def _initEquipTips(self):
        self.ui.equipTips_Group.setVisible(False)
        self.equipTipsProps = []
        idx = 0
        while True:
            ep = getattr(self.ui, "equipProp_Text%d" % idx, None)
            if ep is None:
                break
            self.equipTipsProps.append(ep)
            idx += 1

    # 基础属性部分
    def _initBaseInfo(self):
        self.ui.baseInfo_TextEdit.setReadOnly(True)

    def updateBaseInfo(self):
        baseInfo = self.hero.get_baseInfo()
        baseAddInfo = self.hero.get_baseAddInfo()
        val = [
            "生命：%d/%d" % ( baseInfo['HP'], baseInfo['MAXHP']),
            "内力：%d/%d" % ( baseInfo['MP'], baseInfo['MAXMP']),
            "攻击：%d" % (baseInfo['ATT']),
            "防御：%d" % (baseInfo['DEF']),
            "命中：%d" % (baseInfo['HIT']),
            "闪避：%d" % (baseInfo['DODGE']),
            "暴击：%d" % (baseInfo['CRIATT']),
            "暴防：%d" % (baseInfo['CRIDEF']),
        ]
        addval = [
            "(+%d)" % (baseAddInfo['MAXHP']), 
            "(+%d)" % (baseAddInfo['MAXMP']),
            "(+%d)" % (baseAddInfo['ATT']),
            "(+%d)" % (baseAddInfo['DEF']),
            "(+%d)" % (baseAddInfo['HIT']),
            "(+%d)" % (baseAddInfo['DODGE']),
            "(+%d)" % (baseAddInfo['CRIATT']),
            "(+%d)" % (baseAddInfo['CRIDEF']),
        ]
        self.ui.baseInfo_TextEdit.setText( '\n'.join( val ) )
        self.ui.baseAddInfo_TextEdit.setText( '\n'.join( addval ) )
    
    # 装备部分
    def updateEquip(self, visible=False):
        if visible != None:
            self.ui.equip_Group.setVisible(visible)
        epartList = getEquipPartList()
        for i, epart in enumerate(epartList):
            _, item = self.hero.get_equip_bypart( epart )
            if item:
                self.equipItemBtns[i].setText( data_item.data[ item['id'] ]["name"] )
            else:
                self.equipItemBtns[i].setText( getEquipPartName(epart) )

    def _initEquip(self):
        self.equipItemBtns = []
        idx = 0
        while True:
            btn = getattr(self.ui, "equipButton_%d"% idx, None)
            if btn is None:
                break
            btn.setEnabled(False)
            self.equipItemBtns.append(btn)
            idx += 1
        self.ui.equipChange_Btn.clicked.connect(self.on_equipChange_Btn_Clicked)

    def on_equipChange_Btn_Clicked(self):
        self.ui.equip_Group.setVisible( not self.ui.equip_Group.isVisible() )

    # 显示接口
    def show(self):
        self.ui.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    