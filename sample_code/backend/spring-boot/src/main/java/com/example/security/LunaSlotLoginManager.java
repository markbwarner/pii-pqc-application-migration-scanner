package com.example.security;

import com.safenetinc.luna.LunaSlotManager;

public class LunaSlotLoginManager {

    public LunaSlotManager loginToDefaultPartition(String password) throws Exception {
        LunaSlotManager slotManager = LunaSlotManager.getInstance();
        slotManager.login(password);
        return slotManager;
    }

    public String describeDefaultSlot(LunaSlotManager slotManager) throws Exception {
        int slot = slotManager.getDefaultSlot();
        return "slot=" + slot + ", label=" + slotManager.getTokenLabel(slot);
    }
}
