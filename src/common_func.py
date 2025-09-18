from data import data_item

def isEquip(itemId):
    tp = data_item.data[itemId]["item_type"]
    return tp == data_item.ItemType.EQUIP_ATT or tp == data_item.ItemType.EQUIP_DEF

def getEquipPartName(subType):
    return {
        data_item.ItemSubType.EQUIP_WEAPON : "武器",
        data_item.ItemSubType.EQUIP_BRACER : "护腕",
        data_item.ItemSubType.EQUIP_NECKLACE : "项链",
        data_item.ItemSubType.EQUIP_GAUNTLETS : "手套",
        data_item.ItemSubType.EQUIP_HELMET : "盔",
        data_item.ItemSubType.EQUIP_ARMOR  : "甲",
        data_item.ItemSubType.EQUIP_PAULDRONS : "肩",
        data_item.ItemSubType.EQUIP_BOOTS : "靴"
    }[subType]

def getEquipPartList():
    return (
        data_item.ItemSubType.EQUIP_WEAPON,
        data_item.ItemSubType.EQUIP_BRACER,
        data_item.ItemSubType.EQUIP_NECKLACE,
        data_item.ItemSubType.EQUIP_GAUNTLETS,
        data_item.ItemSubType.EQUIP_HELMET,
        data_item.ItemSubType.EQUIP_ARMOR,
        data_item.ItemSubType.EQUIP_PAULDRONS,
        data_item.ItemSubType.EQUIP_BOOTS
    )

def getPropertyName(propStr):
    return {
        'MAXHP' : "血量",
        'MAXMP' : "内力",
        'ATT' :"攻击",
        'DEF' : "防御",
        'HIT'    : "命中",
        'DODGE'  : "闪避",
        'CRIATT' :"暴击",
        'CRIDEF' : "暴防",
    }[propStr]



def genItem(itemId, itemCount=1):
    ret = {"id" : itemId, "cnt":itemCount}
    if isEquip(itemId):
        ret["equip"] = False
    return ret