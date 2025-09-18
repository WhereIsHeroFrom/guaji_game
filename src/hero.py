import random
from data import data_levelup
from data import data_levelproperty
from data import data_item
from data import data_scene
from data import data_tips
from common_func import *

class Hero(object):
    def __init__(self):
        self.level = 1
        self.exp = 0
        self.baseAddInfo = {}
        self.scene = 0
        self.sysInfo = []
        self.bagItems = []
        self.bagItemMaxCount = 25
        self.equips = {
            data_item.ItemSubType.EQUIP_WEAPON : False,
            data_item.ItemSubType.EQUIP_BRACER : False,
            data_item.ItemSubType.EQUIP_NECKLACE : False,
            data_item.ItemSubType.EQUIP_GAUNTLETS : False,
            data_item.ItemSubType.EQUIP_HELMET : False,
            data_item.ItemSubType.EQUIP_ARMOR  : False,
            data_item.ItemSubType.EQUIP_PAULDRONS : False,
            data_item.ItemSubType.EQUIP_BOOTS : False,
        }
        self.init()
    
    def init(self):
        self.baseAddInfo = {
            'HP' : 1, 'MP' : 1,
        }
        for k, v in data_levelproperty.data.items():
            self.baseAddInfo[k] = 0
        '''
            self.add_bagItems(100000, 1)
            self.add_bagItems(100001, 20)
            self.add_bagItems(301010, 1)
            self.add_bagItems(301011, 1)
        '''
    def set_level(self, l):
        self.level = l
    
    def get_level(self):
        return self.level

    def levelup(self):
        if data_levelup.data.get(self.level + 1, None) is None:
            print("level up failed, max level!")
            return 
        if self.exp < data_levelup.data.get(self.level + 1):
            print("level up failed, exp not enough!")
            return 
        self.level += 1
        self.exp -= data_levelup.data.get(self.level)
        # 升级以后血和蓝升满
        baseInfo = self.get_baseInfo()
        self.baseAddInfo['HP'] = baseInfo['MAXHP']
        self.baseAddInfo['MP'] = baseInfo['MAXMP']

    def add_exp(self, exp):
        self.exp += exp
    
    def get_exp(self):
        return self.exp
    
    def set_scene(self, s):
        self.scene = s
    
    def get_scene(self):
        return self.scene
    
    def add_sysInfo(self, text):
        self.sysInfo.append(text)
        if len(self.sysInfo) > 200:
            self.sysInfo.pop(0)

    def get_sysInfo(self):
        return self.sysInfo

    def get_bagItems(self):
        return self.bagItems
    
    def add_bagItems(self, itemId, itemCount=1):
        for item in self.bagItems:
            if itemId == item["id"]:
                if data_item.data[itemId]["max_count"] > 1:
                    item["cnt"] += itemCount
                    return True
        if len(self.bagItems) < self.bagItemMaxCount:
            self.bagItems.append( genItem(itemId, itemCount) )
            return True
        return 

    def unequip_item(self, index):
        item = self.bagItems[index]
        epart = data_item.data[ item["id"] ]["item_subtype"]
        item["equip"] = False
        self.equips[epart] = False
        for k, v in data_item.data[ item["id"] ][ "property_add" ].items():
            self.baseAddInfo[k] = self.baseAddInfo.get(k, 0) - v
    
    def equip_item(self, index):
        item = self.bagItems[index]
        epart = data_item.data[ item["id"] ]["item_subtype"]
        item["equip"] = True
        self.equips[epart] = True
        for k, v in data_item.data[ item["id"] ][ "property_add" ].items():
            self.baseAddInfo[k] = self.baseAddInfo.get(k, 0) + v
    
    def get_equip_bypart(self, epart):
        for i, bagitem in enumerate(self.bagItems):
            if not isEquip(bagitem["id"]):
                continue
            if not bagitem["equip"]:
                continue
            if data_item.data[ bagitem["id"] ]["item_subtype"] != epart:
                continue
            return i, bagitem
        return -1, None
    
    def try_equip_item(self, index):
        item = self.bagItems[index]
        epart = data_item.data[ item["id"] ][ "item_subtype" ]
        ename = data_item.data[ item["id"] ]["name"]
        elevel = data_item.data[ item["id"] ]["use_level"]
        if self.level < elevel:
            return False, (data_tips.data['EQUIP_FAILED_LEVEL'] % (ename, elevel))
        isThisEquip = item["equip"]
        if self.equips[epart]:
            equip_index, _ = self.get_equip_bypart(epart)
            self.unequip_item( equip_index )
        if not isThisEquip:
            self.equip_item( index )
        return True, data_tips.data["EQUIP_SUCC"] % (ename)
    
    def use_bagItems(self, index):
        item = self.bagItems[index]
        id = item["id"]
        item_d = data_item.data[id]
        if self.level < item_d["use_level"]:
            return False, (data_tips.data['USE_ITEM_LEVEL'] % item_d["use_level"])
        sysInfo = data_tips.data['USE_ITEM_SUCC'] % (item_d["name"], (item_d["desc"]%item_d["desc_arg"])  )
        if item_d["item_type"] == data_item.ItemType.ADD_EXP:
            self.add_exp( item_d["desc_arg"][0] )
            if item["cnt"] > 1:
                item["cnt"] -= 1
            else:
                self.del_bagItems(index)
        return True, sysInfo

    def del_bagItems(self, index):
        item = self.bagItems[index]
        if isEquip(item["id"]) and item["equip"]:
            self.unequip_item(index)
        self.bagItems.pop(index)

    def get_baseInfo(self):
        baseInfo = self.baseAddInfo.copy()
        for k, v in data_levelproperty.data.items():
            baseInfo[k] += int(self.level * v + 1.7)   # 1.7是一个修正值，避免玩家太容易猜出来
        return baseInfo

    def get_baseAddInfo(self):
        return self.baseAddInfo

    def drop_exp(self):
        exp = int( random.randint(1, 10) * data_scene.data.get( self.get_scene() )["exp_multiple"] )
        self.add_exp(exp)
        return exp

    def drop_item(self):
        sn = self.scene
        sn_d = data_scene.data[sn]
        drop_l = 0
        randval = random.randint(0, 100)
        for i, p in enumerate(sn_d["drop_items_prop"]):
            if drop_l <= randval and randval < p:
                itemId = sn_d["drop_items"][i]
                sysInfo = ""
                suc = self.add_bagItems(itemId)
                snName = data_scene.data[sn]["name"]
                itemName = data_item.data[itemId]["name"]
                if suc:
                    sysInfo = data_tips.data["DROP_ITEM"] % ( snName , itemName)
                else:
                    sysInfo = data_tips.data["DROP_ITEM_BAGFULL"] % ( snName , itemName)
                return itemId, suc, sysInfo
            drop_l = p
        return None, False, "" 
